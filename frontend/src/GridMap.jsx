import { useEffect, useRef, useState, useCallback } from 'react'
import axios from 'axios'
import { API } from './constants'

const MONTHS = ['All Months','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const HOUR_LABELS = Array.from({length:24}, (_,h) => h===0?'12am':h===12?'12pm':h<12?`${h}am`:`${h-12}pm`)

const CAUSE_LABELS = {
  vehicle_breakdown:'Vehicle Breakdown', water_logging:'Water Logging',
  accident:'Accident', vip_movement:'VIP Movement', construction:'Construction',
  road_conditions:'Road Conditions', tree_fall:'Tree Fall', pot_holes:'Pot Holes',
  congestion:'Congestion', procession:'Procession', others:'Others',
}

function densityColor(count, maxCount) {
  const r = Math.min(count / Math.max(maxCount,1), 1)
  if (r < 0.10) return ['#3b82f6', 0.30]
  if (r < 0.25) return ['#06b6d4', 0.40]
  if (r < 0.45) return ['#84cc16', 0.45]
  if (r < 0.65) return ['#f59e0b', 0.58]
  if (r < 0.82) return ['#ef4444', 0.68]
  return ['#dc2626', 0.82]
}

function DensityLegend({ maxCount }) {
  return (
    <div style={{background:'rgba(255,255,255,0.95)',backdropFilter:'blur(8px)',
      border:'1px solid #e5e7eb',borderRadius:10,padding:'10px 12px',boxShadow:'0 4px 6px rgba(0,0,0,0.05)'}}>
      <div style={{fontWeight:600,fontSize:'0.85rem',color:'#111827',marginBottom:6}}>Density (peak={maxCount})</div>
      {[['<10%','#3b82f6'],['10–25%','#06b6d4'],['25–45%','#84cc16'],['45–65%','#f59e0b'],['65–82%','#ef4444'],['>82%','#dc2626']].map(([l,c])=>(
        <div key={l} style={{display:'flex',alignItems:'center',gap:6,marginBottom:3}}>
          <div style={{width:16,height:8,borderRadius:2,background:c,opacity:0.85,border:'1px solid rgba(0,0,0,0.1)'}}/>
          <span style={{fontSize:'0.7rem',color:'#4b5563',fontWeight:500}}>{l}</span>
        </div>
      ))}
    </div>
  )
}

function ClusterLegend({ clusters }) {
  return (
    <div style={{background:'rgba(255,255,255,0.97)',backdropFilter:'blur(8px)',
      border:'1px solid #e5e7eb',borderRadius:10,padding:'10px 12px',
      boxShadow:'0 4px 6px rgba(0,0,0,0.05)',maxHeight:220,overflowY:'auto',minWidth:160}}>
      <div style={{fontWeight:700,fontSize:'0.8rem',color:'#111827',marginBottom:8}}>
        🔬 {clusters.length} DBSCAN Clusters
      </div>
      {clusters.slice(0,12).map((c,i) => (
        <div key={c.cluster_id} style={{display:'flex',alignItems:'center',gap:6,marginBottom:4}}>
          <div style={{width:12,height:12,borderRadius:'50%',background:c.color,flexShrink:0,border:'1px solid rgba(0,0,0,0.15)'}}/>
          <span style={{fontSize:'0.68rem',color:'#374151'}}>
            <b>#{i+1}</b> — {c.count} incidents
          </span>
        </div>
      ))}
      {clusters.length > 12 && (
        <div style={{fontSize:'0.65rem',color:'#9ca3af',marginTop:4}}>+{clusters.length - 12} more clusters</div>
      )}
    </div>
  )
}

export default function GridMap({
  appliedFilters, pendingFilters, setPendingFilters,
  onApply, onReset, selectedGridId, onCellSelect,
  selectedClusterId, onClusterSelect
}) {
  const mapRef    = useRef(null)
  const mapInst   = useRef(null)
  const layersRef = useRef([])

  const [viewMode, setViewMode]   = useState('grid')   // 'grid' | 'clusters'
  const [cells, setCells]         = useState([])
  const [maxCount, setMaxCount]   = useState(1)
  const [total, setTotal]         = useState(0)
  const [loading, setLoading]     = useState(false)

  const [clusters, setClusters]           = useState([])
  const [clustersLoading, setClustersLoading] = useState(false)
  // local highlight mirrors selectedClusterId from parent
  const [localHighlight, setLocalHighlight]   = useState(null)

  // Keep local highlight in sync with parent
  useEffect(() => { setLocalHighlight(selectedClusterId) }, [selectedClusterId])

  const isDirty = JSON.stringify(pendingFilters) !== JSON.stringify(appliedFilters)

  // ── Init Leaflet ───────────────────────────────────────────────────────────
  useEffect(() => {
    let id = null
    const tryInit = () => {
      if (!window.L || mapInst.current || !mapRef.current) return
      const { offsetWidth, offsetHeight } = mapRef.current
      if (!offsetWidth || !offsetHeight) return
      mapInst.current = window.L.map(mapRef.current, { center:[12.9716,77.5946], zoom:11 })
      window.L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        { attribution:'© OSM · CartoDB', maxZoom:19 }).addTo(mapInst.current)
      clearInterval(id)
    }
    id = setInterval(tryInit, 200)
    return () => clearInterval(id)
  }, [])

  // ── Fetch grid data ────────────────────────────────────────────────────────
  const fetchGrid = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await axios.get(`${API}/api/analytics/grid_density`, {
        params: { hour_start: appliedFilters.hourStart, hour_end: appliedFilters.hourEnd, month: appliedFilters.month }
      })
      setCells(data.cells || [])
      setMaxCount(data.max_count || 1)
      setTotal(data.total_filtered || 0)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [appliedFilters])

  useEffect(() => { fetchGrid() }, [fetchGrid])

  // ── Fetch clusters ─────────────────────────────────────────────────────────
  const fetchClusters = useCallback(async () => {
    setClustersLoading(true)
    try {
      const { data } = await axios.get(`${API}/api/analytics/clusters`, {
        params: {
          hour_start: appliedFilters.hourStart,
          hour_end:   appliedFilters.hourEnd,
          month:      appliedFilters.month,
        }
      })
      setClusters(data.clusters || [])
    } catch (e) { console.error(e) }
    finally { setClustersLoading(false) }
  }, [appliedFilters])

  useEffect(() => {
    if (viewMode === 'clusters') fetchClusters()
  }, [viewMode, fetchClusters])

  // ── Clear all map layers ───────────────────────────────────────────────────
  const clearLayers = () => {
    layersRef.current.forEach(l => l.remove())
    layersRef.current = []
  }

  // ── Draw grid rectangles ───────────────────────────────────────────────────
  useEffect(() => {
    if (!mapInst.current || !window.L || viewMode !== 'grid') return
    clearLayers()
    cells.forEach(cell => {
      const [fill, opacity] = densityColor(cell.count, maxCount)
      const isSelected = cell.grid_id === selectedGridId
      const rect = window.L.rectangle(
        [[cell.lat_min, cell.lng_min],[cell.lat_max, cell.lng_max]],
        {
          fillColor:   fill,
          fillOpacity: isSelected ? Math.min(opacity + 0.2, 1) : opacity,
          color:       isSelected ? '#ffffff' : 'rgba(255,255,255,0.15)',
          weight:      isSelected ? 2.5 : 0.5,
          opacity:     isSelected ? 1 : 0.7,
        }
      )
      rect.bindTooltip(
        `<div style="font-weight:800;font-size:13px;">${cell.count}</div><div style="font-size:10px;opacity:0.75;">incidents</div>`,
        { sticky: true, direction: 'top', opacity: 1, className: 'leaflet-grid-tooltip' }
      )
      rect.on('click', () => onCellSelect(isSelected ? null : cell.grid_id))
      rect.addTo(mapInst.current)
      layersRef.current.push(rect)
    })
  }, [cells, maxCount, selectedGridId, viewMode])

  // ── Draw DBSCAN cluster polygons ───────────────────────────────────────────
  useEffect(() => {
    if (!mapInst.current || !window.L || viewMode !== 'clusters') return
    clearLayers()

    clusters.forEach((cluster, idx) => {
      if (!cluster.hull || cluster.hull.length < 3) return
      const isSelected = localHighlight === cluster.cluster_id

      // Draw convex hull polygon
      const polygon = window.L.polygon(cluster.hull, {
        fillColor:   cluster.color,
        fillOpacity: isSelected ? 0.45 : 0.22,
        color:       cluster.color,
        weight:      isSelected ? 3 : 1.5,
        opacity:     isSelected ? 1 : 0.7,
        dashArray:   isSelected ? null : '4 4',
      })

      // Popup with cluster stats
      const causeList = Object.entries(cluster.cause_breakdown)
        .map(([cause, n]) => `<div style="display:flex;justify-content:space-between;gap:12px"><span>${CAUSE_LABELS[cause]||cause}</span><b>${n}</b></div>`)
        .join('')

      polygon.bindPopup(`
        <div style="min-width:200px;font-family:Inter,sans-serif">
          <div style="font-weight:800;font-size:1rem;margin-bottom:6px;color:${cluster.color}">
            Cluster #${idx + 1}
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:8px">
            <div style="background:#f3f4f6;border-radius:6px;padding:6px 8px">
              <div style="font-size:0.65rem;color:#6b7280">Incidents</div>
              <div style="font-weight:800;font-size:1.1rem">${cluster.count}</div>
            </div>
            <div style="background:#f3f4f6;border-radius:6px;padding:6px 8px">
              <div style="font-size:0.65rem;color:#6b7280">Avg Duration</div>
              <div style="font-weight:800;font-size:1.1rem">${cluster.avg_duration != null ? cluster.avg_duration + ' min' : 'N/A'}</div>
            </div>
            <div style="background:#f3f4f6;border-radius:6px;padding:6px 8px">
              <div style="font-size:0.65rem;color:#6b7280">High Priority</div>
              <div style="font-weight:800;font-size:1.1rem;color:#ef4444">${cluster.high_priority_pct}%</div>
            </div>
            <div style="background:#f3f4f6;border-radius:6px;padding:6px 8px">
              <div style="font-size:0.65rem;color:#6b7280">Road Closures</div>
              <div style="font-weight:800;font-size:1.1rem;color:#f97316">${cluster.road_closure_pct}%</div>
            </div>
          </div>
          <div style="font-size:0.72rem;color:#374151;font-weight:600;margin-bottom:4px">Cause Breakdown</div>
          <div style="font-size:0.72rem;color:#4b5563">${causeList}</div>
          <div style="margin-top:6px;font-size:0.65rem;color:#9ca3af">
            Radius ~${cluster.radius_km} km · Centre ${cluster.center_lat.toFixed(4)}°N, ${cluster.center_lng.toFixed(4)}°E
          </div>
        </div>
      `, { maxWidth: 260 })

      // Centroid marker
      const marker = window.L.circleMarker([cluster.center_lat, cluster.center_lng], {
        radius:      isSelected ? 10 : 7,
        fillColor:   cluster.color,
        fillOpacity: 0.95,
        color:       '#fff',
        weight:      2,
      })
      marker.bindTooltip(
        `<b style="font-size:12px">Cluster #${idx+1}</b><br/><span style="font-size:11px">${cluster.count} incidents · top: ${CAUSE_LABELS[cluster.top_cause]||cluster.top_cause}</span>`,
        { sticky: true, direction: 'top', opacity: 1, className: 'leaflet-grid-tooltip' }
      )

      const onClickCluster = () => {
        const newId = localHighlight === cluster.cluster_id ? null : cluster.cluster_id
        setLocalHighlight(newId)
        onClusterSelect && onClusterSelect(newId)   // bubble up to App → Analytics
      }
      polygon.on('click', onClickCluster)
      marker.on('click', onClickCluster)

      polygon.addTo(mapInst.current)
      marker.addTo(mapInst.current)
      layersRef.current.push(polygon, marker)
    })
  }, [clusters, viewMode, localHighlight, onClusterSelect])

  // ── Switch views: reset selection when toggling ────────────────────────────
  useEffect(() => {
    if (!mapInst.current) return
    onClusterSelect && onClusterSelect(null)
  }, [viewMode, onClusterSelect])

  return (
    <div style={{display:'flex',flexDirection:'column',height:'100%',minHeight:0}}>

      {/* Leaflet tooltip dark style */}
      <style>{`
        .leaflet-grid-tooltip {
          background: rgba(10,14,26,0.92) !important;
          border: 1px solid rgba(255,255,255,0.15) !important;
          color: #f1f5f9 !important;
          border-radius: 8px !important;
          padding: 6px 10px !important;
          text-align: center !important;
          box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
          font-family: Inter, sans-serif !important;
        }
        .leaflet-grid-tooltip::before { display: none !important; }
        .leaflet-popup-content-wrapper {
          border-radius: 12px !important;
          box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
          font-family: Inter, sans-serif !important;
        }
        .leaflet-popup-content { margin: 14px 16px !important; }
      `}</style>

      {/* ── Filter / Control Bar ── */}
      <div style={{padding:'10px 16px',flexShrink:0,background:'#ffffff',
        borderBottom:'1px solid #e5e7eb',
        display:'flex',gap:16,alignItems:'center',flexWrap:'wrap',color:'#374151'}}>

        {/* View mode toggle */}
        <div style={{display:'flex',background:'#f3f4f6',borderRadius:8,padding:3,gap:2,flexShrink:0}}>
          {[['grid','🔲 Grid Density'],['clusters','🔬 Cluster View']].map(([mode,label]) => (
            <button key={mode} onClick={() => setViewMode(mode)}
              style={{
                padding:'5px 12px', fontSize:'0.78rem', fontWeight:600, borderRadius:6, cursor:'pointer',
                background: viewMode===mode ? '#fff' : 'transparent',
                color: viewMode===mode ? '#3b82f6' : '#6b7280',
                boxShadow: viewMode===mode ? '0 1px 4px rgba(0,0,0,0.1)' : 'none',
                border:'none', transition:'all 0.15s'
              }}>{label}</button>
          ))}
        </div>

        {/* Hour range sliders */}
        <div style={{display:'flex',flexDirection:'column',gap:4,minWidth:220}}>
          <div style={{fontWeight:600,fontSize:'0.85rem',color:'#111827'}}>
            Hour: {HOUR_LABELS[pendingFilters.hourStart]} — {HOUR_LABELS[pendingFilters.hourEnd]}
            {isDirty && <span style={{marginLeft:6,color:'#f59e0b',fontSize:'0.65rem'}}>● unsaved</span>}
          </div>
          <div style={{display:'flex',gap:8,alignItems:'center'}}>
            <input type="range" min={0} max={23} value={pendingFilters.hourStart}
              onChange={e => setPendingFilters(f=>({...f, hourStart:Number(e.target.value)}))}
              style={{flex:1,accentColor:'#3b82f6'}}/>
            <span style={{fontSize:'0.65rem',color:'#9ca3af'}}>—</span>
            <input type="range" min={0} max={23} value={pendingFilters.hourEnd}
              onChange={e => setPendingFilters(f=>({...f, hourEnd:Number(e.target.value)}))}
              style={{flex:1,accentColor:'#8b5cf6'}}/>
          </div>
        </div>

        {/* Month */}
        <div style={{display:'flex',flexDirection:'column',gap:4}}>
          <div style={{fontWeight:600,fontSize:'0.85rem',color:'#111827'}}>Month</div>
          <select value={pendingFilters.month}
            onChange={e => setPendingFilters(f=>({...f, month:Number(e.target.value)}))}
            className="border border-gray-300 rounded cursor-pointer hover:border-gray-400"
            style={{width:128,fontSize:'0.8rem',padding:'5px 10px',background:'#f9fafb',color:'#111827'}}>
            {MONTHS.map((m,i)=><option key={i} value={i}>{m}</option>)}
          </select>
        </div>

        {/* Action buttons */}
        <div style={{display:'flex',gap:8,alignItems:'center'}}>
          <button onClick={onReset} className="text-gray-600 hover:text-gray-900 transition-colors"
            style={{fontSize:'0.78rem',padding:'7px 14px',fontWeight:600,cursor:'pointer'}}>
            ↺ Reset All
          </button>
          <button onClick={onApply} disabled={!isDirty && !loading && !clustersLoading}
            className="rounded text-white transition-opacity font-semibold cursor-pointer"
            style={{fontSize:'0.78rem',padding:'7px 14px',opacity:isDirty?1:0.6,
              background:isDirty?'#3b82f6':'#9ca3af'}}>
            {loading || clustersLoading ? '…' : isDirty ? '⚡ Load' : '✓ Loaded'}
          </button>
        </div>

        {/* Cluster info badge */}
        {viewMode === 'clusters' && (
          <div style={{fontSize:'0.78rem',color:'#4b5563',display:'flex',alignItems:'center',gap:6}}>
            {clustersLoading
              ? <><span style={{width:10,height:10,borderRadius:'50%',border:'2px solid #e5e7eb',borderTopColor:'#3b82f6',display:'inline-block',animation:'spin 0.8s linear infinite'}}/>Running DBSCAN…</>
              : <><span style={{color:'#10b981',fontWeight:700}}>✓</span> {clusters.length} clusters discovered · Click any cluster for details</>
            }
          </div>
        )}

        {/* Stats */}
        {viewMode === 'grid' ? (
          <div style={{fontSize:'0.72rem',color:'#6b7280',borderLeft:'1px solid #e5e7eb',paddingLeft:12,marginLeft:'auto'}}>
            <span style={{fontWeight:700,color:'#111827'}}>{total.toLocaleString()}</span> events
            {' · '}
            <span style={{fontWeight:700,color:'#3b82f6'}}>{cells.length}</span> cells
          </div>
        ) : (
          <div style={{fontSize:'0.72rem',color:'#6b7280',borderLeft:'1px solid #e5e7eb',paddingLeft:12,marginLeft:'auto'}}>
            <span style={{fontWeight:700,color:'#111827'}}>{clusters.length}</span> clusters
          </div>
        )}
      </div>

      {/* ── Map ── */}
      <div style={{flex:1,position:'relative',minHeight:400}}>
        <div ref={mapRef} style={{width:'100%',height:'100%',minHeight:400}}/>

        {/* Legend */}
        <div style={{position:'absolute',bottom:20,left:12,zIndex:1000,pointerEvents:'none'}}>
          {viewMode === 'grid'
            ? <DensityLegend maxCount={maxCount}/>
            : clusters.length > 0 && <ClusterLegend clusters={clusters}/>
          }
        </div>

        {/* Selected cell indicator (grid mode) */}
        {viewMode === 'grid' && selectedGridId && (
          <div style={{
            position:'absolute',top:10,left:'50%',transform:'translateX(-50%)',
            zIndex:1000,pointerEvents:'none',
            background:'rgba(59,130,246,0.9)',borderRadius:20,
            padding:'5px 14px',fontSize:'0.75rem',fontWeight:700,color:'#fff',
            boxShadow:'0 4px 16px rgba(59,130,246,0.4)',
          }}>
            📍 Cell selected — see sidebar for stats
          </div>
        )}

        {/* DBSCAN banner (cluster mode) */}
        {viewMode === 'clusters' && !clustersLoading && clusters.length > 0 && (
          <div style={{
            position:'absolute',top:10,left:'50%',transform:'translateX(-50%)',
            zIndex:1000,pointerEvents:'none',
            background:'rgba(16,185,129,0.9)',borderRadius:20,
            padding:'5px 14px',fontSize:'0.75rem',fontWeight:700,color:'#fff',
            boxShadow:'0 4px 16px rgba(16,185,129,0.3)',whiteSpace:'nowrap',
          }}>
            🔬 DBSCAN — {clusters.length} spatial risk zones auto-discovered from {clusters.reduce((a,c)=>a+c.count,0).toLocaleString()} incidents
          </div>
        )}

        {(loading || clustersLoading) && (
          <div style={{position:'absolute',top:10,right:10,zIndex:1000,
            background:'rgba(10,14,26,0.85)',borderRadius:8,padding:'6px 12px',
            fontSize:'0.75rem',color:'#e2e8f0',display:'flex',gap:6,alignItems:'center'}}>
            <span style={{width:12,height:12,border:'2px solid rgba(255,255,255,0.15)',borderTopColor:'#3b82f6',borderRadius:'50%',display:'inline-block'}}/>
            {clustersLoading ? 'Running DBSCAN…' : 'Computing…'}
          </div>
        )}
      </div>
    </div>
  )
}
