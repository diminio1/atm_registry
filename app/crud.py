from sqlalchemy.orm import Session
from . import models, schemas


def get_locations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Location).offset(skip).limit(limit).all()


def create_location(db: Session, location: schemas.LocationRequestSchema):
    db_geometry = models.Geometry(
        type=location.geometry.type,
        latitude=location.geometry.coordinates[0],
        longitude=location.geometry.coordinates[1])
    db.add(db_geometry)
    db.flush()  # Flush to get the geometry_id

    db_location = models.Location(
        address=location.address,
        provider=location.provider,
        geometry_id=db_geometry.id)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location, db_geometry


def update_location(db: Session, location_id: int, location_data: schemas.LocationUpdate):
    db_location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if db_location is None:
        return None

    if location_data.address:
        db_location.address = location_data.address
    if location_data.provider:
        db_location.provider = location_data.provider

    if location_data.geometry:
        db_geometry = db.query(models.Geometry).filter(models.Geometry.id == db_location.geometry_id).first()
        if db_geometry:
            if location_data.geometry.type:
                db_geometry.type = location_data.geometry.type
            if location_data.geometry.coordinates:
                db_geometry.latitude = location_data.geometry.coordinates[0]
                db_geometry.longitude = location_data.geometry.coordinates[1]

    db.commit()
    db.refresh(db_location)
    return db_location
