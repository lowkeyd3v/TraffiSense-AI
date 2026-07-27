from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrafficBase(BaseModel):
    location: str
    vehicle_count: int
    average_speed: float
    congestion_level: str
    weather_condition: str
    road_status: str
    road_type: str


class TrafficCreate(TrafficBase):
    pass

class TrafficUpdate(BaseModel):
    location: str | None = None
    vehicle_count: int | None = None
    average_speed: float | None = None
    congestion_level: str | None = None
    weather_condition: str | None = None
    road_status: str | None = None
    road_type: str | None = None
    
class TrafficResponse(TrafficBase):
    id: int
    created_by: int | None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)