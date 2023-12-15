from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Geometry(Base):
    __tablename__ = "geometries"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String, default="Point")
    latitude = Column(Float)
    longitude = Column(Float)
    # Relationship to Location
    location = relationship("Location", back_populates="geometry", uselist=False)


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address = Column(String)
    provider = Column(String)
    geometry_id = Column(Integer, ForeignKey('geometries.id'))
    # Relationship to Geometry
    geometry = relationship("Geometry", back_populates="location")
