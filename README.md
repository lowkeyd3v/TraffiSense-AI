# TraffiSense AI: Predictive Urban Traffic Intelligence Engine

<div align="center">

[![AI for Public Good](https://img.shields.io/badge/AI%20for%20Public%20Good-Urban%20Mobility-emerald?style=for-the-badge)](https://github.com/lowkeyd3v/TraffiSense-AI)
[![CI Status](https://img.shields.io/badge/CI%20Build-Passing-brightgreen?style=for-the-badge&logo=githubactions)](https://github.com/lowkeyd3v/TraffiSense-AI/actions)
[![Tests Passing](https://img.shields.io/badge/Pytest-Passing-success?style=for-the-badge&logo=pytest)](https://github.com/lowkeyd3v/TraffiSense-AI)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

**A predictive traffic intelligence & resource allocation engine for event-driven urban congestion — forecasting gridlock impact, generating IRC-aligned deployment plans, and routing diversions before bottlenecks occur.**

[🌐 Live Prototype](https://traffi-sense-ai-neon.vercel.app) • [📑 API Docs](https://traffisense-ai-2.onrender.com/docs) • [⚡ Quickstart / Local Run](#-how-to-run-locally) • [🏛️ System Architecture](#-system-architecture) • [📊 Core Capabilities](#-core-capabilities) • [📜 API Reference](#-api-documentation) • [🧪 Testing](#-running-automated-tests)

</div>

---

## 📌 Project Overview

| Item | Details |
|---|---|
| **Project Name** | **TraffiSense AI: Predictive Urban Traffic Intelligence Engine** |
| **Mission** | Proactive Gridlock Prevention, IRC-Compliant Resourcing & Dynamic Diversions |
| **Focus Area** | Intelligent Transportation Systems (ITS), Urban Mobility & Police Operations |
| **Repository** | [github.com/lowkeyd3v/TraffiSense-AI](https://github.com/lowkeyd3v/TraffiSense-AI) |
| **Live Application URL** | 🌐 **[https://traffi-sense-ai-neon.vercel.app](https://traffi-sense-ai-neon.vercel.app)** |
| **Live API Swagger Docs** | 📑 **[https://traffisense-ai-2.onrender.com/docs](https://traffisense-ai-2.onrender.com/docs)** |
| **Standards Alignment** | **IRC:SP:55-2014 / MoRTH Guidelines** for Traffic Control & Management |
| **Test Suite** | **Unit, Integration & Build Tests Passing** (Pytest + Vite Build) |

---

## 🔗 Live Application & API Endpoints

- 🌐 **Live Web Application:** [https://traffi-sense-ai-neon.vercel.app](https://traffi-sense-ai-neon.vercel.app)
- 📑 **Interactive OpenAPI (Swagger) Docs:** [https://traffisense-ai-2.onrender.com/docs](https://traffisense-ai-2.onrender.com/docs)
- 📖 **ReDoc Documentation:** [https://traffisense-ai-2.onrender.com/redoc](https://traffisense-ai-2.onrender.com/redoc)
- 🩺 **Live Backend API Root / Health Check:** [https://traffisense-ai-2.onrender.com/](https://traffisense-ai-2.onrender.com/)

---

## 🚀 How to Run Locally

Get the full development stack (FastAPI Backend + React 19 Frontend + ML Engine) up and running in minutes:

```bash
# 1. Clone the repository
git clone https://github.com/lowkeyd3v/TraffiSense-AI.git
cd TraffiSense-AI

# 2. Setup Backend & Train Model
cd backend
python -m venv venv
# Windows (PowerShell): .\venv\Scripts\Activate.ps1 | Linux/macOS: source venv/bin/activate
pip install -r requirements.txt -r requirements_train.txt
python ml_model.py
# Windows: Copy-Item ..\ml\model.joblib .\model.joblib | Linux/macOS: cp ../ml/model.joblib ./model.joblib
uvicorn main:app --reload --port 8000

# 3. In a separate terminal, start the Frontend
cd ../frontend
npm install
npm run dev
```

- 🌐 **Web Dashboard:** `http://localhost:5173`
- 📑 **Interactive OpenAPI (Swagger) Docs:** `http://localhost:8000/docs`
- 📖 **ReDoc API Explorer:** `http://localhost:8000/redoc`

*(Optional: Launch self-hosted high-speed OSRM routing via `docker compose -f docker-compose.osrm.yml up -d`)*

---

## 🌟 Problem Statement & Urban Impact

### The Reality of Event-Driven Gridlock
Rapidly growing metropolises like Bengaluru face massive congestion surges from planned events (rallies, sports fixtures, VIP movements, stadium concerts) and unplanned incidents (waterlogging, multi-vehicle collisions, breakdowns). Traffic management currently suffers from critical vulnerabilities:

1. **Reactive Instead of Proactive Dispatch:** Personnel and barricades are deployed *after* congestion has already propagated several kilometers upstream.
2. **Heuristic & Intuition-Based Sizing:** No standardized computation links crowd scale, corridor priority, and weather severity to exact officer headcounts and perimeter control equipment.
3. **Delayed Commuter Advisories:** Public broadcasts and diversions take 30–60 minutes to coordinate manually, by which time thousands of vehicles are already trapped in choke points.
4. **Lack of Post-Incident Learning Loops:** Real-world incident clearance times are rarely captured systematically to validate or improve predictive planning models.

---

## 💡 The TraffiSense AI Solution

TraffiSense AI replaces guesswork with a predictive machine learning pipeline coupled with an IRC:SP:55/MoRTH-aligned fuzzy decision engine:

```
+---------------------------------------------------------------------------------------------------------+
|                                    TRAFFISENSE AI CORE CAPABILITIES                                     |
|                                                                                                         |
|  [📈 ML Duration Predictor]   --> Forecasts incident clearance time & ripple radius (GradientBoosting)  |
|  [🚦 Fuzzy Resourcing Engine] --> Computes exact officer & barricade counts via IRC:SP:55 control logic|
|  [📍 DBSCAN Hotspot Miner]    --> Auto-clusters spatial hazard zones (500m / haversine convex hulls)    |
|  [🗺️ OSRM Diversion Routing]  --> Computes live detour routes avoiding congestion choke points          |
|  [📢 1-Click Advisory Engine] --> Auto-generates hashtagged, broadcast-ready WhatsApp & X advisories   |
|  [🔄 Safe Retraining Loop]    --> Validates & auto-promotes refreshed model weights upon deployment fix |
+---------------------------------------------------------------------------------------------------------+
```

---

## 🏛️ System Architecture

```
                                  +---------------------------------------------+
                                  |         Traffic Operator / Command HQ       |
                                  |             (Web GIS Control Room)          |
                                  +---------------------------------------------+
                                                         |
                                                         v
                                  +---------------------------------------------+
                                  |              Vercel Global Edge             |
                                  |    - React 19 + Vite 6 Single Page App      |
                                  |    - Leaflet OpenStreetMap Interactive GIS  |
                                  |    - Recharts City Analytics & Density Grid |
                                  +---------------------------------------------+
                                                         |
                                                (REST API JSON / CORS)
                                                         |
                                                         v
+---------------------------------------------------------------------------------------------------------------+
|                                    FastAPI High-Performance Application                                       |
|                                        (Render Python 3.12 Engine)                                            |
|                                                                                                               |
|  +---------------------------+  +----------------------------+  +------------------------------------------+  |
|  |     ML Inference Engine   |  |   Fuzzy Resourcing Engine  |  |           Spatial Analytics              |  |
|  | (GradientBoostingRegressor|  | (IRC:SP:55-2014 & MoRTH    |  | (DBSCAN Clustering, Convex Hulls,        |  |
|  |  Duration & Radius Models)|  |  Fuzzy Associative Memory) |  |  0.5 km² Density Aggregation)            |  |
|  +---------------------------+  +----------------------------+  +------------------------------------------+  |
|  +---------------------------+  +----------------------------+  +------------------------------------------+  |
|  |   OSRM Diversion Router   |  |   Advisory Broadcast API   |  |      Continuous Retraining Pipeline      |  |
|  | (Caching & Auto-Fallback) |  | (Multi-Channel Copy Gen)   |  | (Evaluation, Atomic Promotion, Rollback) |  |
|  +---------------------------+  +----------------------------+  +------------------------------------------+  |
+---------------------------------------------------------------------------------------------------------------+
                 |                                               |                                 |
                 v                                               v                                 v
   +---------------------------+                   +---------------------------+     +---------------------------+
   |    SQLAlchemy Database    |                   |    OSRM Routing Server    |     |   Local Model Storage     |
   | (PostgreSQL / SQLite Dev) |                   | (Demo API / Self-Hosted)  |     | (Joblib Serialized Trees) |
   +---------------------------+                   +---------------------------+     +---------------------------+
```

---

## 📊 Core Capabilities

### 1. 🤖 Predictive Clearance & Congestion Radius
- **Algorithm:** Scikit-Learn `GradientBoostingRegressor` trained on comprehensive Bengaluru incident logs.
- **Inputs:** Spatial coordinates, corridor category, event type, vehicle classification, priority level, crowd estimate, and incident description.
- **Output:** Predicted clearance duration (minutes), expected congestion radius (km), severity index (0–10), and time/fuel savings metrics.

### 2. 🚦 Fuzzy Logic Resource Allocation (IRC:SP:55 / MoRTH)
- **Engine:** `scikit-fuzzy` Mamdani-style Fuzzy Associative Memory (FAM) control system.
- **Input Variables:** Severity score, predicted duration, crowd size, corridor priority.
- **Outputs:** Recommended traffic police officers, field marshals, signages, and physical barricades.

### 3. 📍 Dynamic DBSCAN Spatial Clustering & Grid Density
- **Clustering:** Haversine-based DBSCAN (ε = 500m radius, `min_samples = 10`) identifying persistent high-risk bottleneck areas.
- **Convex Hull Polygons:** Automatically computes minimum enclosing geometry for visualization on Leaflet.
- **Temporal Slicing:** Live filters for time-of-day (0–23h) and month-of-year.

### 4. 🗺️ OSRM Diversion Routing with Fallback
- Connects to Open Source Routing Machine (OSRM) to calculate turn-by-turn bypass routes around incident coordinates.
- Features in-memory TTL caching, retry backoffs, and an algorithmic fallback generator ensuring 100% uptime even during network partitions.

### 5. 📢 Instant Public Advisory Generator
- Generates formatted, ready-to-broadcast traffic bulletins with single-click clipboard copying for WhatsApp Community Channels, Twitter/X alerts, and digital variable-message signs (VMS).

### 6. 🔄 Closed-Loop Feedback & Automated Retraining
- When an incident is cleared, operators log the actual duration and deployed resources.
- The backend evaluates newly accumulated real-world data, runs validation checks, and safely promotes updated model weights with rollback protection.

---

## 🛠️ Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | React 19, Vite 6, Tailwind CSS v4 | Ultra-fast UI with responsive dark control-room theme |
| **Mapping & GIS** | Leaflet, React-Leaflet, OpenStreetMap | Interactive pins, diversion routes, congestion radius circles, convex hulls |
| **Data Viz** | Recharts, Lucide Icons | Responsive delay reduction charts and spatial breakdown graphs |
| **Backend API** | FastAPI, Python 3.12, Uvicorn, Pydantic V2 | Async REST architecture with strict validation and auto-generated OpenAPI |
| **Machine Learning** | Scikit-Learn, Joblib, Pandas, NumPy | Gradient Boosting Regressors, feature engineering pipelines |
| **Fuzzy Decision Logic** | Scikit-Fuzzy, SciPy | IRC:SP:55 compliant multi-criteria control systems |
| **Database & ORM** | SQLAlchemy 2.0, PostgreSQL / SQLite | Robust storage for incident history, deployments, and model metrics |
| **Routing Engine** | OSRM (Open Source Routing Machine) | Street network pathfinding with dockerized self-hosting support |
| **Quality & CI/CD** | Pytest, Oxlint, GitHub Actions, CodeQL | Automated unit testing, static security analysis, and branch protection |

---

## 🏗️ Repository Structure

```
TraffiSense-AI/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Backend & ML CI test pipeline
│       ├── frontend.yml           # Frontend build validation
│       ├── pr-check.yml           # Pull request unit tests & build checks
│       └── codeql.yml             # CodeQL static security analysis
├── backend/
│   ├── main.py                    # FastAPI application, route handlers, DBSCAN & analytics
│   ├── ml_model.py                # GradientBoostingRegressor training, validation & promotion
│   ├── fuzzy_engine.py            # IRC:SP:55 / MoRTH-aligned fuzzy logic control system
│   ├── data_pipeline.py           # Dataset cleaning, feature extraction & spatial imputation
│   ├── db.py                      # SQLAlchemy storage (PostgreSQL/SQLite) & retraining lock
│   ├── routing.py                 # Resilient OSRM diversion routing client with caching
│   ├── requirements.txt           # Production dependencies
│   ├── requirements_train.txt     # Training & test dependencies (pytest, httpx)
│   └── README.md                  # Backend-specific architecture & API guide
├── frontend/
│   ├── index.html                 # Single page application entry point
│   ├── package.json               # Frontend scripts & dependencies
│   ├── vite.config.js             # Vite configuration with Tailwind CSS v4
│   ├── vercel.json                # Vercel deployment & rewrite configuration
│   ├── src/
│   │   ├── App.jsx                # Layout controller & view state management
│   │   ├── LeafletMap.jsx         # Interactive Leaflet map (routes, markers, radius)
│   │   ├── Analytics.jsx          # City-wide charts & KPI visualizer
│   │   ├── GridMap.jsx            # 0.5 km² density grid map & DBSCAN polygon layers
│   │   ├── Feedback.jsx           # Deployment tracking & post-event feedback modal
│   │   ├── constants.js           # Shared enums, bounds, and API configuration
│   │   ├── utils/fixLeafletIcons.js # Leaflet marker asset resolver
│   │   └── components/
│   │       ├── Header.jsx         # Navigation bar & platform features modal
│   │       ├── LandingPage.jsx    # Scenario starters & control center entry
│   │       ├── LiveFeeds.jsx      # Simulated live event feed aggregator
│   │       ├── SidebarForm.jsx    # Incident parameter entry panel
│   │       └── ResultsPanel.jsx   # Prediction metrics, ROI, map & advisory modal
│   └── README.md                  # Frontend-specific architecture & component guide
├── ml/
│   ├── model.joblib               # Trained GradientBoostingRegressor artifact
│   ├── feature_importance.csv     # Extracted feature importance scores
│   └── feature_importance.png     # Feature importance visualization plot
├── tests/
│   ├── test_backend.py            # API request validation & police station tests
│   ├── test_fuzzy_engine.py       # Scikit-fuzzy resourcing & FAM rule tests
│   ├── test_ml.py                 # ML artifact presence tests
│   ├── test_retraining.py         # Retraining pipeline, locking & feedback tests
│   └── test_routing.py            # OSRM routing resilience & cache tests
├── dataset.csv                    # Historical Bengaluru traffic-event dataset
├── docker-compose.osrm.yml        # Self-hosted OSRM container stack
├── render.yaml                    # Render deployment blueprint
└── README.md                      # Project documentation
```

---

## 📜 API Documentation

Below is a summary of the core REST API endpoints provided by the backend:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check & API status probe |
| `POST` | `/api/predict` | Primary prediction: clearance duration, ripple radius & fuzzy resourcing |
| `GET` | `/api/hotspots` | Spatial DBSCAN clusters with convex hull boundary coordinates |
| `GET` | `/api/grid-density` | 0.5 km² density matrix filterable by `hour` and `month` |
| `POST` | `/api/deployments` | Record a new active incident deployment plan |
| `POST` | `/api/deployments/{id}/resolve` | Log actual resolution metrics & trigger safe background retraining |
| `GET` | `/api/model/metrics` | Inspect active model accuracy, training samples & performance history |
| `POST` | `/api/model/rollback` | Roll back to previous verified model weights if validation fails |

---

## 🧪 Running Automated Tests

### Python Backend & ML Test Suite
```bash
# Run all tests with strict markers and verbose reporting:
pytest -v
```

### Frontend Linting & Build Verification
```bash
cd frontend
npm run lint
npm run build
```

---

## ☁️ Deployment

- **Frontend (Vercel):** Configured via `frontend/vercel.json` with seamless SPA route rewrites.
- **Backend (Render):** Configured via `render.yaml` with Python 3.12, managed PostgreSQL, and automated model preparation steps.

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).
