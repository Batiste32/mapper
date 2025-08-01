from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import csv
import io

from backend.database import SessionLocal
from backend.database.models import Profile
from backend.utils.dependencies import get_current_user
from backend.utils.geo import haversine, geocode_address

router = APIRouter(prefix="/profiles", tags=["profiles"])

def get_db():
    db = SessionLocal()
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

@router.get("/all")
def list_all_profiles(db: Session = Depends(get_db), user = Depends(get_current_user)):
    profiles = db.query(Profile).all()
    return profiles


@router.get("/")
def list_profiles(
    score_min: int = Query(None),
    score_max: int = Query(None),
    origin: str = Query(None),
    nbhood: str = Query("Loyola"),  
    limit: int = Query(20),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = get_filtered_profiles(db, score_min, score_max, origin, nbhood)

    profiles = query.offset(offset).limit(limit).all()
    return profiles

@router.get("/export")
def export_profiles(
    score_min: int = Query(None),
    score_max: int = Query(None),
    origin: str = Query(None),
    nbhood: str = Query("Loyola"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
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