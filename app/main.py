from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .models import SessionLocal
from .models import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/locations/", response_model=List[schemas.LocationResponseSchema])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    locations = crud.get_locations(db, skip=skip, limit=limit)
    return [
        {"id": loc.id, "geometry": {"type": "Point", "coordinates": [loc.geometry.latitude, loc.geometry.longitude]},
         "address": loc.address, "provider": loc.provider} for loc in locations]


@app.post("/locations/", response_model=schemas.LocationResponseSchema)
def create_location(location: schemas.LocationRequestSchema, db: Session = Depends(get_db)):
    db_location, db_geometry = crud.create_location(db=db, location=location)
    return schemas.LocationResponseSchema(
        id=db_location.id,
        geometry={"type": "Point", "coordinates": [db_geometry.latitude, db_geometry.longitude]},
        address=db_location.address,
        provider=db_location.provider)


@app.put("/locations/{location_id}", response_model=schemas.LocationResponseSchema)
def update_location(location_id: int, location_data: schemas.LocationUpdate, db: Session = Depends(get_db)):
    loc = crud.update_location(db, location_id, location_data)
    if loc is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"id": loc.id, "geometry": {"type": "Point", "coordinates": [loc.geometry.latitude, loc.geometry.longitude]},
            "address": loc.address, "provider": loc.provider}
