"""
routing.py — Diversion-route generation service.

Resolves issue #43: the app previously hit the public OSRM demo server
(router.project-osrm.org) hardcoded directly in main.py. That server is
explicitly "not for production use" — no uptime guarantee, aggressive
rate limiting, and a single shared endpoint for the entire internet.

This module makes the routing backend:
  * configurable via environment variables (self-hosted OSRM, a paid
    OSRM/OSMR-compatible provider, etc. — anything speaking the OSRM
    HTTP API)
  * resilient — retries transient failures with backoff, then falls back
    to a locally-simulated route instead of failing the whole request
  * fast under repeat load — an in-memory TTL cache avoids re-requesting
    routes for incidents reported at (roughly) the same location
"""

from __future__ import annotations

import os
import time
import threading
from typing import Optional

import requests


# ══════════════════════════════════════════════════════════════════════════
# Configuration (all overridable via environment variables)
# ══════════════════════════════════════════════════════════════════════════

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# Base URL of an OSRM-API-compatible routing server. Defaults to the public
# OSRM demo server so local dev / first-run still works out of the box, but
# production deployments MUST override this — see README "Routing Service"
# section for how to self-host OSRM (docker-compose file included) or point
# at a managed provider.
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org").rstrip("/")

# Optional profile segment (OSRM supports driving / walking / cycling).
OSRM_PROFILE = os.getenv("OSRM_PROFILE", "driving")

# Per-request timeout, in seconds.
OSRM_TIMEOUT_SECONDS = _env_float("OSRM_TIMEOUT_SECONDS", 3.0)

# Retry policy for transient network/5xx failures.
OSRM_MAX_RETRIES = _env_int("OSRM_MAX_RETRIES", 2)
OSRM_RETRY_BACKOFF_SECONDS = _env_float("OSRM_RETRY_BACKOFF_SECONDS", 0.25)

# Response cache: avoids re-hitting the routing service for incidents that
# land on (roughly) the same spot within a short window.
ROUTE_CACHE_TTL_SECONDS = _env_float("ROUTE_CACHE_TTL_SECONDS", 300.0)
ROUTE_CACHE_MAX_SIZE = _env_int("ROUTE_CACHE_MAX_SIZE", 500)

# How many decimal places to round coordinates to when building a cache key.
# 4 decimal places ≈ 11m of precision — plenty for "same incident" matching
# without fragmenting the cache over GPS jitter.
ROUTE_CACHE_COORD_PRECISION = _env_int("ROUTE_CACHE_COORD_PRECISION", 4)


# ══════════════════════════════════════════════════════════════════════════
# In-memory TTL cache (simple, dependency-free, thread-safe)
# ══════════════════════════════════════════════════════════════════════════

class _TTLCache:
    def __init__(self, ttl_seconds: float, max_size: int):
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: dict[str, tuple[float, list[dict]]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[list[dict]]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: list[dict]) -> None:
        with self._lock:
            if len(self._store) >= self._max_size and key not in self._store:
                # Evict the oldest entry (cheap FIFO-ish eviction; good
                # enough for a bounded diagnostic cache, not a hot path).
                oldest_key = min(self._store, key=lambda k: self._store[k][0], default=None)
                if oldest_key is not None:
                    del self._store[oldest_key]
            self._store[key] = (time.monotonic() + self._ttl, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)


_route_cache = _TTLCache(ROUTE_CACHE_TTL_SECONDS, ROUTE_CACHE_MAX_SIZE)


def clear_route_cache() -> None:
    """Exposed for tests / ops tooling."""
    _route_cache.clear()


def _cache_key(lat: float, lng: float) -> str:
    p = ROUTE_CACHE_COORD_PRECISION
    return f"{round(lat, p)}:{round(lng, p)}"


# ══════════════════════════════════════════════════════════════════════════
# Routing
# ══════════════════════════════════════════════════════════════════════════

def _fallback_route(lat: float, lng: float) -> list[dict]:
    """Locally-simulated diversion loop, used when the routing service is
    unavailable so the API never fails an incident report just because
    routing is degraded."""
    off = 0.003
    return [
        {"lat": lat - off, "lng": lng - off},
        {"lat": lat + off / 2, "lng": lng - off},
        {"lat": lat + off, "lng": lng + off / 2},
        {"lat": lat + off, "lng": lng + off},
    ]


def _request_route_from_osrm(lat_a, lng_a, lat_c, lng_c, lat_b, lng_b) -> Optional[list[dict]]:
    url = (
        f"{OSRM_BASE_URL}/route/v1/{OSRM_PROFILE}/"
        f"{lng_a},{lat_a};{lng_c},{lat_c};{lng_b},{lat_b}"
        f"?overview=full&geometries=geojson"
    )

    last_error = None
    for attempt in range(OSRM_MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=OSRM_TIMEOUT_SECONDS)
            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes") or []
                if routes:
                    coords = routes[0]["geometry"]["coordinates"]
                    return [{"lat": c[1], "lng": c[0]} for c in coords]
                # 200 with no routes is a definitive "no route" answer —
                # retrying won't help.
                return None
            if response.status_code < 500:
                # Client-side error (bad request, rate limited, etc.) —
                # retrying the same request won't help.
                print(f"Routing service returned {response.status_code}, not retrying: {url}")
                return None
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as e:
            last_error = str(e)

        if attempt < OSRM_MAX_RETRIES:
            time.sleep(OSRM_RETRY_BACKOFF_SECONDS * (2 ** attempt))

    print(f"Routing service unavailable after {OSRM_MAX_RETRIES + 1} attempt(s): {last_error}")
    return None


def get_real_diversion_route(lat: float, lng: float) -> list[dict]:
    """Return a driving diversion route around (lat, lng).

    Tries the configured OSRM-compatible routing service (with retries),
    serves cached results for repeat locations, and falls back to a
    locally-simulated loop if the service is unavailable — routing
    degrades gracefully instead of failing the incident report.
    """
    key = _cache_key(lat, lng)
    cached = _route_cache.get(key)
    if cached is not None:
        return cached

    lat_a, lng_a = lat - 0.003, lng - 0.003
    lat_b, lng_b = lat + 0.003, lng + 0.003
    lat_c, lng_c = lat + 0.002, lng - 0.002

    route = _request_route_from_osrm(lat_a, lng_a, lat_c, lng_c, lat_b, lng_b)
    if route is None:
        # Don't cache the fallback — we want the next request to retry the
        # real service rather than pinning a degraded response for the TTL.
        return _fallback_route(lat, lng)

    _route_cache.set(key, route)
    return route
