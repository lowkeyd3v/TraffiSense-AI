from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.traffic import Traffic
from app.models.prediction import Prediction


def get_dashboard_overview(db: Session):
    total_vehicles = (
        db.query(func.sum(Traffic.vehicle_count))
        .scalar()
        or 0
    )

    active_incidents = (
        db.query(Prediction)
        .filter(Prediction.incident_type.isnot(None))
        .count()
    )

    high_risk_roads = (
        db.query(Prediction)
        .filter(Prediction.risk_score >= 0.7)
        .count()
    )

    avg = (
        db.query(func.avg(Prediction.risk_score))
        .scalar()
        or 0
    )

    if avg >= 0.7:
        congestion = "High"
    elif avg >= 0.4:
        congestion = "Medium"
    else:
        congestion = "Low"

    return {
        "total_vehicles": total_vehicles,
        "active_incidents": active_incidents,
        "high_risk_roads": high_risk_roads,
        "average_congestion": congestion,
    }


def get_prediction_history(db: Session):
    predictions = (
        db.query(Prediction)
        .order_by(Prediction.prediction_time.desc())
        .all()
    )

    return predictions


def get_traffic_history(db: Session):
    traffic = (
        db.query(Traffic)
        .order_by(Traffic.timestamp.desc())
        .all()
    )

    return traffic