from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import re
from pydantic import BaseModel, field_validator
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict
from typing import Optional
import requests
import os
from dotenv import load_dotenv

from fuzzy_engine import compute_resources
from data_pipeline import load_full_data

load_dotenv()

app = FastAPI(title="Traffic Intelligence Engine API — TraffiSense AI")

# Replace https://traffisense-ai.vercel.app with your actual production
# Vercel domain. The regex below additionally allows any *.vercel.app
# preview-deployment URL (e.g. traffisense-ai-git-feature-you.vercel.app).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://traffisense-ai.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load ML model ────────────────────────────────────────────────────────────
MODEL_PATH = "model.joblib"
try:
    model_pipeline = joblib.load(MODEL_PATH)
    print("Model loaded OK")
except FileNotFoundError:
    model_pipeline = None
    print(f"Warning: Model not found at {MODEL_PATH}")

# ── Pre-load analytics data once at startup ──────────────────────────────────
print("Loading analytics dataset...")
_df = load_full_data()
print(f"Analytics dataset: {len(_df)} rows loaded")

from db import init_db, add_deployment, get_deployments, resolve_deployment
try:
    init_db()
    print("Database initialized successfully.")
except Exception as e:
    print("Failed to initialize database:", e)

# ── Historical lookup helpers ────────────────────────────────────────────────
_CAUSE_CLOSURE_RATE: dict[str, float] = {}
_CAUSE_AVG_DURATION: dict[str, float] = {}
_JUNCTION_COUNTS: dict[str, int] = {}
_CORRIDOR_HOUR_PROFILE: dict[str, list[int]] = {}

def _precompute():
    global _CAUSE_CLOSURE_RATE, _CAUSE_AVG_DURATION, _JUNCTION_COUNTS, _CORRIDOR_HOUR_PROFILE
    df = _df.copy()

    # Closure rate per event cause
    for cause, grp in df.groupby('event_cause'):
        _CAUSE_CLOSURE_RATE[cause] = round(grp['requires_road_closure'].mean() * 100, 1)

    # Avg duration per event cause (only rows with valid duration)
    dur_df = df[df['resolution_time_minutes'].notna() &
                (df['resolution_time_minutes'] > 0) &
                (df['resolution_time_minutes'] < 1440)]
    for cause, grp in dur_df.groupby('event_cause'):
        _CAUSE_AVG_DURATION[cause] = round(grp['resolution_time_minutes'].mean(), 1)

    # Junction hotspot counts
    junc_series = df[df['junction'] != '']['junction']
    _JUNCTION_COUNTS = dict(Counter(junc_series).most_common(20))

    # Events per hour per corridor
    for corridor, grp in df.groupby('corridor'):
        hour_counts = [0] * 24
        for h, cnt in grp['hour_of_day'].value_counts().items():
            hour_counts[int(h)] = int(cnt)
        _CORRIDOR_HOUR_PROFILE[corridor] = hour_counts

_precompute()


# ══════════════════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ══════════════════════════════════════════════════════════════════════════════

POLICE_STATION_MAX_LENGTH = 100
POLICE_STATION_PATTERN = re.compile(r"^[A-Za-z0-9\s.\-]+$")

class IncidentRequest(BaseModel):
    event_cause: str
    veh_type: str
    corridor: str
    priority: str
    time: str          # ISO format
    requires_road_closure: bool
    event_type: str
    latitude: float
    longitude: float
    police_station: str
    description: str
    event_scale: Optional[str] = "Medium"
    crowd_size: Optional[int] = 0

    @field_validator("police_station")
    @classmethod
    def validate_police_station(cls, value: str) -> str:
        v = (value or "").strip()
        if not v:
            raise ValueError("Police Station is required.")
        if len(v) > POLICE_STATION_MAX_LENGTH:
            raise ValueError(
                f"Police Station must be {POLICE_STATION_MAX_LENGTH} characters or fewer."
            )
        if not POLICE_STATION_PATTERN.match(v):
            raise ValueError(
                "Police Station may only contain letters, numbers, spaces, "
                "hyphens and periods."
            )
        return v

class Coordinate(BaseModel):
    lat: float
    lng: float

class PredictionResponse(BaseModel):
    predicted_duration_minutes: float
    personnel_needed: int
    barricades_needed: int
    diversion_route: list[Coordinate] = []
    ripple_effect_warning: str = ""
    road_closure_probability: float = 0.0   # % from historical data
    historical_avg_duration: float = 0.0    # mins, same cause
    similar_past_events: int = 0            # count of matching events
    risk_level: str = "Low"                 # Low / Medium / High / Critical
    congestion_radius_meters: float = 0.0
    commuter_delay_minutes: float = 0.0


