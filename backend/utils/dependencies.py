from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.database.models import User, Device
from backend.utils.security import SECRET_KEY, ALGORITHM

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    authorization: str = Header(...),
    device_token: str = Header(...),
    db: Session = Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token decode failed")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    device = db.query(Device).filter(Device.user_id == user.id, Device.device_token == device_token).first()
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device token")

    return user
