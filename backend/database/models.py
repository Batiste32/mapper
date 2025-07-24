from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.utils.constants import *
from backend.database.schema import Base

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
