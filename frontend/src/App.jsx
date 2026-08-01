import { useState, useCallback } from 'react'
import axios from 'axios'
import Header from './components/Header'
import SidebarForm from './components/SidebarForm'
import ResultsPanel from './components/ResultsPanel'
import LandingPage from './components/LandingPage'
import Analytics from './Analytics'
import GridMap from './GridMap'
import Feedback from './Feedback'
import LiveFeeds from './components/LiveFeeds'
import { API } from './constants'

const DEFAULT_FORM = {
  event_cause:'vehicle_breakdown', veh_type:'heavy_vehicle',
  corridor: "National Highway 44", priority:'High',
  time: new Date().toISOString().slice(0,16),
  requires_road_closure:false, event_type:'unplanned',
  latitude: 28.6139, longitude: 77.2090,
  police_station: "Central Traffic Control", description:'',
  event_scale: 'Medium',
  crowd_size: 0
}

const DEFAULT_FILTERS = { hourStart: 0, hourEnd: 23, month: 0 }

export default function App() {
  const [view, setView] = useState('landing') // 'landing' | 'dashboard'
  const [tab, setTab] = useState('predict')

  // ── Shared analytics state (lifted for GridMap / Analytics) ──────────────
  const [appliedFilters, setApplied]  = useState(DEFAULT_FILTERS)
  const [pendingFilters, setPending]  = useState(DEFAULT_FILTERS)
  const [selectedGridId, setGridId]   = useState(null)

  const applyFilters = useCallback(() => {
    setApplied({...pendingFilters})
    setGridId(null)
    setClusterId(null)
  }, [pendingFilters])
  const resetAll     = useCallback(() => { setApplied(DEFAULT_FILTERS); setPending(DEFAULT_FILTERS); setGridId(null); setClusterId(null) }, [])
  const selectCell   = useCallback((gid) => setGridId(gid), [])
  const clearCell    = useCallback(() => setGridId(null), [])

  // ── Cluster selection (DBSCAN) ────────────────────────────────────────────
  const [selectedClusterId, setClusterId] = useState(null)
  const selectCluster = useCallback((cid) => { setClusterId(cid); setGridId(null) }, [])
  const clearCluster  = useCallback(() => setClusterId(null), [])
  
  // Predict App State
  const [form, setForm] = useState(DEFAULT_FORM)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)

  const submit = async e => {
    e.preventDefault()
    setLoading(true); setError(null)
    try {
      const res = await axios.post(`${API}/api/predict`, {
        ...form, time: new Date(form.time).toISOString()
      })
      setResults({data: res.data, form})
    } catch {
      setError('Backend error — check server is running.')
    } finally { setLoading(false) }
  }

  const handleScenarioSelect = (scenario) => {
  if (scenario === "water_logging") {
    setForm({
      ...DEFAULT_FORM,
      event_cause: "water_logging",
      corridor: "National Highway 48",
      veh_type: "unknown",
      priority: "High",
      latitude: 28.5355,
      longitude: 77.3910,
      police_station: "Traffic Control Unit",
      description: "Severe waterlogging causing heavy traffic congestion.",
      requires_road_closure: true,
    })
  } else if (scenario === "accident") {
    setForm({
      ...DEFAULT_FORM,
      event_cause: "accident",
      corridor: "Ring Road",
      veh_type: "heavy_vehicle",
      priority: "High",
      latitude: 28.6139,
      longitude: 77.2090,
      police_station: "Central Traffic Control",
      description: "Major road accident causing severe congestion.",
      requires_road_closure: true,
    })
  } else if (scenario === "vip_movement") {
    setForm({
      ...DEFAULT_FORM,
      event_cause: "vip_movement",
      corridor: "Airport Expressway",
      veh_type: "others",
      priority: "Medium",
      latitude: 28.5562,
      longitude: 77.1000,
      police_station: "Airport Traffic Unit",
      description: "Temporary traffic diversion due to VIP movement.",
      requires_road_closure: false,
    })
  } else if (scenario === "manual") {
    setForm(DEFAULT_FORM)
  }

  setResults(null)
  setView("dashboard")
}

  const handleLiveEventSelect = (formData) => {
    setForm({ ...DEFAULT_FORM, ...formData })
    setResults(null)
    setView('dashboard')
    setTab('predict')
  }

  if (view === 'landing') {
    return (
      <>
        <Header setView={setView} />
        <LandingPage onScenarioSelect={handleScenarioSelect} onLiveFeedSelect={() => setView('live_feeds')} />
      </>
    )
  }

  if (view === 'live_feeds') {
    return (
      <>
        <Header setView={setView} />
        <LiveFeeds onEventSelect={handleLiveEventSelect} onBack={() => setView('landing')} />
      </>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50 font-sans overflow-hidden">
      {/* Taskbar / Navbar */}
      <div className="shrink-0 z-20 shadow-sm relative">
        <Header setView={setView} />
      </div>

      {/* ── Body ── */}
      <div className="flex-1 flex overflow-hidden">

        {/* LEFT SIDEBAR */}
        <aside className="w-96 bg-white border-r border-gray-200 overflow-y-auto flex flex-col shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
          {/* Tab nav */}
          <div className="p-6 pb-0">
            <div className="flex gap-1 bg-gray-100 p-1 rounded-xl shadow-inner">
              <button 
                className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all ${tab==='predict' ? 'bg-white text-blue-600 shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200/50'}`} 
                onClick={() => setTab('predict')}
              >
                🚦 Prediction
              </button>
              <button 
                className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all ${tab==='analytics' ? 'bg-white text-blue-600 shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200/50'}`} 
                onClick={() => setTab('analytics')}
              >
                📈 Analytics
              </button>
              <button 
                className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all ${tab==='feedback' ? 'bg-white text-blue-600 shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200/50'}`} 
                onClick={() => setTab('feedback')}
              >
                💬 Feedback
              </button>
            </div>
          </div>

          {tab === 'analytics' && <Analytics
              filters={appliedFilters}
              selectedGridId={selectedGridId}
              onClearCell={clearCell}
              selectedClusterId={selectedClusterId}
              onClearCluster={clearCluster}
            />}
          {tab === 'feedback'  && (
            <div className="p-6 text-sm text-gray-500 leading-relaxed font-semibold fade-in-up">
              Submit feedback to improve prediction accuracy and help retrain the machine learning model using real traffic events.
            </div>
          )}
          {tab === 'predict'  && (
            <div className="fade-in-up flex flex-col h-full">
              <SidebarForm 
                form={form} 
                setForm={setForm} 
                loading={loading} 
                submit={submit} 
                DEFAULT_FORM={DEFAULT_FORM}
                setResults={setResults} 
              />
              {error && (
                <div className="mx-6 mb-6 p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm flex gap-2">
                  <span>⚠️</span>{error}
                </div>
              )}
            </div>
          )}
        </aside>

        {/* RIGHT MAIN */}
        <main className="flex-1 bg-gray-50 overflow-y-auto flex flex-col">
          {tab === 'predict'   && <ResultsPanel results={results} />}
          {tab === 'feedback'  && <Feedback />}
          {tab === 'analytics' && (
            <div className="flex flex-col h-full">
              <div className="p-4 px-6 border-b border-gray-200 bg-white shrink-0">
                <div className="font-extrabold text-gray-900">Traffic Density Heatmap</div>
                <div className="text-xs text-gray-500 mt-1">
                Interactive traffic density map showing congestion hotspots across monitored regions.
                </div>
              </div>
              <div className="flex-1 min-h-0 overflow-hidden">
                <GridMap
                  appliedFilters={appliedFilters}
                  pendingFilters={pendingFilters}
                  setPendingFilters={setPending}
                  onApply={applyFilters}
                  onReset={resetAll}
                  selectedGridId={selectedGridId}
                  onCellSelect={selectCell}
                  selectedClusterId={selectedClusterId}
                  onClusterSelect={selectCluster}
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
