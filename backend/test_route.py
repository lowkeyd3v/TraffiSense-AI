"""
Tests for the routing service in routing.py (used by main.py's /api/predict
diversion-route logic).

test_route.py used to be a standalone script that fired a *live* HTTP request
to the Mappls routing API at import time -- pytest collection itself made a
network call and required MAPPLS_ACCESS_TOKEN (issue #54). The app doesn't
use Mappls at all anymore; routing goes through routing.get_real_diversion_route(),
which talks to an OSRM-compatible service (issue #43) with retries, a
fallback simulated route, and an in-memory cache.

These tests mock requests.get so no real network call is ever made and no
external credentials are required. The route cache is cleared before every
test since several tests intentionally reuse the same coordinates.
"""

import pytest
from unittest.mock import patch, Mock
import requests

import routing
from routing import get_real_diversion_route, clear_route_cache


LAT, LNG = 12.9716, 77.5946


@pytest.fixture(autouse=True)
def _clear_cache():
    """The route cache is keyed by rounded (lat, lng); clear it before each
    test so tests don't see stale results from one another."""
    clear_route_cache()
    yield
    clear_route_cache()


def _mock_response(status_code=200, routes=None):
    mock_response = Mock()
    mock_response.status_code = status_code
    if routes is not None:
        mock_response.json.return_value = {"routes": routes}
    return mock_response


@patch("routing.requests.get")
def test_returns_osrm_route_when_available(mock_get):
    coordinates = [[77.5946, 12.9716], [77.5950, 12.9720], [77.5955, 12.9725]]
    mock_get.return_value = _mock_response(
        200, routes=[{"geometry": {"coordinates": coordinates}}]
    )

    route = get_real_diversion_route(LAT, LNG)

    mock_get.assert_called_once()
    called_url = mock_get.call_args[0][0]
    assert called_url.startswith(routing.OSRM_BASE_URL)

    assert route == [
        {"lat": 12.9716, "lng": 77.5946},
        {"lat": 12.9720, "lng": 77.5950},
        {"lat": 12.9725, "lng": 77.5955},
    ]


@patch("routing.time.sleep")  # skip real backoff delays
@patch("routing.requests.get")
def test_falls_back_after_retries_on_server_error(mock_get, mock_sleep):
    mock_get.return_value = _mock_response(500)

    route = get_real_diversion_route(LAT, LNG)

    # 5xx is retried up to OSRM_MAX_RETRIES additional times.
    assert mock_get.call_count == routing.OSRM_MAX_RETRIES + 1
    off = 0.003
    assert route == [
        {"lat": LAT - off, "lng": LNG - off},
        {"lat": LAT + off / 2, "lng": LNG - off},
        {"lat": LAT + off, "lng": LNG + off / 2},
        {"lat": LAT + off, "lng": LNG + off},
    ]


@patch("routing.time.sleep")
@patch("routing.requests.get")
def test_falls_back_immediately_on_client_error_no_retry(mock_get, mock_sleep):
    mock_get.return_value = _mock_response(404)

    route = get_real_diversion_route(LAT, LNG)

    # 4xx is not retried -- it's treated as a definitive answer.
    mock_get.assert_called_once()
    assert len(route) == 4


@patch("routing.time.sleep")
@patch("routing.requests.get")
def test_falls_back_when_no_routes_in_response(mock_get, mock_sleep):
    mock_get.return_value = _mock_response(200, routes=[])

    route = get_real_diversion_route(LAT, LNG)

    # 200 with an empty route list is also not retried.
    mock_get.assert_called_once()
    assert len(route) == 4


@patch("routing.time.sleep")
@patch("routing.requests.get")
def test_falls_back_when_request_raises(mock_get, mock_sleep):
    mock_get.side_effect = requests.exceptions.ConnectionError("no network")

    route = get_real_diversion_route(LAT, LNG)

    assert mock_get.call_count == routing.OSRM_MAX_RETRIES + 1
    assert len(route) == 4
    assert all("lat" in point and "lng" in point for point in route)


@patch("routing.requests.get")
def test_successful_route_is_cached_for_same_coordinates(mock_get):
    coordinates = [[77.5946, 12.9716], [77.5950, 12.9720]]
    mock_get.return_value = _mock_response(
        200, routes=[{"geometry": {"coordinates": coordinates}}]
    )

    first = get_real_diversion_route(LAT, LNG)
    second = get_real_diversion_route(LAT, LNG)

    assert first == second
    mock_get.assert_called_once()  # second call served from cache