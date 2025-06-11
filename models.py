from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Seeker(Base):
    __tablename__ = 'seekers'

    id = Column(Integer, primary_key=True)
    age = Column(String)
    city = Column(String)
    housing = Column(String)
    other_birds = Column(Text)
    animals_kids = Column(Text)
    experience = Column(Text)
    photo_ids = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Owner(Base):
    __tablename__ = 'owners'

    id = Column(Integer, primary_key=True)
    species = Column(String)
    city = Column(String)
    age = Column(String)
    gender = Column(String)
    description = Column(Text)
    photo_ids = Column(Text)
    contact = Column(String)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
