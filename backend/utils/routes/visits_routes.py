from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import backend.database as db_module
from backend.database.models import Visit, Profile
from backend.utils.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/visits", tags=["visits"])

def get_db():
    db = db_module.SessionLocal()
    print(str(db_module.SessionLocal.kw['bind'].url))
    try:
        yield db
    finally:
        db.close()

@router.post("/{profile_id}/visit")
def mark_as_visited(profile_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    visit = Visit(profile_id=profile_id, user_id=user.id, visited_at=datetime.utcnow())
    db.add(visit)
    db.commit()
    return {"status": "Profile marked as visited"}
