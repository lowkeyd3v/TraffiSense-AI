"""
Deployment log storage.

Uses Postgres when a DATABASE_URL env var is present (e.g. on Render, where
this points at a managed Postgres instance and data survives restarts/deploys).
Falls back to a local db.sqlite3 file when DATABASE_URL is unset, so local
dev still works with zero setup.

Public function signatures (init_db, add_deployment, get_deployments,
resolve_deployment) are unchanged from the original sqlite3-only version,
so main.py does not need to change.
"""

import os
from typing import List, Dict, Any, Optional

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, Float, String,
    Boolean, DateTime, select, insert, update, func,
)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    # Render's DATABASE_URL uses the "postgres://" scheme; SQLAlchemy 2.x /
    # psycopg2 want "postgresql://".
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # Local dev fallback — NOT suitable for Render's ephemeral filesystem.
    engine = create_engine("sqlite:///db.sqlite3", connect_args={"check_same_thread": False})

metadata = MetaData()

deployments = Table(
    "deployments", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("event_cause", String),
    Column("veh_type", String),
    Column("corridor", String),
    Column("priority", String),
    Column("time", String),
    Column("requires_road_closure", Boolean),
    Column("event_type", String),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("police_station", String),
    Column("description", String),
    Column("event_scale", String),
    Column("crowd_size", Integer),
    Column("predicted_duration", Float),
    Column("personnel", Integer),
    Column("barricades", Integer),
    Column("congestion_radius_meters", Float),
    Column("commuter_delay_minutes", Float),
    Column("status", String, default="active"),
    Column("actual_duration", Float),
    Column("actual_personnel", Integer),
    Column("actual_barricades", Integer),
    Column("actual_congestion_radius", Float),
    Column("actual_delay", Float),
    Column("feedback_comments", String),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


def init_db():
    """Creates the deployments table if it doesn't exist."""
    metadata.create_all(engine)


def add_deployment(data: Dict[str, Any], predictions: Dict[str, Any]) -> int:
    """Inserts a new deployment log entry into the database."""
    with engine.begin() as conn:
        result = conn.execute(
            insert(deployments).values(
                event_cause=data.get("event_cause"),
                veh_type=data.get("veh_type"),
                corridor=data.get("corridor"),
                priority=data.get("priority"),
                time=data.get("time"),
                requires_road_closure=bool(data.get("requires_road_closure")),
                event_type=data.get("event_type"),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                police_station=data.get("police_station"),
                description=data.get("description"),
                event_scale=data.get("event_scale", "Medium"),
                crowd_size=data.get("crowd_size", 0),
                predicted_duration=predictions.get("predicted_duration"),
                personnel=predictions.get("personnel"),
                barricades=predictions.get("barricades"),
                congestion_radius_meters=predictions.get("congestion_radius_meters"),
                commuter_delay_minutes=predictions.get("commuter_delay_minutes"),
                status="active",
            )
        )
        new_id = result.inserted_primary_key[0]
    return new_id


def get_deployments(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves deployments from the database, optionally filtered by status."""
    with engine.connect() as conn:
        stmt = select(deployments).order_by(deployments.c.created_at.desc())
        if status:
            stmt = stmt.where(deployments.c.status == status)
        rows = conn.execute(stmt).mappings().all()
    return [dict(r) for r in rows]


def resolve_deployment(deployment_id: int, feedback: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an active deployment with actual metrics and sets status to resolved."""
    with engine.begin() as conn:
        existing = conn.execute(
            select(deployments).where(deployments.c.id == deployment_id)
        ).mappings().first()
        if not existing:
            return None

        conn.execute(
            update(deployments)
            .where(deployments.c.id == deployment_id)
            .values(
                status="resolved",
                actual_duration=feedback.get("actual_duration"),
                actual_personnel=feedback.get("actual_personnel"),
                actual_barricades=feedback.get("actual_barricades"),
                actual_congestion_radius=feedback.get("actual_congestion_radius"),
                actual_delay=feedback.get("actual_delay"),
                feedback_comments=feedback.get("feedback_comments"),
            )
        )

        updated = conn.execute(
            select(deployments).where(deployments.c.id == deployment_id)
        ).mappings().first()

    return dict(updated) if updated else None
