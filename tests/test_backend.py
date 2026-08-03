import os
import sys

import pytest
from pydantic import ValidationError

# backend/ has no __init__.py, so add it to sys.path to import main directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import IncidentRequest  # noqa: E402


def test_basic():
    assert 1 + 1 == 2


# ── Police Station validation (issue #17) ───────────────────────────────────

VALID_BASE_PAYLOAD = {
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


@pytest.mark.parametrize("name", [
    "Central Traffic Police Station",
    "MG Road PS",
    "Police Station No. 2",
    "Traffic-Control Unit",
])
def test_police_station_accepts_valid_names(name):
    payload = {**VALID_BASE_PAYLOAD, "police_station": name}
    request = IncidentRequest(**payload)
    assert request.police_station == name


@pytest.mark.parametrize("name", [
    "7556@#$%^*#$@%Q^&W%ETDDDDGFFFFI",
    "Station!!!",
    "PS#1",
    "   ",
    "",
])
def test_police_station_rejects_invalid_input(name):
    payload = {**VALID_BASE_PAYLOAD, "police_station": name}
    with pytest.raises(ValidationError):
        IncidentRequest(**payload)


def test_police_station_rejects_over_max_length():
    payload = {**VALID_BASE_PAYLOAD, "police_station": "A" * 101}
    with pytest.raises(ValidationError):
        IncidentRequest(**payload)


def test_police_station_accepts_max_length():
    payload = {**VALID_BASE_PAYLOAD, "police_station": "A" * 100}
    request = IncidentRequest(**payload)
    assert len(request.police_station) == 100