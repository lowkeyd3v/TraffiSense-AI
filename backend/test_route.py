"""
Tests for the OSRM-based diversion-route helper in main.py.

This file used to be a standalone script that fired a *live* HTTP request to
the Mappls routing API as soon as pytest imported it during test collection
(see issue #54). That made test collection depend on network access and an
unset MAPPLS_ACCESS_TOKEN, and it wasn't structured as pytest tests at all.

The app itself no longer uses Mappls -- routing now goes through OSRM via
main.get_real_diversion_route(). These tests exercise that function with
requests.get mocked out, so no real network call is ever made and no
external credentials are required.
"""

from unittest.mock import patch, Mock

from main import get_real_diversion_route


def _mock_osrm_response(coordinates):
    """Build a Mock object that looks like a successful OSRM response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "routes": [{"geometry": {"coordinates": coordinates}}]
    }
    return mock_response


@patch("main.requests.get")
def test_get_real_diversion_route_uses_osrm_result_when_available(mock_get):
    # OSRM returns coordinates as [lng, lat] pairs.
    coordinates = [[77.5946, 12.9716], [77.5950, 12.9720], [77.5955, 12.9725]]
    mock_get.return_value = _mock_osrm_response(coordinates)

    route = get_real_diversion_route(12.9716, 77.5946)

    mock_get.assert_called_once()
    called_url = mock_get.call_args[0][0]
    assert called_url.startswith("http://router.project-osrm.org/route/v1/driving/")

    assert route == [
        {"lat": 12.9716, "lng": 77.5946},
        {"lat": 12.9720, "lng": 77.5950},
        {"lat": 12.9725, "lng": 77.5955},
    ]


@patch("main.requests.get")
def test_get_real_diversion_route_falls_back_when_osrm_errors(mock_get):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    lat, lng = 12.9716, 77.5946
    route = get_real_diversion_route(lat, lng)

    # Falls back to the deterministic simulated route rather than raising.
    off = 0.003
    assert route == [
        {"lat": lat - off, "lng": lng - off},
        {"lat": lat + off / 2, "lng": lng - off},
        {"lat": lat + off, "lng": lng + off / 2},
        {"lat": lat + off, "lng": lng + off},
    ]


@patch("main.requests.get")
def test_get_real_diversion_route_falls_back_when_request_raises(mock_get):
    import requests

    mock_get.side_effect = requests.exceptions.ConnectionError("no network")

    lat, lng = 12.9716, 77.5946
    route = get_real_diversion_route(lat, lng)

    # Should not raise -- falls back to the simulated route.
    assert len(route) == 4
    assert all("lat" in point and "lng" in point for point in route)


@patch("main.requests.get")
def test_get_real_diversion_route_falls_back_when_no_routes_in_response(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"routes": []}
    mock_get.return_value = mock_response

    lat, lng = 12.9716, 77.5946
    route = get_real_diversion_route(lat, lng)

    assert len(route) == 4