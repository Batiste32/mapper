# Creates the engine and Session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.utils.constants import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def set_database_path(db_path: str):
    global engine, SessionLocal
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)