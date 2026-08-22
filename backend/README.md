# TraffiSense AI — Backend Service

The backend of **TraffiSense AI** is a high-performance, asynchronous REST API built with **FastAPI**. It powers predictive clearance modeling, fuzzy logic resource allocation, dynamic spatial analytics (DBSCAN & grid density), automated model retraining, and diversion routing.

---

## 🏗️ Architecture & Modules

```
backend/
├── main.py              # FastAPI application, route handlers, analytics & DBSCAN endpoints
├── ml_model.py          # Scikit-Learn GradientBoostingRegressor training & validation pipeline
├── fuzzy_engine.py      # Scikit-Fuzzy IRC:SP:55 / MoRTH-aligned resource allocation system
├── data_pipeline.py     # Data cleaning, feature extraction & spatial imputation (BallTree)
├── db.py                # Database layer (PostgreSQL / SQLite) & retraining lock mutex
├── routing.py           # Configurable OSRM routing client with caching & fallback
├── requirements.txt     # Production dependencies
├── requirements_train.txt # Training & testing dependencies (pytest, httpx)
├── test_model.py        # Model loading test
└── test_route.py        # Routing client unit & mock tests
```

---

## ⚡ Key Capabilities

### 1. Machine Learning Inference (`ml_model.py`)
- **Algorithm**: `GradientBoostingRegressor` (`n_estimators=300`, `learning_rate=0.05`, `max_depth=5`, `subsample=0.8`).
- **Feature Pipeline**: Combines spatial coordinates (latitude, longitude), temporal features (hour of day, day of week, weekend indicator), categorical metadata (event cause, vehicle type, corridor, priority, police station, event type), NLP severity flags, and road closure indicators.
- **Model Promotion & Hot Reloading**: Retraining evaluates candidate models on held-out test splits. Promoted models are atomically written to disk and hot-reloaded into memory under thread locks without service downtime.

### 2. Fuzzy Logic Resourcing Engine (`fuzzy_engine.py`)
- **Standard**: Aligned with Indian Road Congress (IRC:SP:55) and Ministry of Road Transport & Highways (MoRTH) resourcing guidelines.
- **Inputs**: Predicted duration (0–300 min), corridor priority (Low/Medium/High), composite severity score (0–10), and crowd size (0–2000+).
- **Outputs**:
  - `personnel_needed`: Officer headcount recommendations (0–30).
  - `barricades_needed`: Taper & barrier counts (0–80).
  - `resource_allocation_score`: Deployment intensity (0–10, Low to Critical).
  - `response_priority_score`: Dispatch urgency (0–10, Low to Critical).

### 3. Spatial Hotspot & Clustering Analytics (`main.py`)
- **DBSCAN Dynamic Clustering**: Uses haversine distance metric (500m radius, min 10 points) to compute spatial clusters and convex hull polygons dynamically filtered by time-of-day and month.
- **Grid Density**: Divides Bengaluru into ~0.5 km² bounding cells with incident breakdowns, priority ratios, and duration metrics.

### 4. Resilient Diversion Routing (`routing.py`)
- Interfaces with OSRM-compatible routing engines.
- Features exponential backoff retries, in-memory TTL caching for duplicate coordinates, and graceful fallback to simulated diversion loops if network calls fail.

### 5. Persistent Deployment Logs & Retraining (`db.py`)
- Uses **SQLAlchemy** with PostgreSQL in production (Render) and falls back to SQLite in local development.
- Tracks deployed resources, actual post-incident outcomes, and background retraining jobs protected by a database-backed mutex lock.

---

## 🔌 API Reference

### Health & Prediction
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service health check. |
| `POST` | `/api/predict` | Computes ML duration prediction, fuzzy resourcing, congestion radius, and diversion route. |

### Analytics & Spatial Data
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/analytics/overview` | Overall city-wide event statistics and active counts. |
| `GET` | `/api/analytics/cause_breakdown` | Event frequencies, closure rates, and average durations per cause. |
| `GET` | `/api/analytics/hotspots` | Top junction hotspots with median coordinates. |
| `GET` | `/api/analytics/corridor_profile` | 24-hour distribution for a selected corridor. |
| `GET` | `/api/analytics/corridors` | List of all monitored corridors and incident counts. |
| `GET` | `/api/analytics/zone_summary` | Summary of events and high-priority ratios per police zone. |
| `GET` | `/api/analytics/heatmap_points` | Weighted coordinates for spatial heatmap rendering. |
| `GET` | `/api/analytics/grid_density` | ~0.5 km² grid cells with filtered density metrics. |
| `GET` | `/api/analytics/grid_cell_detail` | In-depth statistics for a single grid cell. |
| `GET` | `/api/analytics/summary` | Combined summary filtered by hour, month, and optional grid cell. |
| `GET` | `/api/analytics/clusters` | Dynamically computed DBSCAN clusters with convex hulls. |
| `GET` | `/api/analytics/cluster_summary/{cluster_id}` | Detailed analytics for a specific DBSCAN cluster. |

### Deployments & Model Feedback
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/deployments` | Create a new active deployment log. |
| `GET` | `/api/deployments` | List deployments (filter by `status=active` or `status=resolved`). |
| `POST` | `/api/deployments/{id}/resolve` | Record post-event actuals and schedule background model retraining. |
| `GET` | `/api/retrain-jobs` | List recent model retraining jobs and outcomes. |
| `GET` | `/api/retrain-jobs/{job_id}` | Retrieve specific retraining job status and metrics. |
| `POST` | `/api/model/rollback` | Roll back model to previous production backup. |

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | *(empty -> SQLite `db.sqlite3`)* | PostgreSQL connection string (e.g. on Render). |
| `ALLOWED_ORIGINS` | `http://localhost:5173,https://traffisense-ai.vercel.app` | Comma-separated CORS allowlist. |
| `OSRM_BASE_URL` | `http://router.project-osrm.org` | OSRM routing server URL. |
| `OSRM_PROFILE` | `driving` | OSRM routing profile (`driving`, `walking`, `cycling`). |
| `OSRM_TIMEOUT_SECONDS` | `3.0` | HTTP request timeout for routing. |
| `RESOLVE_API_KEY` | *(empty -> open)* | Secret required in `X-API-Key` header for `/resolve` and `/rollback`. |
| `RESOLVE_RATE_LIMIT_MAX` | `5` | Max requests per IP window on resolve endpoint. |
| `RESOLVE_RATE_LIMIT_WINDOW` | `60` | Rate limit window in seconds. |

---

## 🚀 Setup & Local Development

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)

### 2. Installation
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements_train.txt
```

### 3. Train ML Model
```bash
# Trains model from ../dataset.csv and saves to ../ml/model.joblib
python ml_model.py

# Copy trained model artifact to backend working directory
# Windows (PowerShell):
Copy-Item ..\ml\model.joblib .\model.joblib
# Linux/macOS:
cp ../ml/model.joblib ./model.joblib
```

### 4. Run Development Server
```bash
uvicorn main:app --reload --port 8000
```
- API live at: `http://127.0.0.1:8000`
- Interactive OpenAPI Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc docs: `http://127.0.0.1:8000/redoc`

### 5. Run Automated Tests
```bash
# From backend directory:
pytest -v

# From repository root:
pytest tests backend/ -v
```
