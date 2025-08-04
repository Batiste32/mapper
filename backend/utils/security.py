import bcrypt
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

from backend.database.models import User
from backend.database import SessionLocal
from backend.utils.constants import *

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def create_access_token(data: dict):
    load_dotenv()

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    load_dotenv()

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
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