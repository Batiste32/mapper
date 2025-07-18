import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.models import User
from backend.database import SessionLocal

SECRET_KEY = "YOUR_SECRET_KEY"
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImM1MWU3MzZiNjkyYTRhZWJhOWU4NTc3YzNmYmVjMWVlIiwiaCI6Im11cm11cjY0In0="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_admin():
    username = input("Admin username: ").strip()
    password = input("Admin password: ").strip()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    db = SessionLocal()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print("User already exists.")
        return

    admin = User(username=username, password_hash=password_hash, is_admin=True)
    db.add(admin)
    db.commit()
    db.close()

def remove_admin():
    username = input("Admin username: ").strip()
    password = input("Admin password: ").strip()

    db = SessionLocal()

    existing = db.query(User).filter(User.username == username, User.is_admin == True).first()

    if existing:
        if bcrypt.checkpw(password.encode('utf-8'), existing.password_hash):
            db.delete(existing)
            db.commit()
            print(f"Admin user '{username}' deleted.")
        else:
            print("Wrong credentials.")
    else:
        print("Admin user not found.")

    db.close()

def list_admins():
    db = SessionLocal()

    admins = db.query(User).filter(User.is_admin == True).all()

    if not admins:
        print("No admins found.")
    else:
        print("Registered admins:")
        for admin in admins:
            print(f"- {admin.username}")

    db.close()