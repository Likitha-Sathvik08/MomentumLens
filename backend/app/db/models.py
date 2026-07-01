from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, unique=True, index=True)
    home_team = Column(String)
    away_team = Column(String)
    date = Column(String, nullable=True)
    competition = Column(String, nullable=True)
    status = Column(String, default="loaded")  # loaded | analyzed | explained
    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship("Event", back_populates="match", cascade="all, delete-orphan")
    features = relationship("Feature", back_populates="match", cascade="all, delete-orphan")
    turning_points = relationship("TurningPoint", back_populates="match", cascade="all, delete-orphan")
    explanations = relationship("Explanation", back_populates="match", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    minute = Column(Integer)
    second = Column(Integer, nullable=True)
    event_type = Column(String)
    team = Column(String, nullable=True)
    player = Column(String, nullable=True)
    outcome = Column(String, nullable=True)
    extra = Column(JSON, nullable=True)

    match = relationship("Match", back_populates="events")


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    minute = Column(Integer)
    momentum_score = Column(Float)
    possession_home = Column(Float, nullable=True)
    shots_home = Column(Integer, nullable=True)
    shots_away = Column(Integer, nullable=True)
    pressure_index = Column(Float, nullable=True)
    extra = Column(JSON, nullable=True)

    match = relationship("Match", back_populates="features")


class TurningPoint(Base):
    __tablename__ = "turning_points"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    minute = Column(Integer)
    momentum_delta = Column(Float)
    direction = Column(String)
    confidence = Column(Float)
    causes = Column(JSON, nullable=True)

    match = relationship("Match", back_populates="turning_points")


class Explanation(Base):
    __tablename__ = "explanations"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    turning_point_id = Column(Integer, ForeignKey("turning_points.id"))
    explanation_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="explanations")
