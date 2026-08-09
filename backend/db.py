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

from datetime import datetime, timezone

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

    # Frequently queried fields
    Column("event_cause", String, index=True),
    Column("veh_type", String, index=True),
    Column("corridor", String),
    Column("priority", String, index=True),
    Column("time", String, index=True),
    Column("requires_road_closure", Boolean),
    Column("event_type", String),

    # Location
    Column("latitude", Float, index=True),
    Column("longitude", Float, index=True),
    Column("police_station", String, index=True),

    Column("description", String),
    Column("event_scale", String, index=True),
    Column("crowd_size", Integer),

    # Predictions
    Column("predicted_duration", Float),
    Column("personnel", Integer),
    Column("barricades", Integer),
    Column("congestion_radius_meters", Float),
    Column("commuter_delay_minutes", Float),

    # Status
    Column("status", String, default="active", index=True),

    # Feedback
    Column("actual_duration", Float),
    Column("actual_personnel", Integer),
    Column("actual_barricades", Integer),
    Column("actual_congestion_radius", Float),
    Column("actual_delay", Float),
    Column("feedback_comments", String),

    # Timestamp
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    ),
)

# ── Retraining job tracking (issue #41) ──────────────────────────────────────
# Every retrain attempt (triggered by resolving a deployment) gets a row here,
# so training runs asynchronously in the background instead of blocking the
# /resolve request, and its outcome is durable and queryable rather than
# living only in server logs.
retrain_jobs = Table(
    "retrain_jobs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("deployment_id", Integer, index=True),
    # queued -> running -> (promoted | rejected | failed | skipped)
    Column("status", String, default="queued", index=True),
    Column("message", String, default=""),

    # Evaluation metrics used to decide whether to promote the candidate
    # model over the currently deployed one (Fixes: unvalidated promotion).
    Column("baseline_mae", Float),
    Column("baseline_r2", Float),
    Column("candidate_mae", Float),
    Column("candidate_r2", Float),
    Column("promoted", Boolean, default=False),

    Column("requested_at", DateTime(timezone=True), server_default=func.now()),
    Column("started_at", DateTime(timezone=True)),
    Column("finished_at", DateTime(timezone=True)),
)

# ── Single-row mutex so only one retraining job runs at a time ──────────────
# A plain in-process threading.Lock isn't enough because the API can run as
# multiple worker processes; the lock needs to live somewhere shared, so it
# lives in the database and is claimed with an atomic UPDATE ... WHERE.
training_lock = Table(
    "training_lock", metadata,
    Column("id", Integer, primary_key=True),
    Column("locked", Boolean, default=False),
    Column("locked_at", DateTime(timezone=True)),
    Column("job_id", Integer),
)


def init_db():
    """Creates tables if they don't exist and seeds the training_lock row."""
    metadata.create_all(engine)
    with engine.begin() as conn:
        existing = conn.execute(
            select(training_lock).where(training_lock.c.id == 1)
        ).first()
        if not existing:
            conn.execute(insert(training_lock).values(id=1, locked=False))


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


def get_deployment(deployment_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single deployment by id, or None if it doesn't exist."""
    with engine.connect() as conn:
        row = conn.execute(
            select(deployments).where(deployments.c.id == deployment_id)
        ).mappings().first()
    return dict(row) if row else None


def get_resolved_feedback() -> List[Dict[str, Any]]:
    """
    Returns every resolved deployment with feedback, to be used as additional
    training data. This replaces the old flow of appending each feedback row
    to dataset.csv on disk — the database is now the single source of truth
    for feedback, so nothing is lost on redeploys with ephemeral storage.
    """
    with engine.connect() as conn:
        rows = conn.execute(
            select(deployments)
            .where(deployments.c.status == "resolved")
            .where(deployments.c.actual_duration.is_not(None))
        ).mappings().all()
    return [dict(r) for r in rows]


# ── Retrain job helpers ──────────────────────────────────────────────────────

def create_retrain_job(deployment_id: int) -> int:
    """Creates a new queued retrain job row and returns its id."""
    with engine.begin() as conn:
        result = conn.execute(
            insert(retrain_jobs).values(
                deployment_id=deployment_id,
                status="queued",
            )
        )
        return result.inserted_primary_key[0]


def update_retrain_job(job_id: int, **fields: Any) -> None:
    """Patches a retrain job row (status, metrics, timestamps, message...)."""
    if not fields:
        return
    with engine.begin() as conn:
        conn.execute(
            update(retrain_jobs).where(retrain_jobs.c.id == job_id).values(**fields)
        )


def get_retrain_job(job_id: int) -> Optional[Dict[str, Any]]:
    with engine.connect() as conn:
        row = conn.execute(
            select(retrain_jobs).where(retrain_jobs.c.id == job_id)
        ).mappings().first()
    return dict(row) if row else None


def list_retrain_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(
            select(retrain_jobs).order_by(retrain_jobs.c.id.desc()).limit(limit)
        ).mappings().all()
    return [dict(r) for r in rows]


def try_acquire_training_lock(job_id: int) -> bool:
    """
    Atomically claims the single training slot. Returns True if this caller
    now owns the lock, False if another retraining job is already running
    (this is what prevents concurrent retrains from racing on the model
    file / dataset, across one or many worker processes).
    """
    with engine.begin() as conn:
        result = conn.execute(
            update(training_lock)
            .where(training_lock.c.id == 1)
            .where(training_lock.c.locked.is_(False))
            .values(locked=True, locked_at=datetime.now(timezone.utc), job_id=job_id)
        )
        return result.rowcount > 0


def release_training_lock() -> None:
    with engine.begin() as conn:
        conn.execute(
            update(training_lock)
            .where(training_lock.c.id == 1)
            .values(locked=False, job_id=None)
        )
