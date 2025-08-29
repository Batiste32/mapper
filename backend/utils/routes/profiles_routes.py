from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from fastapi.responses import StreamingResponse
import csv
import io

import backend.database as db_module
from backend.database.models import Profile, FieldMetadata

router = APIRouter(prefix="/profiles", tags=["profiles"])

def get_db():
    db = db_module.SessionLocal() # Persistent link
    print(str(db_module.SessionLocal.kw['bind'].url))
    try:
        yield db
    finally:
        db.close()

def get_filtered_profiles(
    db: Session,
    score_min: int | None = None,
    score_max: int | None = None,
    origin: str | None = None,
    nbhood: str = "Loyola"
):
    query = db.query(Profile).filter(Profile.nbhood == nbhood)

    if score_min is not None:
        query = query.filter(Profile.score_vote >= score_min)
    if score_max is not None:
        query = query.filter(Profile.score_vote <= score_max)
    if origin:
        query = query.filter(Profile.origin.ilike(f"%{origin}%"))

    return query

@router.get("/fields")
def list_profile_fields():
    """
    Returns all available Profile fields and their SQLAlchemy types.
    Useful for building dynamic filters on the frontend.
    """
    mapper = inspect(Profile)
    fields = {}
    for column in mapper.columns:
        fields[column.name] = str(column.type)
    return fields

@router.get("/all")
def list_all_profiles(db: Session = Depends(get_db)):
    profiles = db.query(Profile).all()
    return profiles

@router.get("/")
def list_profiles(
    db: Session = Depends(get_db),
    limit: int = Query(20),
    offset: int = Query(0),
    **filters
):
    query = db.query(Profile)

    # Apply filters dynamically
    for field, value in filters.items():
        if not hasattr(Profile, field) or value is None:
            continue
        column = getattr(Profile, field)

        # Support numeric ranges (min/max)
        if field.endswith("_min"):
            base_field = field[:-4]
            if hasattr(Profile, base_field):
                query = query.filter(getattr(Profile, base_field) >= value)
        elif field.endswith("_max"):
            base_field = field[:-4]
            if hasattr(Profile, base_field):
                query = query.filter(getattr(Profile, base_field) <= value)
        else:
            # Fuzzy match for strings
            if isinstance(value, str):
                query = query.filter(column.ilike(f"%{value}%"))
            else:
                query = query.filter(column == value)

    return query.offset(offset).limit(limit).all()

@router.get("/export")
def export_profiles(
    score_min: int = Query(None),
    score_max: int = Query(None),
    origin: str = Query(None),
    nbhood: str = Query("Loyola"),
    db: Session = Depends(get_db)
):
    query = get_filtered_profiles(db, score_min, score_max, origin, nbhood)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id", "name", "nbhood", "score_vote",
        "preferred_language", "native_language",
        "origin", "political_lean", "personality",
        "political_scale", "ideal_process",
        "strategic_profile", "suggested_arguments"
    ])

    for profile in query.all():
        writer.writerow([
            profile.id, profile.name, profile.nbhood, profile.score_vote,
            profile.preferred_language, profile.native_language,
            profile.origin, profile.political_lean, profile.personality,
            profile.political_scale, profile.ideal_process,
            profile.strategic_profile, profile.suggested_arguments
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=profiles.csv"}
    )

@router.get("/valid_values")
def get_valid_values(field: str, db: Session = Depends(get_db)):
    if not hasattr(Profile, field):
        raise HTTPException(status_code=400, detail=f"Invalid field: {field}")
    values = db.query(getattr(Profile, field)).distinct().all()
    return list({v[0] for v in values if v[0]})

@router.get("/field_metadata/{field_name}")
def get_field_metadata(field_name: str, db: Session = Depends(get_db)):
    meta = db.query(FieldMetadata).filter(FieldMetadata.field_name == field_name).first()
    if not meta:
        return {"field_name": field_name, "label": None, "description": None}
    return {"field_name": meta.field_name, "label": meta.label, "description": meta.descript}