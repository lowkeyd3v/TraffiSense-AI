"""
Tests for issue #41: background retraining with validation, DB-backed
feedback, concurrency locking, and endpoint protection.
"""
import os
import sys
import importlib

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

VALID_FORM = {
    "event_cause": "vehicle_breakdown",
    "veh_type": "heavy_vehicle",
    "corridor": "National Highway 44",
    "priority": "High",
    "time": "2026-01-01T12:00:00",
    "requires_road_closure": False,
    "event_type": "unplanned",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "police_station": "Central Traffic Control",
    "description": "Test incident",
}

FEEDBACK = {
    "actual_duration": 45.0,
    "actual_personnel": 5,
    "actual_barricades": 2,
    "actual_congestion_radius": 300.0,
    "actual_delay": 12.0,
    "feedback_comments": "test",
}


@pytest.fixture()
def app_client(tmp_path, monkeypatch):
    """Fresh app + isolated sqlite DB per test, with retraining stubbed out
    so tests don't spend real time training a GradientBoostingRegressor."""
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SQLITE_TEST_PATH", str(db_path))

    import db as db_module
    importlib.reload(db_module)
    # Point sqlite at a per-test file instead of the shared db.sqlite3.
    from sqlalchemy import create_engine
    db_module.engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    db_module.init_db()

    import main as main_module
    importlib.reload(main_module)
    main_module.init_db = db_module.init_db
    main_module.add_deployment = db_module.add_deployment
    main_module.get_deployments = db_module.get_deployments
    main_module.resolve_deployment = db_module.resolve_deployment
    main_module.get_deployment = db_module.get_deployment
    main_module.get_resolved_feedback = db_module.get_resolved_feedback
    main_module.create_retrain_job = db_module.create_retrain_job
    main_module.update_retrain_job = db_module.update_retrain_job
    main_module.get_retrain_job = db_module.get_retrain_job
    main_module.list_retrain_jobs = db_module.list_retrain_jobs
    main_module.try_acquire_training_lock = db_module.try_acquire_training_lock
    main_module.release_training_lock = db_module.release_training_lock

    # Stub out the actual model training so tests are fast and deterministic.
    def fake_job(job_id, deployment_id):
        import datetime as _dt
        main_module.update_retrain_job(
            job_id, status="promoted", message="stubbed for test",
            promoted=True, finished_at=_dt.datetime.now(_dt.timezone.utc),
        )
    monkeypatch.setattr(main_module, "_run_retraining_job", fake_job)

    client = TestClient(main_module.app)
    yield client, main_module


def _create_deployment(client):
    pred = {
        "predicted_duration_minutes": 30.0, "personnel_needed": 4,
        "barricades_needed": 2, "congestion_radius_meters": 100.0,
        "commuter_delay_minutes": 5.0,
    }
    resp = client.post("/api/deployments", json={"form": VALID_FORM, "predictions": pred})
    assert resp.status_code == 200
    return resp.json()["id"]


def test_resolve_triggers_background_job_and_returns_immediately(app_client):
    client, _ = app_client
    dep_id = _create_deployment(client)
    resp = client.post(f"/api/deployments/{dep_id}/resolve", json=FEEDBACK)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert "retrain_job_id" in body


def test_resolving_twice_is_rejected(app_client):
    client, _ = app_client
    dep_id = _create_deployment(client)
    r1 = client.post(f"/api/deployments/{dep_id}/resolve", json=FEEDBACK)
    assert r1.status_code == 200
    r2 = client.post(f"/api/deployments/{dep_id}/resolve", json=FEEDBACK)
    assert r2.status_code == 409


def test_resolving_unknown_deployment_errors(app_client):
    client, _ = app_client
    resp = client.post("/api/deployments/999999/resolve", json=FEEDBACK)
    assert resp.status_code == 200  # existing not-found convention: {"status": "error"}
    assert resp.json()["status"] == "error"


def test_auth_required_when_api_key_configured(app_client, monkeypatch):
    client, main_module = app_client
    monkeypatch.setattr(main_module, "RESOLVE_API_KEY", "secret")
    dep_id = _create_deployment(client)

    no_key = client.post(f"/api/deployments/{dep_id}/resolve", json=FEEDBACK)
    assert no_key.status_code == 401

    wrong_key = client.post(
        f"/api/deployments/{dep_id}/resolve", json=FEEDBACK,
        headers={"X-API-Key": "wrong"},
    )
    assert wrong_key.status_code == 401

    right_key = client.post(
        f"/api/deployments/{dep_id}/resolve", json=FEEDBACK,
        headers={"X-API-Key": "secret"},
    )
    assert right_key.status_code == 200


def test_rate_limit_blocks_excess_resolve_requests(app_client, monkeypatch):
    client, main_module = app_client
    monkeypatch.setattr(main_module, "_RATE_LIMIT_MAX_REQUESTS", 1)
    monkeypatch.setattr(main_module, "_RATE_LIMIT_WINDOW_SECONDS", 60)
    main_module._rate_limit_hits.clear()

    dep_a = _create_deployment(client)
    dep_b = _create_deployment(client)

    r1 = client.post(f"/api/deployments/{dep_a}/resolve", json=FEEDBACK)
    assert r1.status_code == 200

    r2 = client.post(f"/api/deployments/{dep_b}/resolve", json=FEEDBACK)
    assert r2.status_code == 429


def test_retrain_job_status_is_queryable(app_client):
    client, _ = app_client
    dep_id = _create_deployment(client)
    resp = client.post(f"/api/deployments/{dep_id}/resolve", json=FEEDBACK)
    job_id = resp.json()["retrain_job_id"]

    job = client.get(f"/api/retrain-jobs/{job_id}").json()
    assert job["id"] == job_id
    assert job["deployment_id"] == dep_id

    missing = client.get("/api/retrain-jobs/999999")
    assert missing.status_code == 404


def test_prediction_endpoint_unaffected(app_client):
    client, _ = app_client
    resp = client.post("/api/predict", json=VALID_FORM)
    assert resp.status_code == 200
    body = resp.json()
    assert "predicted_duration_minutes" in body
    assert body["predicted_duration_minutes"] >= 0


# ── Locking behaviour (issue #41: no concurrent retraining) ─────────────────

def test_training_lock_prevents_concurrent_claims(app_client):
    _, main_module = app_client
    from db import try_acquire_training_lock, release_training_lock

    assert try_acquire_training_lock(job_id=1) is True
    assert try_acquire_training_lock(job_id=2) is False  # already held
    release_training_lock()
    assert try_acquire_training_lock(job_id=3) is True  # free again
    release_training_lock()
