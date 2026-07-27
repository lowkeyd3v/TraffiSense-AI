from sqlalchemy.orm import Session

from app.models.traffic import Traffic
from app.schemas.traffic import TrafficCreate, TrafficUpdate

def create_traffic(db: Session, traffic: TrafficCreate, user_id: int | None = None):
    db_traffic = Traffic(
        **traffic.model_dump(),
        created_by=user_id
    )

    db.add(db_traffic)
    db.commit()
    db.refresh(db_traffic)

    return db_traffic


def get_all_traffic(db: Session):
    return db.query(Traffic).all()


def get_traffic(db: Session, traffic_id: int):
    return (
        db.query(Traffic)
        .filter(Traffic.id == traffic_id)
        .first()
    )


def update_traffic(
    db: Session,
    traffic_id: int,
    traffic: TrafficUpdate
):
    db_traffic = get_traffic(db, traffic_id)

    if not db_traffic:
        return None

    for key, value in traffic.model_dump(exclude_unset=True).items():
        setattr(db_traffic, key, value)

    db.commit()
    db.refresh(db_traffic)

    return db_traffic


def delete_traffic(db: Session, traffic_id: int):
    db_traffic = get_traffic(db, traffic_id)

    if not db_traffic:
        return None

    db.delete(db_traffic)
    db.commit()

    return db_traffic