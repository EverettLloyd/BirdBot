from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SeekerApplication(Base):
    __tablename__ = 'seeker_applications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    age = Column(String(50))
    city = Column(String(100))
    housing = Column(String(100))
    other_birds = Column(String(200))
    animals_kids = Column(String(200))
    experience = Column(Text)

    photos = relationship('Photo', back_populates='seeker')

class OwnerApplication(Base):
    __tablename__ = 'owner_applications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    species = Column(String(100))
    city = Column(String(100))
    age = Column(String(50))
    gender = Column(String(20))
    description = Column(Text)
    contact = Column(String(200))

    photos = relationship('Photo', back_populates='owner')

class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    file_id = Column(String(250), nullable=False)
    seeker_id = Column(Integer, ForeignKey('seeker_applications.id'))
    owner_id = Column(Integer, ForeignKey('owner_applications.id'))

    seeker = relationship('SeekerApplication', back_populates='photos')
    owner = relationship('OwnerApplication', back_populates='photos')
