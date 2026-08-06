#  TraffiSense AI (Traffic Intelligence Engine)

Predictive traffic intelligence dashboard for event-driven congestion — forecasts gridlock impact and recommends resource deployment before it happens.

**Live demo:** [traffi-sense-ai-neon.vercel.app](https://traffi-sense-ai-neon.vercel.app)
**API docs:** [traffisense-ai-2.onrender.com/docs](https://traffisense-ai-2.onrender.com/docs) — the bare API root (`/`) intentionally returns `404 Not Found`, since this is an API-only backend with no route defined for `/`; only `/docs` and the actual `/api/...` endpoints resolve.

---

## 📌 Overview

Planned events (concerts, matches, rallies) and unplanned incidents (accidents, waterlogging, breakdowns) create localized traffic breakdowns across a city. Today, that impact is rarely quantified in advance — resource deployment (officers, barricades, diversions) is largely experience-driven, with no systematic post-event learning loop.

TraffiSense AI predicts how long an incident will block traffic, how far the congestion is likely to ripple, and exactly what resources a precinct should deploy — using a model trained on historical Bengaluru traffic-event data.

## 🚀 Core Workflow

1. **Event Input** — an operator logs an incident: cause, location, corridor, vehicle type, priority, crowd size, and description.
2. **ML Inference** — a Scikit-Learn `GradientBoostingRegressor`, trained on historical resolution times, predicts expected clearance duration from the event's spatial, temporal, and categorical features.
3. **Fuzzy Logic Resourcing** — the predicted duration and corridor priority are run through a `scikit-fuzzy` control system to derive personnel and barricade counts.
4. **Spatial Analytics** — DBSCAN clustering surfaces recurring incident hotspots and corridor-level hourly patterns from the historical dataset, computed live and filterable by hour/month.
5. **Diversion Routing & Mapping** — a driving route around the incident is fetched from OSRM and rendered on an interactive Leaflet/OpenStreetMap view, along with a congestion-radius overlay.
6. **Automated Advisory** — one click generates a pre-formatted public advisory ready to post to WhatsApp or X (Twitter).
7. **Feedback Loop** — resolved deployments can be logged with actual outcomes, closing the loop between prediction and reality.

## 🛠️ Tech Stack

**Frontend**
- React 19 + Vite
- Tailwind CSS v4
- Leaflet + React-Leaflet (OpenStreetMap tiles — no API key required)
- Recharts (analytics visualizations)
- Axios

**Backend**
- FastAPI (async Python API)
- Scikit-Learn (`GradientBoostingRegressor` for duration prediction)
- Scikit-Fuzzy (resource-allocation control system)
- Pandas / NumPy / SciPy (data pipeline, DBSCAN clustering, feature engineering)
- SQLAlchemy + PostgreSQL (deployment log storage; falls back to local SQLite in dev)
- OSRM (routing API for diversion paths — self-hostable, configurable via env vars, see [Routing Service](#️-routing-service))

**Infrastructure**
- Frontend deployed on **Vercel**
- Backend + Postgres deployed on **Render** (see `render.yaml`)

## 🏗️ File Structure

```
TraffiSense-AI/
├── backend/
│   ├── main.py              # FastAPI app — routes, CORS, DBSCAN analytics
│   ├── routing.py            # Configurable OSRM routing client — retries, caching, fallback
│   ├── db.py                 # Postgres/SQLite deployment log storage (SQLAlchemy)
│   ├── ml_model.py           # GradientBoostingRegressor training + persistence
│   ├── fuzzy_engine.py       # scikit-fuzzy resource-allocation system
│   ├── data_pipeline.py      # Historical dataset loading & cleaning
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── vercel.json
│   ├── src/
│   │   ├── App.jsx                    # Layout controller / view state
│   │   ├── LeafletMap.jsx             # Leaflet/OSM map (marker, diversion route, radius)
│   │   ├── Analytics.jsx              # City-wide analytics view
│   │   ├── GridMap.jsx                # Grid-density map view
│   │   ├── Feedback.jsx               # Deployment feedback / outcome logging
│   │   ├── constants.js               # Shared enums, API base URL config
│   │   ├── utils/fixLeafletIcons.js   # Leaflet default-marker icon fix for bundlers
│   │   └── components/
│   │       ├── LandingPage.jsx
│   │       ├── Header.jsx
│   │       ├── LiveFeeds.jsx          # Simulated live event feed aggregator
│   │       ├── SidebarForm.jsx        # Event input panel
│   │       └── ResultsPanel.jsx       # KPI dashboard, ROI analysis, map
│   └── package.json
│
├── dataset.csv               # Historical Bengaluru traffic-event dataset
├── ml/                        # Trained model artifact + feature-importance outputs
├── render.yaml                # Render deployment blueprint
└── README.md
```

## 🎯 Key Features

- **Predictive clearance modeling** — estimates how long an intersection or corridor will stay blocked, based on historical patterns for similar events.
- **Fuzzy resource allocation** — translates predicted duration and priority into concrete officer and barricade counts.
- **Spatial hotspot analysis** — DBSCAN-based clustering of historical incidents, filterable by hour-of-day and month, with per-cluster breakdowns (causes, closure rate, zones).
- **Live diversion mapping** — OSRM-routed diversion paths and congestion radius rendered on an interactive Leaflet map.
- **ROI & impact analysis** — estimated commuter time saved by AI-assisted response vs. unassisted response.
- **One-click public advisory** — auto-generated, hashtag-ready alert text for WhatsApp/X.
- **Deployment feedback loop** — log actual outcomes against predictions to track model performance over time.

## 🏁 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements_train.txt
python ml_model.py            # trains the model (writes to ../ml/model.joblib)
cp ../ml/model.joblib .        # main.py loads it from the backend/ working directory
uvicorn main:app --reload --port 8000
```
The API will be live at `http://127.0.0.1:8000`, with interactive docs at `/docs`.

By default the backend uses a local SQLite database (`db.sqlite3`). To use Postgres locally instead, set a `DATABASE_URL` environment variable before starting the server.

By default the backend allows requests from `http://localhost:5173` and `https://traffisense-ai.vercel.app`.
To allow additional origins (e.g. a custom domain or a Vercel preview URL), set `ALLOWED_ORIGINS` as a
comma-separated list before starting the server, e.g.:
```bash
export ALLOWED_ORIGINS="https://traffisense-ai.vercel.app,https://your-preview-url.vercel.app"
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The app will be live at `http://localhost:5173` and will talk to the local backend automatically.

## 🗺️ Routing Service

Diversion routes are generated by calling an [OSRM](http://project-osrm.org/)-API-compatible
routing service (`backend/routing.py`). By default this points at the public
OSRM demo server (`router.project-osrm.org`) so the app works out of the box for local
development — **that demo server is not intended for production traffic** (no uptime
guarantee, shared rate limits, community-run infrastructure).

For a production deployment, self-host OSRM (or point at a managed OSRM-compatible
provider) and configure the backend via environment variables — no code changes needed:

| Variable | Default | Description |
|---|---|---|
| `OSRM_BASE_URL` | `http://router.project-osrm.org` | Base URL of the routing service. |
| `OSRM_PROFILE` | `driving` | Routing profile (`driving` / `walking` / `cycling`). |
| `OSRM_TIMEOUT_SECONDS` | `3.0` | Per-request timeout. |
| `OSRM_MAX_RETRIES` | `2` | Retries on network errors / 5xx responses (exponential backoff), before falling back to a simulated route. |
| `OSRM_RETRY_BACKOFF_SECONDS` | `0.25` | Base backoff between retries. |
| `ROUTE_CACHE_TTL_SECONDS` | `300` | How long a route for a given location is cached before it's re-fetched. |
| `ROUTE_CACHE_MAX_SIZE` | `500` | Max number of cached routes kept in memory. |

If the routing service is unreachable after retries, the API falls back to a
locally-simulated diversion loop rather than failing the request — incident reporting
never blocks on routing availability.

### Self-hosting OSRM

`docker-compose.osrm.yml` (repo root) spins up a self-hosted OSRM instance preconfigured
for the Bengaluru/Karnataka region used by the sample dataset:

```bash
docker compose -f docker-compose.osrm.yml up -d
```

This downloads the Karnataka OSM extract, pre-processes it (`osrm-extract` +
`osrm-partition` + `osrm-customize`, using the MLD routing algorithm), and serves it on
`http://localhost:5000`. Point the backend at it with:

```bash
export OSRM_BASE_URL=http://localhost:5000
```

For other regions, swap the `.osm.pbf` download URL in the compose file for the
relevant [Geofabrik extract](https://download.geofabrik.de/).

## ☁️ Deployment

This project is deployed as two independent services:

- **Backend** (`backend/`) → Render, via `render.yaml`. Provisions a web service and a managed Postgres database automatically.
- **Frontend** (`frontend/`) → Vercel, with `VITE_API_URL` set to the Render backend's URL.

See `render.yaml` and `frontend/vercel.json` for the exact build/start configuration.

## 🗺️ Roadmap / Known Limitations

- Current model's explanatory power (R²) is modest — predictions lean on historical averages for less-represented event types. Improving feature engineering and training data volume is the next priority.
- Render's free-tier Postgres and web service have standard free-tier limitations (90-day database expiry, cold starts on inactivity).
