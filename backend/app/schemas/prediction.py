from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PredictionBase(BaseModel):
    predicted_congestion: str
    risk_score: float
    recommended_action: str
    incident_type: str | None = None


class PredictionCreate(PredictionBase):
    traffic_id: int


class PredictionResponse(PredictionBase):
    id: int
    traffic_id: int
    prediction_time: datetime

    model_config = ConfigDict(from_attributes=True)