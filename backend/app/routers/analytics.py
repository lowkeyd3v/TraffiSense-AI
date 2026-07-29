from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt import get_current_user
from app.crud.analytics import (
    get_dashboard_overview,
    get_prediction_history,
    get_traffic_history,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_dashboard_overview(db)


@router.get("/traffic-history")
def traffic_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_traffic_history(db)


@router.get("/prediction-history")
def prediction_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_prediction_history(db)