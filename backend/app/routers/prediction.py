from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.prediction import (
    create_prediction,
    get_prediction_by_traffic,
)
from app.database import get_db
from app.schemas.prediction import PredictionResponse

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"],
)


@router.post(
    "/predict/{traffic_id}",
    response_model=PredictionResponse,
)
def predict(
    traffic_id: int,
    db: Session = Depends(get_db),
):
    existing = get_prediction_by_traffic(
        db,
        traffic_id,
    )

    if existing:
        return existing

    prediction = create_prediction(
        db,
        traffic_id,
    )

    if prediction is None:
        raise HTTPException(
            status_code=404,
            detail="Traffic record not found",
        )

    return prediction