# ── OSRM routing helper ───────────────────────────────────────────────────────
def get_real_diversion_route(lat: float, lng: float) -> list[dict]:
    lat_a, lng_a = lat - 0.003, lng - 0.003
    lat_b, lng_b = lat + 0.003, lng + 0.003
    lat_c, lng_c = lat + 0.002, lng - 0.002

    # Public free OSRM routing
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lng_a},{lat_a};{lng_c},{lat_c};{lng_b},{lat_b}?overview=full&geometries=geojson"
    try:
        response = requests.get(osrm_url, timeout=3.0)
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                coords = data["routes"][0]["geometry"]["coordinates"]
                return [{"lat": c[1], "lng": c[0]} for c in coords]
    except Exception as e:
        print("OSRM routing failed, using fallback route simulation:", e)
    
    # Fallback simulation
    off = 0.003
    return [
        {"lat": lat - off, "lng": lng - off},
        {"lat": lat + off/2, "lng": lng - off},
        {"lat": lat + off, "lng": lng + off/2},
        {"lat": lat + off, "lng": lng + off},
    ]


@app.post("/api/predict", response_model=PredictionResponse)
def predict_resources(request: IncidentRequest):
    # ── Time features ────────────────────────────────────────────────────────
    try:
        dt = datetime.fromisoformat(request.time.replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.now()
    hour_of_day = dt.hour
    day_of_week = dt.weekday()
    is_weekend  = 1 if day_of_week in [5, 6] else 0

    priority_map     = {'Low': 1, 'Medium': 2, 'High': 3}
    corridor_priority = priority_map.get(request.priority, 1)

    severity_keywords = ['severe', 'fatal', 'fire', 'water', 'heavy', 'blast', 'accident', 'dead', 'injur']
    has_severity_keyword = 1 if any(kw in request.description.lower() for kw in severity_keywords) else 0

    input_data = pd.DataFrame([{
        'latitude': request.latitude,
        'longitude': request.longitude,
        'hour_of_day': hour_of_day,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend,
        'event_cause': request.event_cause,
        'veh_type': request.veh_type,
        'corridor': request.corridor,
        'corridor_priority': corridor_priority,
        'requires_road_closure': int(request.requires_road_closure),
        'event_type': request.event_type,
        'police_station': request.police_station,
        'has_severity_keyword': has_severity_keyword,
    }])

    if model_pipeline:
        try:
            predicted_duration = float(model_pipeline.predict(input_data)[0])
        except Exception as e:
            print("Predict error:", e)
            predicted_duration = _CAUSE_AVG_DURATION.get(request.event_cause, 60.0)
    else:
        predicted_duration = _CAUSE_AVG_DURATION.get(request.event_cause, 60.0)

    predicted_duration = max(0.0, predicted_duration)

    # ── Fuzzy logic resources ────────────────────────────────────────────────
    base_personnel, base_barricades = compute_resources(predicted_duration, corridor_priority)

    # ── Scale factors based on event scale & crowd size ──────────────────────
    import math
    scale_factors = {'Small': 0.8, 'Medium': 1.2, 'Large': 2.0}
    scale_factor = scale_factors.get(request.event_scale, 1.2)
    
    crowd_size = request.crowd_size if request.crowd_size else 0
    crowd_factor = 1.0 + (math.log10(max(1, crowd_size)) / 3.0 if crowd_size > 0 else 0.0)
    
    # Scale resources based on event size/crowd size
    personnel = int(round(base_personnel * scale_factor * crowd_factor))
    barricades = int(round(base_barricades * scale_factor * crowd_factor))
    
    # Cap resources to realistic bounds
    personnel = max(1, min(30, personnel))
    barricades = max(0, min(80, barricades))

    # Calculate congestion impact metrics
    # Congestion radius: 4m per minute of delay
    base_radius = predicted_duration * 4.0  
    priority_factor = {1: 1.0, 2: 1.5, 3: 2.2}.get(corridor_priority, 1.0)
    # Scale up based on severity but cap it to avoid massive map circles
    congestion_radius = base_radius * scale_factor * priority_factor
    congestion_radius = max(100.0, min(1200.0, round(congestion_radius, 1)))

    commuter_delay = (predicted_duration * 0.3) * scale_factor * priority_factor * crowd_factor
    commuter_delay = max(1.0, min(180.0, round(commuter_delay, 1)))

    # ── Historical enrichment ────────────────────────────────────────────────
    road_closure_prob   = _CAUSE_CLOSURE_RATE.get(request.event_cause, 0.0)
    historical_avg_dur  = _CAUSE_AVG_DURATION.get(request.event_cause, 0.0)

    # Count similar events in dataset
    similar_mask = (
        (_df['event_cause'] == request.event_cause) &
        (_df['corridor'] == request.corridor)
    )
    similar_past_events = int(similar_mask.sum())

    # ── Risk level ───────────────────────────────────────────────────────────
    if predicted_duration > 120 and corridor_priority == 3:
        risk_level = "Critical"
    elif predicted_duration > 60 or road_closure_prob > 40:
        risk_level = "High"
    elif predicted_duration > 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # ── Ripple effect ────────────────────────────────────────────────────────
    ripple = ""
    if predicted_duration > 60 and corridor_priority == 3:
        ripple = f"CRITICAL: Secondary congestion expected in adjacent zones within 30 min due to {predicted_duration:.0f}m clearance. Recommend preemptive signal tuning."
    elif predicted_duration > 40:
        ripple = "WARNING: Moderate ripple effect likely. Monitor adjacent junctions closely."

    # ── Real street-level diversion route via OSRM/Mappls ────────────────────
    diversion_route = get_real_diversion_route(request.latitude, request.longitude)

    return PredictionResponse(
        predicted_duration_minutes=round(predicted_duration, 1),
        personnel_needed=int(personnel),
        barricades_needed=int(barricades),
        diversion_route=diversion_route,
        ripple_effect_warning=ripple,
        road_closure_probability=road_closure_prob,
        historical_avg_duration=historical_avg_dur,
        similar_past_events=similar_past_events,
        risk_level=risk_level,
        congestion_radius_meters=congestion_radius,
        commuter_delay_minutes=commuter_delay,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/analytics/overview")
def analytics_overview():
    """Summary stats for the dashboard header."""
    total = len(_df)
    active = int((_df['status'] == 'active').sum()) if 'status' in _df.columns else 0
    high_priority = int((_df['priority'] == 'High').sum())
    road_closures = int(_df['requires_road_closure'].sum())
    return {
        "total_events": total,
        "active_events": active,
        "high_priority": high_priority,
        "road_closures": road_closures,
    }


@app.get("/api/analytics/cause_breakdown")
def cause_breakdown():
    """Event count per cause, sorted descending."""
    counts = _df['event_cause'].value_counts().to_dict()
    result = []
    for cause, count in sorted(counts.items(), key=lambda x: -x[1]):
        result.append({
            "cause": cause,
            "count": count,
            "closure_rate": _CAUSE_CLOSURE_RATE.get(cause, 0.0),
            "avg_duration": _CAUSE_AVG_DURATION.get(cause, 0.0),
        })
    return result


@app.get("/api/analytics/hotspots")
def junction_hotspots(top: int = Query(10, ge=1, le=20)):
    """Top junction hotspots by event count."""
    result = []
    for i, (junction, count) in enumerate(list(_JUNCTION_COUNTS.items())[:top]):
        junc_df = _df[_df['junction'] == junction]
        lat = junc_df['latitude'].median()
        lng = junc_df['longitude'].median()
        result.append({
            "rank": i + 1,
            "junction": junction,
            "count": count,
            "lat": round(float(lat), 6) if pd.notna(lat) else None,
            "lng": round(float(lng), 6) if pd.notna(lng) else None,
        })
    return result


@app.get("/api/analytics/corridor_profile")
def corridor_profile(corridor: str = Query("Mysore Road")):
    """Hourly event distribution for a given corridor (24 buckets)."""
    hours = _CORRIDOR_HOUR_PROFILE.get(corridor, [0] * 24)
    return [{"hour": h, "count": hours[h]} for h in range(24)]


@app.get("/api/analytics/corridors")
def list_corridors():
    """Return all corridor names with event counts."""
    counts = _df['corridor'].value_counts().to_dict()
    return [{"corridor": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])]


@app.get("/api/analytics/zone_summary")
def zone_summary():
    """Per-zone event counts and high-priority fraction."""
    result = []
    for zone, grp in _df.groupby('zone'):
        if not zone or zone == 'unknown':
            continue
        result.append({
            "zone": zone,
            "total": len(grp),
            "high_priority": int((grp['priority'] == 'High').sum()),
            "road_closures": int(grp['requires_road_closure'].sum()),
        })
    return sorted(result, key=lambda x: -x['total'])


@app.get("/api/analytics/heatmap_points")
def heatmap_points(limit: int = Query(2000, ge=100, le=5000)):
    """Return lat/lng points for heatmap rendering (sampled for performance)."""
    valid = _df[_df['latitude'].notna() & _df['longitude'].notna()].copy()
    # Weight high-priority events more
    sample = valid.sample(min(limit, len(valid)), random_state=42)
    result = []
    for _, row in sample.iterrows():
        result.append({
            "lat": round(float(row['latitude']), 5),
            "lng": round(float(row['longitude']), 5),
            "weight": 3 if row['priority'] == 'High' else 1,
        })
    return result


@app.get("/api/analytics/planned_vs_unplanned")
def planned_vs_unplanned():
    """Planned vs unplanned breakdown by cause."""
    result = []
    for etype, grp in _df.groupby('event_type'):
        causes = grp['event_cause'].value_counts().head(6).to_dict()
        result.append({"type": etype, "total": len(grp), "causes": causes})
    return result


# ── Grid Density ─────────────────────────────────────────────────────────────
# Bangalore bounding box (lat/lng)
BLAT_MIN, BLAT_MAX = 12.82, 13.18
BLNG_MIN, BLNG_MAX = 77.40, 77.80

# At lat ~13°N: 1° lat ≈ 111 km, 1° lng ≈ 108.2 km
# sqrt(0.5 km²) ≈ 0.707 km side → 0.707/111 ≈ 0.00637° lat, 0.707/108.2 ≈ 0.00653° lng
GRID_LAT = 0.0064
GRID_LNG = 0.0065

def _apply_filters(hour_start: int, hour_end: int, month: int) -> pd.DataFrame:
    df = _df.copy()
    if hour_start <= hour_end:
        df = df[(df['hour_of_day'] >= hour_start) & (df['hour_of_day'] <= hour_end)]
    else:  # overnight range e.g. 22–06
        df = df[(df['hour_of_day'] >= hour_start) | (df['hour_of_day'] <= hour_end)]
    if month > 0 and 'start_datetime' in df.columns:
        df = df[df['start_datetime'].dt.month == month]
    return df


@app.get("/api/analytics/grid_density")
def grid_density(
    hour_start: int = Query(0,  ge=0, le=23),
    hour_end:   int = Query(23, ge=0, le=23),
    month:      int = Query(0,  ge=0, le=12),   # 0 = all months
):
    """
    Divide Bengaluru into ~0.5 km² grid cells and return per-cell incident
    density with optional hour-of-day and month filters.
    """
    df = _apply_filters(hour_start, hour_end, month)

    # Restrict to Bangalore bbox and valid coords
    df = df[
        df['latitude'].between(BLAT_MIN, BLAT_MAX) &
        df['longitude'].between(BLNG_MIN, BLNG_MAX)
    ].dropna(subset=['latitude', 'longitude'])

    if len(df) == 0:
        return {"cells": [], "max_count": 0, "total_filtered": 0}

    # Assign grid row/col
    df = df.copy()
    df['grid_row'] = ((df['latitude']  - BLAT_MIN) / GRID_LAT).astype(int)
    df['grid_col'] = ((df['longitude'] - BLNG_MIN) / GRID_LNG).astype(int)

    cells = []
    for (row, col), grp in df.groupby(['grid_row', 'grid_col']):
        lat_min = round(BLAT_MIN + row * GRID_LAT, 5)
        lng_min = round(BLNG_MIN + col * GRID_LNG, 5)

        cause_counts = grp['event_cause'].value_counts()
        top_cause    = cause_counts.index[0] if len(cause_counts) else 'unknown'
        cause_brkdn  = cause_counts.head(4).to_dict()

        dur_valid = grp[grp['resolution_time_minutes'].between(0, 1440)] \
            if 'resolution_time_minutes' in grp.columns else pd.DataFrame()
        avg_dur = round(float(dur_valid['resolution_time_minutes'].mean()), 1) \
            if len(dur_valid) > 0 else None

        zone_counts  = grp['zone'].value_counts()
        dominant_zone = zone_counts.index[0] if len(zone_counts) else 'unknown'

        cells.append({
            "grid_id":      f"{row}_{col}",
            "lat_min":      lat_min,
            "lat_max":      round(lat_min + GRID_LAT, 5),
            "lng_min":      lng_min,
            "lng_max":      round(lng_min + GRID_LNG, 5),
            "center_lat":   round(lat_min + GRID_LAT / 2, 5),
            "center_lng":   round(lng_min + GRID_LNG / 2, 5),
            "count":        len(grp),
            "high_priority":int((grp['priority'] == 'High').sum()),
            "road_closures":int(grp['requires_road_closure'].sum()),
            "top_cause":    top_cause,
            "cause_breakdown": cause_brkdn,
            "avg_duration": avg_dur,
            "planned":      int((grp['event_type'] == 'planned').sum()),
            "unplanned":    int((grp['event_type'] == 'unplanned').sum()),
            "zone":         dominant_zone,
        })

    max_count = max(c['count'] for c in cells) if cells else 1
    return {
        "cells":          sorted(cells, key=lambda x: -x['count']),
        "max_count":      max_count,
        "total_filtered": int(len(df)),
    }


@app.get("/api/analytics/grid_cell_detail")
def grid_cell_detail(grid_id: str, hour_start: int = 0, hour_end: int = 23, month: int = 0):
    """Return detailed stats for a single grid cell."""
    try:
        row, col = map(int, grid_id.split('_'))
    except ValueError:
        return {"error": "Invalid grid_id"}

    df = _apply_filters(hour_start, hour_end, month)
    df = df.dropna(subset=['latitude', 'longitude'])
    df = df.copy()
    df['grid_row'] = ((df['latitude']  - BLAT_MIN) / GRID_LAT).astype(int)
    df['grid_col'] = ((df['longitude'] - BLNG_MIN) / GRID_LNG).astype(int)
    grp = df[(df['grid_row'] == row) & (df['grid_col'] == col)]

    if len(grp) == 0:
        return {"count": 0, "grid_id": grid_id}

    # Hour distribution
    hour_dist = [int((grp['hour_of_day'] == h).sum()) for h in range(24)]

    # Cause breakdown
    cause_brkdn = grp['event_cause'].value_counts().to_dict()

    dur_valid = grp[grp['resolution_time_minutes'].between(0, 1440)] \
        if 'resolution_time_minutes' in grp.columns else pd.DataFrame()

    return {
        "grid_id":       grid_id,
        "count":         len(grp),
        "high_priority": int((grp['priority'] == 'High').sum()),
        "road_closures": int(grp['requires_road_closure'].sum()),
        "planned":       int((grp['event_type'] == 'planned').sum()),
        "unplanned":     int((grp['event_type'] == 'unplanned').sum()),
        "cause_breakdown": cause_brkdn,
        "hour_distribution": hour_dist,
        "avg_duration":  round(float(dur_valid['resolution_time_minutes'].mean()), 1) if len(dur_valid) > 0 else None,
        "zone":          grp['zone'].value_counts().index[0] if len(grp) > 0 else 'unknown',
        "junctions":     grp[grp['junction'] != '']['junction'].value_counts().head(5).to_dict(),
    }


# ══════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT & FEEDBACK LOGGING ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

class DeploymentRequest(BaseModel):
    form: IncidentRequest
    predictions: PredictionResponse

class DeploymentFeedback(BaseModel):
    actual_duration: float
    actual_personnel: int
    actual_barricades: int
    actual_congestion_radius: float
    actual_delay: float
    feedback_comments: Optional[str] = ""

@app.post("/api/deployments")
def create_deployment(req: DeploymentRequest):
    data = req.form.dict()
    preds = {
        "predicted_duration": req.predictions.predicted_duration_minutes,
        "personnel": req.predictions.personnel_needed,
        "barricades": req.predictions.barricades_needed,
        "congestion_radius_meters": req.predictions.congestion_radius_meters,
        "commuter_delay_minutes": req.predictions.commuter_delay_minutes
    }
    new_id = add_deployment(data, preds)
    return {"status": "success", "id": new_id}

@app.get("/api/deployments")
def list_deployments(status: Optional[str] = None):
    return get_deployments(status)

@app.post("/api/deployments/{deployment_id}/resolve")
def resolve_existing_deployment(deployment_id: int, feedback: DeploymentFeedback):
    res = resolve_deployment(deployment_id, feedback.dict())
    if not res:
        return {"status": "error", "message": "Deployment not found"}
    
    # Trigger model retraining in background / synchronously for immediate update
    try:
        from ml_model import retrain_with_feedback
        retrained = retrain_with_feedback(res)
        if retrained:
            # Hot-reload the model pipeline
            global model_pipeline
            model_pipeline = joblib.load(MODEL_PATH)
            print("Model hot-reloaded successfully after retraining.")
    except Exception as e:
        print("Failed to retrain or hot-reload model:", e)
        
    return {"status": "success", "deployment": res}

# ══════════════════════════════════════════════════════════════════════════════
# SERVE REACT FRONTEND (Must be at the very bottom)
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/api/analytics/summary")
def analytics_summary(
    hour_start: int = Query(0,  ge=0, le=23),
    hour_end:   int = Query(23, ge=0, le=23),
    month:      int = Query(0,  ge=0, le=12),
    grid_id:    str = Query("", description="Optional: filter to a 0.5km2 grid cell"),
):
    df = _apply_filters(hour_start, hour_end, month)
    cell_info = None
    if grid_id:
        try:
            r, c = map(int, grid_id.split('_'))
            dfc = df.dropna(subset=['latitude','longitude']).copy()
            dfc['grid_row'] = ((dfc['latitude']  - BLAT_MIN) / GRID_LAT).astype(int)
            dfc['grid_col'] = ((dfc['longitude'] - BLNG_MIN) / GRID_LNG).astype(int)
            df = dfc[(dfc['grid_row'] == r) & (dfc['grid_col'] == c)]
            cell_info = {"grid_id": grid_id,
                "center_lat": round(BLAT_MIN + r*GRID_LAT + GRID_LAT/2, 5),
                "center_lng": round(BLNG_MIN + c*GRID_LNG + GRID_LNG/2, 5)}
        except Exception:
            pass
    total = len(df)
    overview = {"total_events": total,
        "active_events": int((df['status'] == 'active').sum()) if 'status' in df.columns else 0,
        "high_priority": int((df['priority'] == 'High').sum()),
        "road_closures": int(df['requires_road_closure'].sum())}
    cause_counts = df['event_cause'].value_counts()
    causes = [{"cause": cause, "count": int(n),
        "closure_rate": _CAUSE_CLOSURE_RATE.get(cause, 0.0),
        "avg_duration":  _CAUSE_AVG_DURATION.get(cause, 0.0)}
        for cause, n in cause_counts.head(10).items()]
    junc_series = df[df['junction'].str.len() > 0]['junction'] if 'junction' in df.columns else pd.Series(dtype=str)
    junc_counts = junc_series.value_counts().head(10)
    hotspots = []
    for i, (j, cnt) in enumerate(junc_counts.items()):
        rows = df[df['junction'] == j]
        hotspots.append({"rank": i+1, "junction": j, "count": int(cnt),
            "lat": round(float(rows['latitude'].median()), 6) if pd.notna(rows['latitude'].median()) else None,
            "lng": round(float(rows['longitude'].median()),6) if pd.notna(rows['longitude'].median()) else None})
    zones = []
    for zone, grp in df.groupby('zone'):
        if not zone or zone == 'unknown': continue
        zones.append({"zone": zone, "total": len(grp),
            "high_priority": int((grp['priority']=='High').sum()),
            "road_closures": int(grp['requires_road_closure'].sum())})
    zones.sort(key=lambda x: -x['total'])
    hour_dist = [int((df['hour_of_day'] == h).sum()) for h in range(24)]
    return {"overview": overview, "causes": causes, "hotspots": hotspots,
        "zones": zones[:8], "hour_distribution": hour_dist,
        "is_filtered": (hour_start!=0 or hour_end!=23 or month!=0 or bool(grid_id)),
        "cell_info": cell_info}


# ══════════════════════════════════════════════════════════════════════════════
# DBSCAN SPATIAL CLUSTERING
# ══════════════════════════════════════════════════════════════════════════════

from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
import math

# Cluster palette — up to 30 distinct colours
_CLUSTER_COLORS = [
    "#ef4444","#f97316","#eab308","#22c55e","#06b6d4",
    "#3b82f6","#8b5cf6","#ec4899","#14b8a6","#f59e0b",
    "#84cc16","#0ea5e9","#a855f7","#f43f5e","#10b981",
    "#6366f1","#fb923c","#4ade80","#38bdf8","#c084fc",
    "#fbbf24","#34d399","#60a5fa","#f472b6","#a78bfa",
    "#2dd4bf","#fb7185","#818cf8","#4ade80","#facc15",
]

# Pre-compute/dynamic cluster variables
_DBSCAN_CLUSTERS: list = []
_DBSCAN_LABELLED_DF: pd.DataFrame = pd.DataFrame()   # full labelled dataframe

def run_dbscan_dynamic(hour_start: int = 0, hour_end: int = 23, month: int = 0):
    """
    Run DBSCAN dynamically on-the-fly based on time and month filters.
    Converts coordinates to radians for a mathematically correct haversine metric.
    """
    global _DBSCAN_CLUSTERS, _DBSCAN_LABELLED_DF
    
    # Start with all cleaned data
    df = _df.dropna(subset=["latitude", "longitude"]).copy()
    
    # 1. Month filter (1-indexed: 1=Jan, 2=Feb, etc.)
    if month > 0:
        df = df[df['start_datetime'].dt.month == month]
        
    # 2. Hour filter
    if hour_start <= hour_end:
        df = df[df['hour_of_day'].between(hour_start, hour_end)]
    else:
        # Overlapping midnight
        df = df[(df['hour_of_day'] >= hour_start) | (df['hour_of_day'] <= hour_end)]

    # Limit to Bengaluru bounding box to filter out anomalies
    df = df[
        df["latitude"].between(12.82, 13.18) &
        df["longitude"].between(77.40, 77.80)
    ]

    if len(df) < 5:
        _DBSCAN_CLUSTERS = []
        _DBSCAN_LABELLED_DF = df
        return

    coords = df[["latitude", "longitude"]].values
    
    # IMPORTANT: Convert to radians for haversine metric!
    coords_rad = np.radians(coords)

    # Tight, dense clustering criteria: 500m radius, min 10 points
    eps_rad = 0.50 / 6371.0
    
    db = DBSCAN(eps=eps_rad, min_samples=10, algorithm="ball_tree", metric="haversine")
    labels = db.fit_predict(coords_rad)

    df["cluster"] = labels
    _DBSCAN_LABELLED_DF = df

    clusters = []
    for label in sorted(set(labels)):
        if label == -1:          # noise points — skip
            continue
        grp = df[df["cluster"] == label]
        pts = grp[["latitude", "longitude"]].values

        # Convex hull (need ≥3 points)
        hull_coords = []
        if len(pts) >= 3:
            try:
                hull = ConvexHull(pts)
                hull_pts = pts[hull.vertices]
                # close the polygon
                hull_pts = list(hull_pts) + [hull_pts[0]]
                hull_coords = [[float(p[0]), float(p[1])] for p in hull_pts]
            except Exception:
                hull_coords = [[float(p[0]), float(p[1])] for p in pts]
        else:
            hull_coords = [[float(p[0]), float(p[1])] for p in pts]

        center_lat = float(grp["latitude"].mean())
        center_lng = float(grp["longitude"].mean())

        cause_counts  = grp["event_cause"].value_counts()
        top_cause     = cause_counts.index[0] if len(cause_counts) else "unknown"
        high_pri_pct  = round(float((grp["priority"] == "High").mean() * 100), 1)
        closure_pct   = round(float(grp["requires_road_closure"].mean() * 100), 1)

        dur_valid = grp[
            grp["resolution_time_minutes"].notna() &
            grp["resolution_time_minutes"].between(0, 1440)
        ] if "resolution_time_minutes" in grp.columns else pd.DataFrame()
        avg_dur = round(float(dur_valid["resolution_time_minutes"].mean()), 1) if len(dur_valid) > 0 else None

        dists = [
            math.sqrt((r["latitude"] - center_lat)**2 + (r["longitude"] - center_lng)**2) * 111
            for _, r in grp.iterrows()
        ]
        radius_km = round(float(sum(dists) / max(len(dists), 1)), 2)

        clusters.append({
            "cluster_id":        int(label),
            "count":             len(grp),
            "center_lat":        round(center_lat, 5),
            "center_lng":        round(center_lng, 5),
            "hull":              hull_coords,
            "top_cause":         top_cause,
            "cause_breakdown":   cause_counts.head(5).to_dict(),
            "high_priority_pct": high_pri_pct,
            "road_closure_pct":  closure_pct,
            "avg_duration":      avg_dur,
            "radius_km":         radius_km,
        })

    # Sort clusters by event count descending
    _DBSCAN_CLUSTERS = sorted(clusters, key=lambda x: -x["count"])
    
    # Assign distinct colors to sorted clusters
    for idx, c in enumerate(_DBSCAN_CLUSTERS):
        c["color"] = _CLUSTER_COLORS[idx % len(_CLUSTER_COLORS)]

    print(f"DBSCAN (dynamic): {len(_DBSCAN_CLUSTERS)} clusters found with {len(df)} samples")


# Run initial DBSCAN with default constraints on startup
run_dbscan_dynamic()


@app.get("/api/analytics/clusters")
def get_clusters(hour_start: int = 0, hour_end: int = 23, month: int = 0):
    """
    Return DBSCAN spatial clusters computed dynamically under the current filter criteria.
    """
    run_dbscan_dynamic(hour_start=hour_start, hour_end=hour_end, month=month)
    return {
        "clusters": _DBSCAN_CLUSTERS,
        "total_clusters": len(_DBSCAN_CLUSTERS),
    }


@app.get("/api/analytics/cluster_summary/{cluster_id}")
def cluster_summary(cluster_id: int):
    """
    Return full analytics for a single DBSCAN cluster from the last computed set.
    """
    if _DBSCAN_LABELLED_DF.empty:
        return {"error": "Clusters not yet computed"}

    grp = _DBSCAN_LABELLED_DF[_DBSCAN_LABELLED_DF["cluster"] == cluster_id]
    if len(grp) == 0:
        return {"error": f"Cluster {cluster_id} not found"}

    # Find the ranked index of this cluster (sorted by count desc)
    rank = next((i+1 for i, c in enumerate(_DBSCAN_CLUSTERS) if c["cluster_id"] == cluster_id), "?")
    color = next((c["color"] for c in _DBSCAN_CLUSTERS if c["cluster_id"] == cluster_id), "#3b82f6")

    # Overview
    total = len(grp)
    active = int((grp["status"] == "active").sum()) if "status" in grp.columns else 0
    high_priority = int((grp["priority"] == "High").sum())
    road_closures = int(grp["requires_road_closure"].sum())
    overview = {"total_events": total, "active_events": active,
                "high_priority": high_priority, "road_closures": road_closures}

    # Causes
    cause_counts = grp["event_cause"].value_counts()
    causes = [{"cause": c, "count": int(n),
               "closure_rate": _CAUSE_CLOSURE_RATE.get(c, 0.0),
               "avg_duration":  _CAUSE_AVG_DURATION.get(c, 0.0)}
              for c, n in cause_counts.head(10).items()]

    # Junction hotspots within cluster
    junc_series = grp[grp["junction"].str.len() > 0]["junction"] if "junction" in grp.columns else pd.Series(dtype=str)
    junc_counts = junc_series.value_counts().head(8)
    hotspots = []
    for i, (j, cnt) in enumerate(junc_counts.items()):
        rows = grp[grp["junction"] == j]
        hotspots.append({"rank": i+1, "junction": j, "count": int(cnt),
            "lat": round(float(rows["latitude"].median()), 6) if pd.notna(rows["latitude"].median()) else None,
            "lng": round(float(rows["longitude"].median()), 6) if pd.notna(rows["longitude"].median()) else None})

    # Zones within cluster
    zones = []
    for zone, zgrp in grp.groupby("zone"):
        if not zone or zone == "unknown": continue
        zones.append({"zone": zone, "total": len(zgrp),
            "high_priority": int((zgrp["priority"] == "High").sum()),
            "road_closures": int(zgrp["requires_road_closure"].sum())})
    zones.sort(key=lambda x: -x["total"])

    # Hour distribution
    hour_dist = [int((grp["hour_of_day"] == h).sum()) for h in range(24)]

    # Cluster metadata for banner
    cluster_info = {
        "cluster_id":  cluster_id,
        "rank":        rank,
        "color":       color,
        "center_lat":  round(float(grp["latitude"].mean()), 4),
        "center_lng":  round(float(grp["longitude"].mean()), 4),
        "top_cause":   cause_counts.index[0] if len(cause_counts) else "unknown",
    }

    return {"overview": overview, "causes": causes, "hotspots": hotspots,
            "zones": zones[:8], "hour_distribution": hour_dist,
            "is_filtered": True, "cell_info": None,
            "cluster_info": cluster_info}


# ══════════════════════════════════════════════════════════════════════════════
# SERVE REACT FRONTEND (Must be at the very bottom)
# ══════════════════════════════════════════════════════════════════════════════

from fastapi import HTTPException
import os

if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        return FileResponse("static/index.html")
