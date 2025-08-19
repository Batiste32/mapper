from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import backend.database as db_module
from backend.database.models import ConnectionLog
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = db_module.SessionLocal()
    print(str(db_module.SessionLocal.kw['bind'].url))
    try:
        yield db
    finally:
        db.close()

@router.get("/logs")
def get_logs(db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    logs = db.query(ConnectionLog).all()
    return logs
