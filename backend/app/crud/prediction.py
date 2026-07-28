from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.models.traffic import Traffic
from app.services.predictor import generate_prediction


def create_prediction(db: Session, traffic_id: int):
    traffic = (
        db.query(Traffic)
        .filter(Traffic.id == traffic_id)
        .first()
    )

    if traffic is None:
        return None

    prediction_data = generate_prediction(traffic)

    prediction = Prediction(
        traffic_id=traffic.id,
        **prediction_data,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction


def get_prediction(db: Session, prediction_id: int):
    return (
        db.query(Prediction)
        .filter(Prediction.id == prediction_id)
        .first()
    )


def get_prediction_by_traffic(db: Session, traffic_id: int):
    return (
        db.query(Prediction)
        .filter(Prediction.traffic_id == traffic_id)
        .first()
    )