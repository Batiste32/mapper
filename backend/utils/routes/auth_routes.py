from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.models import User, Device
from backend.utils.security import verify_password, create_access_token, create_refresh_token
import backend.database as db_module

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

def get_db():
    db = db_module.SessionLocal()
    print(str(db_module.SessionLocal.kw['bind'].url))
    try:
        yield db
    finally:
        db.close()
"""
@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    import uuid
    device_token = str(uuid.uuid4())

    device = Device(user_id=user.id, device_token=device_token)
    db.add(device)
    db.commit()

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "device_token": device_token
    }
"""