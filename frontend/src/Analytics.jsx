import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { API, CAUSE_LABELS } from './constants'

const COLORS = ['#3b82f6','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#f97316','#ec4899','#14b8a6','#6366f1']
const HOUR_LABELS = Array.from({length:24}, (_,h) => h===0?'12am':h===12?'12pm':h<12?`${h}am`:`${h-12}pm`)

export default function Analytics({ filters, selectedGridId, onClearCell, selectedClusterId, onClearCluster }) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      let res
      if (selectedClusterId != null) {
        // Fetch per-cluster analytics
        res = await axios.get(`${API}/api/analytics/cluster_summary/${selectedClusterId}`)
      } else {
        // Fetch global / grid-cell analytics
        res = await axios.get(`${API}/api/analytics/summary`, {
          params: {
            hour_start: filters.hourStart,
            hour_end:   filters.hourEnd,
            month:      filters.month,
            grid_id:    selectedGridId || '',
          }
        })
      }
      setData(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [filters, selectedGridId, selectedClusterId])

  useEffect(() => { fetchData() }, [fetchData])

  if (!data) {
    return (
      <div style={{padding:'20px',color:'#9ca3af',fontSize:'0.8rem'}}>
        Loading analytics…
      </div>
    )
  }

  if (data.error) {
    return (
      <div style={{padding:'20px 24px', display:'flex', flexDirection:'column', gap:10, color:'#374151'}}>
        <div style={{fontWeight:700,color:'#ef4444'}}>Error Loading Analytics</div>
        <div style={{fontSize:'0.82rem',color:'#6b7280'}}>{data.error}</div>
        <button onClick={() => { onClearCluster && onClearCluster(); onClearCell && onClearCell(); }} 
          style={{alignSelf:'flex-start',padding:'6px 12px',background:'#3b82f6',color:'#fff',border:'none',borderRadius:6,fontWeight:600,cursor:'pointer',fontSize:'0.75rem'}}>
          Back to Global view
        </button>
      </div>
    )
  }

  const { overview, causes, hotspots, zones, hour_distribution, is_filtered, cell_info, cluster_info } = data
  const maxCause = Math.max(...(causes ? causes.map(c => c.count) : []), 1)
  const maxZone  = Math.max(...(zones ? zones.map(z => z.total) : []), 1)
  const hourData = hour_distribution ? hour_distribution.map((c,h) => ({ h: HOUR_LABELS[h], count: c })) : []

  return (
    <div style={{padding:'16px 18px', display:'flex', flexDirection:'column', gap:14, overflowY:'auto'}}>

      {/* ── Cluster banner ── */}
      {cluster_info && (
        <div style={{
          background: cluster_info.color + '18',
          border: `1.5px solid ${cluster_info.color}55`,
          borderRadius:10, padding:'10px 14px',
          display:'flex', justifyContent:'space-between', alignItems:'center'
        }}>
          <div>
            <div style={{fontSize:'0.78rem',fontWeight:800,color: cluster_info.color, display:'flex', alignItems:'center', gap:6}}>
              <span style={{width:10,height:10,borderRadius:'50%',background:cluster_info.color,display:'inline-block'}}/>
              🔬 Cluster #{cluster_info.rank} — DBSCAN Zone
            </div>
            <div style={{fontSize:'0.68rem',color:'#6b7280',marginTop:2}}>
              {cluster_info.center_lat.toFixed(4)}°N · {cluster_info.center_lng.toFixed(4)}°E · Top cause: <b>{CAUSE_LABELS[cluster_info.top_cause]||cluster_info.top_cause}</b>
            </div>
          </div>
          <button onClick={onClearCluster} style={{
            background:'#f3f4f6', border:'1px solid #e5e7eb',
            color:'#374151', borderRadius:6, padding:'4px 10px',
            cursor:'pointer', fontSize:'0.72rem', fontWeight:700,
          }}>✕ Clear</button>
        </div>
      )}

      {/* ── Grid cell banner ── */}
      {cell_info && !cluster_info && (
        <div style={{background:'rgba(59,130,246,0.08)',border:'1px solid rgba(59,130,246,0.25)',
          borderRadius:10,padding:'8px 12px',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <div>
            <div style={{fontSize:'0.75rem',fontWeight:700,color:'#3b82f6'}}>📍 Grid Cell View</div>
            <div style={{fontSize:'0.68rem',color:'#9ca3af',marginTop:1}}>
              {cell_info.center_lat.toFixed(4)}°N · {cell_info.center_lng.toFixed(4)}°E
            </div>
          </div>
          <button onClick={onClearCell} style={{
            background:'#f3f4f6',border:'1px solid #e5e7eb',
            color:'#374151',borderRadius:6,padding:'4px 10px',
            cursor:'pointer',fontSize:'0.72rem',fontWeight:700,
          }}>✕ Clear</button>
        </div>
      )}

      {/* ── Time filter banner ── */}
      {is_filtered && !cell_info && !cluster_info && (
        <div style={{background:'rgba(139,92,246,0.08)',border:'1px solid rgba(139,92,246,0.25)',
          borderRadius:10,padding:'8px 12px',fontSize:'0.72rem',color:'#7c3aed',fontWeight:600}}>
          ⏱ Showing filtered period only
        </div>
      )}

      {/* ── Overview KPIs ── */}
      <div>
        <div style={{fontSize:'0.7rem',fontWeight:700,color:'#6b7280',letterSpacing:'0.06em',textTransform:'uppercase',marginBottom:8}}>
          {cluster_info ? `Cluster #${cluster_info.rank} Summary` : cell_info ? 'Cell Summary' : 'Overview'}
          {loading && <span style={{marginLeft:8,color:'#9ca3af',fontWeight:400,textTransform:'none'}}>Updating…</span>}
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
          {[
            { label:'Events',        value: overview.total_events.toLocaleString(), color:'#3b82f6' },
            { label:'Active',        value: overview.active_events,                 color:'#10b981' },
            { label:'High Priority', value: overview.high_priority.toLocaleString(),color:'#ef4444' },
            { label:'Road Closures', value: overview.road_closures,                 color:'#f59e0b' },
          ].map(k => (
            <div key={k.label} style={{background:'#f9fafb',border:'1px solid #e5e7eb',borderRadius:10,padding:'12px 14px'}}>
              <div style={{fontSize:'0.65rem',color:'#9ca3af',fontWeight:600,textTransform:'uppercase',letterSpacing:'0.04em',marginBottom:4}}>{k.label}</div>
              <div style={{fontSize:'1.5rem',fontWeight:900,color:k.color,lineHeight:1}}>{k.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Events by Cause ── */}
      <div style={{background:'#f9fafb',border:'1px solid #e5e7eb',borderRadius:10,padding:'14px 16px'}}>
        <div style={{fontSize:'0.7rem',fontWeight:700,color:'#6b7280',letterSpacing:'0.06em',textTransform:'uppercase',marginBottom:10}}>Events by Cause</div>
        <div style={{display:'flex',flexDirection:'column',gap:6}}>
          {causes.map((c,i) => (
            <div key={c.cause} style={{display:'flex',alignItems:'center',gap:8}}>
              <div style={{width:100,fontSize:'0.68rem',color:'#6b7280',textAlign:'right',flexShrink:0,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
                {CAUSE_LABELS[c.cause]||c.cause}
              </div>
              <div style={{flex:1,height:6,background:'#e5e7eb',borderRadius:3,overflow:'hidden'}}>
                <div style={{height:'100%',width:`${c.count/maxCause*100}%`,background:COLORS[i%COLORS.length],borderRadius:3}}/>
              </div>
              <div style={{width:32,fontSize:'0.7rem',fontWeight:700,color:'#111827',flexShrink:0,textAlign:'right'}}>{c.count}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Peak Hours ── */}
      <div style={{background:'#f9fafb',border:'1px solid #e5e7eb',borderRadius:10,padding:'14px 16px'}}>
        <div style={{fontSize:'0.7rem',fontWeight:700,color:'#6b7280',letterSpacing:'0.06em',textTransform:'uppercase',marginBottom:8}}>Peak Hours</div>
        <ResponsiveContainer width="100%" height={90}>
          <BarChart data={hourData} margin={{top:0,right:0,left:-24,bottom:0}}>
            <XAxis dataKey="h" tick={{fontSize:8,fill:'#9ca3af'}} interval={5}/>
            <YAxis tick={{fontSize:8,fill:'#9ca3af'}}/>
            <Tooltip contentStyle={{background:'#fff',border:'1px solid #e5e7eb',borderRadius:8,fontSize:11}}/>
            <Bar dataKey="count" radius={[2,2,0,0]}>
              {hourData.map((d,i) => (
                <Cell key={i} fill={d.count > 80 ? '#ef4444' : d.count > 40 ? '#f59e0b' : '#3b82f6'}/>
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Junction Hotspots ── */}
      {hotspots.length > 0 && (
        <div style={{background:'#f9fafb',border:'1px solid #e5e7eb',borderRadius:10,padding:'14px 16px'}}>
          <div style={{fontSize:'0.7rem',fontWeight:700,color:'#6b7280',letterSpacing:'0.06em',textTransform:'uppercase',marginBottom:8}}>Junction Hotspots</div>
          {hotspots.map(h => (
            <div key={h.junction} style={{display:'flex',alignItems:'center',gap:8,marginBottom:8}}>
              <div style={{
                background: h.rank<=3 ? ['#fef3c722','#f1f5f922','#fef9c322'][h.rank-1] : '#f3f4f6',
                color: h.rank<=3 ? ['#d97706','#64748b','#a16207'][h.rank-1] : '#9ca3af',
                width:26,height:26,borderRadius:7,display:'flex',alignItems:'center',justifyContent:'center',
                fontSize:'0.7rem',fontWeight:800,flexShrink:0,border:'1px solid #e5e7eb'
              }}>#{h.rank}</div>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontSize:'0.75rem',fontWeight:600,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',color:'#111827'}}>{h.junction}</div>
                <div style={{height:4,background:'#e5e7eb',borderRadius:2,marginTop:3,overflow:'hidden'}}>
                  <div style={{height:'100%',width:`${h.count/hotspots[0].count*100}%`,background:'#3b82f6',borderRadius:2}}/>
                </div>
              </div>
              <div style={{fontSize:'0.78rem',fontWeight:800,flexShrink:0,color:'#111827'}}>{h.count}</div>
            </div>
          ))}
        </div>
      )}

      {/* ── Zone Summary ── */}
      {zones.length > 0 && (
        <div style={{background:'#f9fafb',border:'1px solid #e5e7eb',borderRadius:10,padding:'14px 16px'}}>
          <div style={{fontSize:'0.7rem',fontWeight:700,color:'#6b7280',letterSpacing:'0.06em',textTransform:'uppercase',marginBottom:8}}>Zone Summary</div>
          {zones.map(z => {
            const hiPct = z.total ? Math.round(z.high_priority/z.total*100) : 0
            return (
              <div key={z.zone} style={{paddingBottom:8,marginBottom:8,borderBottom:'1px solid #e5e7eb'}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:3}}>
                  <span style={{fontSize:'0.75rem',fontWeight:600,color:'#111827'}}>{z.zone}</span>
                  <span style={{fontSize:'0.68rem',color:'#9ca3af'}}>{z.total} events</span>
                </div>
                <div style={{display:'flex',gap:8,alignItems:'center'}}>
                  <div style={{flex:1,height:5,background:'#e5e7eb',borderRadius:3,overflow:'hidden'}}>
                    <div style={{height:'100%',width:`${z.total/maxZone*100}%`,background:'#3b82f6',borderRadius:3}}/>
                  </div>
                  <span style={{fontSize:'0.65rem',color:'#ef4444',width:42,textAlign:'right',flexShrink:0,fontWeight:600}}>{hiPct}% Hi-Pri</span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
