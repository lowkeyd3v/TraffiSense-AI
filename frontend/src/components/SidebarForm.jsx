import React from 'react'
import { EVENT_CAUSES, VEH_TYPES, CORRIDORS, CAUSE_LABELS } from '../constants'

export default function SidebarForm({ form, setForm, loading, submit, DEFAULT_FORM, setResults }) {
  const set = (k,v) => setForm(f=>({...f,[k]:v}))
  const handle = e => set(e.target.name, e.target.value)

  const labelClass = "block text-[0.65rem] font-extrabold text-fk-blue uppercase tracking-widest mb-1.5"
  const inputClass = "w-full rounded-xl border-2 border-gray-100 bg-white hover:border-gray-200 text-gray-900 font-medium text-sm p-3 focus:outline-none focus:border-fk-blue focus:ring-0 transition-colors shadow-sm"

  return (
    <form onSubmit={submit} className="p-8 flex flex-col gap-6 flex-1 bg-white">
      
      <div className="flex bg-gray-50 p-1.5 rounded-2xl border border-gray-100">
        {['unplanned','planned'].map(t=>(
          <button key={t} type="button" className={`flex-1 py-2 text-sm font-extrabold rounded-xl transition-all ${form.event_type===t ? 'bg-white text-fk-blue shadow-sm border border-gray-200' : 'text-gray-400 hover:text-gray-800'}`}
            onClick={()=>set('event_type',t)}>
            {t==='unplanned'?'🔴 Unplanned':'📅 Planned'}
          </button>
        ))}
      </div>

      <div>
        <label className={labelClass}>Event Cause</label>
        <select name="event_cause" value={form.event_cause} onChange={handle} className={inputClass}>
          {EVENT_CAUSES.map(c=><option key={c} value={c}>{CAUSE_LABELS[c]||c}</option>)}
        </select>
      </div>

      <div>
        <label className={labelClass}>Corridor</label>
        <select name="corridor" value={form.corridor} onChange={handle} className={inputClass}>
          {CORRIDORS.map(c=><option key={c}>{c}</option>)}
        </select>
      </div>

      <div>
        <label className={labelClass}>Priority</label>
        <div className="flex gap-2">
          {['Low','Medium','High'].map(p=>(
            <button key={p} type="button"
              className={`flex-1 py-2.5 text-sm font-extrabold rounded-xl border-2 transition-all ${form.priority===p ? 'bg-fk-yellow border-fk-yellow text-gray-900 shadow-sm' : 'bg-white border-gray-100 text-gray-400 hover:bg-gray-50 hover:text-gray-800'}`}
              onClick={()=>set('priority',p)}>{p}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className={labelClass}>Vehicle Type</label>
        <select name="veh_type" value={form.veh_type} onChange={handle} className={inputClass}>
          {VEH_TYPES.map(v=><option key={v} value={v}>{v.replace(/_/g,' ')}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Latitude</label>
          <input name="latitude" type="number" step="any" value={form.latitude} onChange={handle} className={inputClass}/>
        </div>
        <div>
          <label className={labelClass}>Longitude</label>
          <input name="longitude" type="number" step="any" value={form.longitude} onChange={handle} className={inputClass}/>
        </div>
      </div>

      <div>
        <label className={labelClass}>Event Time</label>
        <input type="datetime-local" name="time" value={form.time} onChange={handle} className={inputClass}/>
      </div>

      <div>
        <label className={labelClass}>Police Station</label>
        <input name="police_station" value={form.police_station} onChange={handle}
          placeholder="e.g. Cubbon Park" className={inputClass}/>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Event Scale</label>
          <select name="event_scale" value={form.event_scale} onChange={handle} className={inputClass}>
            <option value="Small">Small Event</option>
            <option value="Medium">Medium Event</option>
            <option value="Large">Large Event</option>
          </select>
        </div>
        <div>
          <label className={labelClass}>Crowd Size</label>
          <input name="crowd_size" type="number" value={form.crowd_size || ''}
            onChange={e=>set('crowd_size', parseInt(e.target.value) || 0)} className={inputClass} placeholder="Est."/>
        </div>
      </div>

      <label className="flex items-center gap-3 cursor-pointer select-none bg-blue-50/50 p-4 rounded-xl border border-blue-100/50 hover:bg-blue-50 transition-colors">
        <input type="checkbox" checked={form.requires_road_closure}
          onChange={e=>set('requires_road_closure',e.target.checked)}
          className="w-5 h-5 text-fk-blue rounded border-gray-300 focus:ring-fk-blue" />
        <span className="text-sm font-extrabold text-fk-blue">Requires Road Closure</span>
      </label>

      <div>
        <label className={labelClass}>Description</label>
        <textarea name="description" value={form.description} onChange={handle}
          placeholder="Describe the incident…" className={`${inputClass} min-h-[100px] resize-y`}/>
      </div>

      <button type="submit" disabled={loading} className="w-full bg-fk-blue hover:bg-blue-700 text-white font-black text-lg py-4 rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2 mt-4 disabled:opacity-50 disabled:cursor-not-allowed">
        {loading
          ? <>
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              Analyzing…
            </>
          : '⚡ Generate Intelligence'
        }
      </button>
    </form>
  )
}
