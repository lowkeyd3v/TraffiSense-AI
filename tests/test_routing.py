import os
import sys
import importlib
from unittest.mock import MagicMock, patch

import pytest
import requests

# backend/ has no __init__.py, so add it to sys.path to import routing directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import routing  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_routing_state():
    """Every test gets a clean cache and fast retry timings."""
    routing.clear_route_cache()
    routing.OSRM_MAX_RETRIES = 1
    routing.OSRM_RETRY_BACKOFF_SECONDS = 0.001
    yield
    routing.clear_route_cache()


def _ok_response(coords):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"routes": [{"geometry": {"coordinates": coords}}]}
    return resp


def test_osrm_base_url_is_configurable_via_env():
    """Acceptance criterion: routing endpoint is configurable via env vars,
    and the public demo server is no longer hardcoded."""
    old_value = os.environ.get("OSRM_BASE_URL")
    os.environ["OSRM_BASE_URL"] = "https://osrm.internal.example.com"
    try:
        importlib.reload(routing)
        assert routing.OSRM_BASE_URL == "https://osrm.internal.example.com"
        with patch("routing.requests.get", return_value=_ok_response([[1, 2]])) as m:
            routing.get_real_diversion_route(1.0, 2.0)
            called_url = m.call_args[0][0]
            assert called_url.startswith("https://osrm.internal.example.com/")
    finally:
        # Restore the env var *before* reloading so the module picks the
        # default back up for subsequent tests.
        if old_value is None:
            os.environ.pop("OSRM_BASE_URL", None)
        else:
            os.environ["OSRM_BASE_URL"] = old_value
        importlib.reload(routing)


def test_successful_route_matches_existing_response_shape():
    """Existing routing functionality (list of {lat, lng} dicts) is unchanged."""
    coords = [[77.59, 12.97], [77.591, 12.971], [77.592, 12.972]]
    with patch("routing.requests.get", return_value=_ok_response(coords)):
        route = routing.get_real_diversion_route(12.97, 77.59)
    assert route == [
        {"lat": 12.97, "lng": 77.59},
        {"lat": 12.971, "lng": 77.591},
        {"lat": 12.972, "lng": 77.592},
    ]


def test_falls_back_gracefully_on_connection_error():
    with patch("routing.requests.get", side_effect=requests.exceptions.ConnectionError("down")):
        route = routing.get_real_diversion_route(12.97, 77.59)
    assert len(route) == 4
    assert all({"lat", "lng"} <= set(pt) for pt in route)


def test_falls_back_gracefully_on_timeout():
    with patch("routing.requests.get", side_effect=requests.exceptions.Timeout("slow")):
        route = routing.get_real_diversion_route(12.97, 77.59)
    assert len(route) == 4


def test_retries_on_server_error_then_falls_back():
    resp = MagicMock(status_code=503)
    with patch("routing.requests.get", return_value=resp) as m:
        route = routing.get_real_diversion_route(1.0, 1.0)
    assert len(route) == 4
    assert m.call_count == routing.OSRM_MAX_RETRIES + 1


def test_does_not_retry_on_client_error():
    resp = MagicMock(status_code=400)
    with patch("routing.requests.get", return_value=resp) as m:
        route = routing.get_real_diversion_route(2.0, 2.0)
    assert len(route) == 4
    assert m.call_count == 1


def test_recovers_after_transient_failure_succeeds_on_retry():
    fail = MagicMock(status_code=503)
    ok = _ok_response([[5.0, 6.0]])
    with patch("routing.requests.get", side_effect=[fail, ok]) as m:
        route = routing.get_real_diversion_route(6.0, 5.0)
    assert route == [{"lat": 6.0, "lng": 5.0}]
    assert m.call_count == 2


def test_repeated_requests_for_same_location_are_cached():
    with patch("routing.requests.get", return_value=_ok_response([[1.0, 1.0]])) as m:
        routing.get_real_diversion_route(1.0, 1.0)
        routing.get_real_diversion_route(1.0, 1.0)
    assert m.call_count == 1


def test_different_locations_are_not_conflated_in_cache():
    with patch("routing.requests.get", return_value=_ok_response([[1.0, 1.0]])) as m:
        routing.get_real_diversion_route(1.0, 1.0)
        routing.get_real_diversion_route(50.0, 50.0)
    assert m.call_count == 2


def test_fallback_route_is_not_cached_so_next_call_retries_service():
    with patch("routing.requests.get", side_effect=requests.exceptions.ConnectionError("down")) as m:
        routing.get_real_diversion_route(9.0, 9.0)
        routing.get_real_diversion_route(9.0, 9.0)
    assert m.call_count == 2 * (routing.OSRM_MAX_RETRIES + 1)


def test_no_route_found_returns_fallback_without_retry():
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"routes": []}
    with patch("routing.requests.get", return_value=resp) as m:
        route = routing.get_real_diversion_route(3.0, 3.0)
    assert len(route) == 4
    assert m.call_count == 1
