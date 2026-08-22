# TraffiSense AI — Frontend Application

The frontend of **TraffiSense AI** is a responsive, modern traffic intelligence dashboard built with **React 19**, **Vite**, **Tailwind CSS v4**, **Leaflet**, and **Recharts**.

---

## 🎨 Views & Modules

### 1. Landing Page & Scenarios (`components/LandingPage.jsx`)
- **Quick-Start Incident Scenarios**:
  - 🌊 *Urban Flooding* (Tumkur Road corridor)
  - 🚑 *Highway Accident Response* (ORR East corridor)
  - 🚔 *VIP Convoy Management* (Hosur Road / Airport corridor)
- Direct entry into the **Live Feeds** simulator or custom manual incident reporting.

### 2. Incident Prediction & Field Deployment (`components/SidebarForm.jsx`, `components/ResultsPanel.jsx`, `LeafletMap.jsx`)
- **Incident Input Form**: Cause, corridor, priority, vehicle type, GPS coordinates, police station validation, crowd size, and road closure toggle.
- **KPI Metrics Dashboard**: Predicted clearance duration, required officers and barricades, closure probability, and model confidence.
- **ROI & Commuter Impact**: Time saved with AI-managed response vs. unassisted gridlock.
- **Interactive Leaflet Map**: Real-time driving diversion path (via OSRM) and dynamic congestion-radius overlay.
- **Automated Advisory Generator**: One-click broadcast alert formatted for WhatsApp and X (Twitter).

### 3. Live Event Feeds Simulator (`components/LiveFeeds.jsx`)
- Aggregates simulated feeds from ticketing APIs (e.g. stadium matches), meteorological warning services (heavy rain/waterlogging), and social monitoring to proactively anticipate congestion.

### 4. City-Wide Analytics & DBSCAN Clustering (`Analytics.jsx`, `GridMap.jsx`)
- **Grid Density Heatmap**: Divides Bengaluru into ~0.5 km² bounding cells with interactive click-to-inspect metrics.
- **DBSCAN Spatial Risk Zones**: Dynamic clustering of historical incidents using haversine metric (500m radius, min 10 points) rendered as convex hull polygons and centroid markers.
- **Temporal Filters**: Interactive 24-hour range sliders and month-of-year dropdown with live re-computation.
- **Analytics Visualizations**: Cause distribution bars, 24-hour peak hour charts, junction hotspots, and zone rankings.

### 5. Deployments Log & Feedback Loop (`Feedback.jsx`)
- Inspect active field deployments in real time.
- Log actual clearance times, personnel used, and delay metrics to continuously retrain the AI prediction engine.

---

## 📂 Project Structure

```
frontend/
├── index.html               # Entry HTML with meta tags & fonts
├── package.json             # Scripts & dependencies
├── vite.config.js           # Vite configuration with Tailwind CSS v4 & React plugin
├── vercel.json              # Vercel deployment & SPA routing rewrites
├── public/
│   ├── favicon.svg          # App favicon
│   ├── icons.svg            # UI iconography
│   └── hero-image.png       # Landing page banner graphic
└── src/
    ├── App.jsx              # Main layout controller & navigation state
    ├── App.css / index.css  # Global styles & animations
    ├── constants.js         # API URL, corridor names, cause labels, bounds
    ├── LeafletMap.jsx       # Leaflet map with routing polyline & radius circle
    ├── GridMap.jsx          # Density grid map & DBSCAN polygon layers
    ├── Analytics.jsx        # Recharts analytics charts & KPI summaries
    ├── Feedback.jsx         # Field deployment logs & post-event feedback modal
    ├── utils/
    │   └── fixLeafletIcons.js # Leaflet asset path resolution fix for bundlers
    └── components/
        ├── Header.jsx       # Global navigation bar & platform feature modal
        ├── LandingPage.jsx  # Landing view with scenario starters
        ├── LiveFeeds.jsx    # Live API simulated feed aggregator
        ├── SidebarForm.jsx  # Incident parameters input form
        └── ResultsPanel.jsx # Prediction metrics, impact ROI, map & advisory
```

---

## 🛠️ Tech Stack

- **Framework**: React 19 + Vite 6
- **Styling**: Tailwind CSS v4
- **Mapping**: Leaflet 1.9 + React-Leaflet 5 (OpenStreetMap CartoDB tiles)
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Linter**: Oxlint

---

## ⚙️ Environment Configuration

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://127.0.0.1:8000` | Backend API base URL. Set to the Render backend URL in production (e.g. `https://traffisense-ai-2.onrender.com`). |

---

## 🚀 Setup & Local Development

### 1. Prerequisites
- Node.js 18+
- npm 9+

### 2. Installation
```bash
# Navigate to frontend directory
cd frontend

# Install packages
npm install
```

### 3. Start Development Server
```bash
npm run dev
```
The application will be live at `http://localhost:5173`.

### 4. Build for Production
```bash
npm run build
```
Generates optimized static assets in `dist/`.

### 5. Run Linter
```bash
npm run lint
```
Runs `oxlint` across all source files.
