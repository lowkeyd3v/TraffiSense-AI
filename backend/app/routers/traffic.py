from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.jwt import get_current_user
from app.models.user import User
from app.crud.traffic import (
    create_traffic,
    delete_traffic,
    get_all_traffic,
    get_traffic,
    update_traffic,
)
from app.database import get_db
from app.schemas.traffic import (
    TrafficCreate,
    TrafficResponse,
    TrafficUpdate,
)

router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"],
)


@router.post("/", response_model=TrafficResponse)
def create(
    traffic: TrafficCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_traffic(
        db=db,
        traffic=traffic,
        user_id=current_user.id,
    )


@router.get("/", response_model=list[TrafficResponse])
def read_all(db: Session = Depends(get_db)):
    return get_all_traffic(db)


@router.get("/{traffic_id}", response_model=TrafficResponse)
def read_one(
    traffic_id: int,
    db: Session = Depends(get_db),
):
    traffic = get_traffic(db, traffic_id)

    if not traffic:
        raise HTTPException(
            status_code=404,
            detail="Traffic record not found",
        )

    return traffic


@router.put("/{traffic_id}", response_model=TrafficResponse)
def update(
    traffic_id: int,
    traffic: TrafficUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated = update_traffic(
        db,
        traffic_id,
        traffic,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Traffic record not found",
        )

    return updated


@router.delete("/{traffic_id}")
def delete(
    traffic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_traffic(
        db,
        traffic_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Traffic record not found",
        )

    return {
        "message": "Traffic record deleted successfully"
    }