from pydantic import BaseModel
from typing import List, Optional


class GeometrySchema(BaseModel):
    type: str = "Point"
    coordinates: List[float]


class LocationResponseSchema(BaseModel):
    id: int
    geometry: GeometrySchema
    address: str
    provider: str


class LocationRequestSchema(BaseModel):
    geometry: GeometrySchema
    address: str
    provider: str


class GeometryUpdate(BaseModel):
    type: Optional[str] = None
    coordinates: Optional[List[float]] = None


class LocationUpdate(BaseModel):
    address: Optional[str] = None
    provider: Optional[str] = None
    geometry: Optional[GeometryUpdate] = None
