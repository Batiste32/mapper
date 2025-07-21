from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float, Index
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.engine.base import Engine
from datetime import datetime
import csv
import bcrypt
import re # regex to cleanup data

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    devices = relationship("Device", back_populates="user")
    visits = relationship("Visit", back_populates="user")
    logs = relationship("ConnectionLog", back_populates="user")

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="devices")
    logs = relationship("ConnectionLog", back_populates="device")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    uniqueid = Column(String, unique=True, nullable=False)
    name = Column(String)
    age = Column(Integer)
    nbhood = Column(String, nullable=False, default="Loyola")
    score_vote = Column(Integer)  # 1 to 10
    preferred_language = Column(String)
    native_language = Column(String)
    origin = Column(String)
    political_lean = Column(String)
    personality = Column(String)
    political_scale = Column(Text)
    ideal_process = Column(String)
    strategic_profile = Column(String)
    suggested_arguments = Column(Text)
    picture_url = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    distance = Column(Float)  # distance from start
    __table_args__ = (Index("ix_nbhood_score", "nbhood", "score_vote"),) # Allows filtering on neighborhood and score 

    visits = relationship("Visit", back_populates="profile")

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    visited_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="visits")
    user = relationship("User", back_populates="visits")

class ConnectionLog(Base):
    __tablename__ = "connection_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String)
    device_id = Column(Integer, ForeignKey("devices.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")
    device = relationship("Device", back_populates="logs")


def create_data_base(file_path:str = "backend/database/electoral_app.db"):
    "Generate a db file for SQLite."
    engine = create_engine("sqlite:///"+file_path, echo=True)
    Base.metadata.create_all(engine)
    print("Created database")
    return(engine)

def import_data_from_csv(engine: Engine, filepath: str = "backend/database/profiles.csv"):
    """
    Read a csv file to update the database.
    Requires the engine used to create the database and optionally the filepath.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            profile = Profile(
                uniqueid=row['UNIQUEID'],
                name=f"{row['FIRSTNAME']} {row['NAME']}",
                age=int(row['AGE']),
                nbhood=row['CIRCONSCRIPT'],  # Mapped as neighborhood
                score_vote=int(row['VOTE_PROBABILITY']) if row['VOTE_PROBABILITY'] else None,
                preferred_language=row['PREFERRED_LANGUAGE'],
                native_language=row['LANGUAGE'],
                origin=row['ORIGIN'],
                political_lean=row['POLITICAL_LEANING'],
                personality=isolate_stressed_element_in_field(row['PERSONNALITY']),
                political_scale=row['POLITICAL_PROFILE'],
                ideal_process=row['INTERACTION_SEQUENCE'],
                strategic_profile=row['STRATEGIC_PROFILE'],
                suggested_arguments=row['SUGGESTED_ARGUMENTS'],
                picture_url="",
                distance=None
            )
            session.add(profile)

    session.commit()
    print("Imported profiles!")

def add_admin(engine:Engine, username:str, password:str):
    "Add an admin profile to the database. Requires the engine used to create the database and the credentials."
    Session = sessionmaker(bind=engine)
    session = Session()

    username = "admin"
    password = "SuperSecret123"

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    admin_user = User(username=username, password_hash=password_hash, is_admin=True)
    session.add(admin_user)
    session.commit()

    print(f"Admin user '{username}' created.")

def isolate_stressed_element_in_field(field: str):
    """
    Uses regex to extract first text inside ** ** or the whole field if not found.
    Cleans up the text fields generated by LLMs. 
    """
    regex_pattern = r'\*\*(.*?)\*\*'
    search = re.search(regex_pattern, field)
    if search:
        return search.group(1)
    else: 
        return field