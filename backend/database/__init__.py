# Creates the engine and Session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SessionLocal = None  # Needed to expose at module level
engine = None

def set_database_path(db_path: str):
    global engine, SessionLocal
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"Switched database to {db_path}.")