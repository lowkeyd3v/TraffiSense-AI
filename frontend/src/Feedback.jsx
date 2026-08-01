import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API, CAUSE_LABELS } from './constants'

export default function Feedback() {
  const [deployments, setDeployments] = useState([])
  const [loading, setLoading] = useState(false)
  const [resolvingId, setResolvingId] = useState(null)
  const [feedbackForm, setFeedbackForm] = useState({
    actual_duration: '',
    actual_personnel: '',
    actual_barricades: '',
    actual_congestion_radius: '',
    actual_delay: '',
    feedback_comments: ''
  })
  const [showToast, setShowToast] = useState(false)

  const fetchDeployments = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API}/api/deployments`)
      setDeployments(res.data)
    } catch (err) {
      console.error("Error fetching deployments", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDeployments()
  }, [])

  const startResolve = (d) => {
    setResolvingId(d.id)
    setFeedbackForm({
      actual_duration: d.predicted_duration ? Math.round(d.predicted_duration) : '',
      actual_personnel: d.personnel || '',
      actual_barricades: d.barricades || '',
      actual_congestion_radius: d.congestion_radius_meters ? Math.round(d.congestion_radius_meters) : '',
      actual_delay: d.commuter_delay_minutes ? Math.round(d.commuter_delay_minutes) : '',
      feedback_comments: ''
    })
  }

  const submitResolve = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        actual_duration: parseFloat(feedbackForm.actual_duration) || 0,
        actual_personnel: parseInt(feedbackForm.actual_personnel) || 0,
        actual_barricades: parseInt(feedbackForm.actual_barricades) || 0,
        actual_congestion_radius: parseFloat(feedbackForm.actual_congestion_radius) || 0,
        actual_delay: parseFloat(feedbackForm.actual_delay) || 0,
        feedback_comments: feedbackForm.feedback_comments
      }
      await axios.post(`${API}/api/deployments/${resolvingId}/resolve`, payload)
      setResolvingId(null)
      setShowToast(true)
      setTimeout(() => setShowToast(false), 3000)
      fetchDeployments()
    } catch (err) {
      console.error("Error resolving deployment", err)
      alert("Failed to submit feedback.")
    }
  }

  const activeDeps = deployments.filter(d => d.status === 'active')
  const resolvedDeps = deployments.filter(d => d.status === 'resolved')

  const thClass = "px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider"
  const tdClass = "px-6 py-4 whitespace-nowrap text-sm text-gray-600"

  return (
    <div className="p-8 flex flex-col gap-8 bg-gray-50 min-h-full">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Deployments Log & Feedback Loop</h2>
          <p className="text-sm font-semibold text-gray-500 mt-1">
            Review active deployment units and record post-event metrics to retrain AI routing and scale engines.
          </p>
        </div>
        <button 
          onClick={fetchDeployments} 
          disabled={loading}
          className="bg-white hover:bg-gray-100 text-gray-800 font-bold py-2 px-4 border border-gray-300 rounded-lg shadow-sm text-sm transition-all"
        >
          {loading ? 'Refreshing...' : '🔄 Refresh Log'}
        </button>
      </div>

      {/* Active Deployments */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
          <span className="font-extrabold text-gray-900 text-base">Active Field Deployments ({activeDeps.length})</span>
          <span className="w-2.5 h-2.5 bg-green-500 rounded-full animate-ping"></span>
        </div>
        {activeDeps.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">
            No active deployments. Deploy field units from the Predict panel map.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className={thClass}>Event</th>
                  <th className={thClass}>Location</th>
                  <th className={thClass}>Dispatched (Est.)</th>
                  <th className={thClass}>Est. Impact</th>
                  <th className={thClass}>Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activeDeps.map(d => (
                  <tr key={d.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-bold text-gray-900">{CAUSE_LABELS[d.event_cause] || d.event_cause}</div>
                      <div className="text-xs text-gray-500">{d.event_scale} scale · {d.event_type}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-semibold text-gray-800">{d.corridor}</div>
                      <div className="text-xs text-gray-500">{d.police_station} Station</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-700">👮 <span className="font-bold">{d.personnel}</span> Personnel</div>
                      <div className="text-xs text-gray-500">🚧 <span className="font-bold">{d.barricades}</span> Barricades</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-700">⏱️ <span className="font-bold">{d.predicted_duration ? Math.round(d.predicted_duration) : 0}</span> min</div>
                      <div className="text-xs text-gray-500">🔴 {d.congestion_radius_meters ? Math.round(d.congestion_radius_meters) : 0}m rad</div>
                    </td>
                    <td className="px-6 py-4">
                      <button 
                        onClick={() => startResolve(d)}
                        className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold py-1.5 px-3 rounded-lg shadow-sm transition-all"
                      >
                        Resolve Event
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Resolve Dialog */}
      {resolvingId && (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl border border-gray-100 max-w-lg w-full p-6 relative">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Record Post-Event Resolution Feedback</h3>
            <p className="text-xs text-gray-500 mb-4">Input actual observations to automatically retrain the Traffic Intelligence model.</p>
            <form onSubmit={submitResolve} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Actual Duration (minutes)</label>
                  <input 
                    type="number" required
                    value={feedbackForm.actual_duration}
                    onChange={e => setFeedbackForm({...feedbackForm, actual_duration: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Actual Personnel Used</label>
                  <input 
                    type="number" required
                    value={feedbackForm.actual_personnel}
                    onChange={e => setFeedbackForm({...feedbackForm, actual_personnel: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Actual Barricades</label>
                  <input 
                    type="number" required
                    value={feedbackForm.actual_barricades}
                    onChange={e => setFeedbackForm({...feedbackForm, actual_barricades: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Actual Radius (m)</label>
                  <input 
                    type="number" required
                    value={feedbackForm.actual_congestion_radius}
                    onChange={e => setFeedbackForm({...feedbackForm, actual_congestion_radius: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Actual Delay (min)</label>
                  <input 
                    type="number" required
                    value={feedbackForm.actual_delay}
                    onChange={e => setFeedbackForm({...feedbackForm, actual_delay: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Feedback Comments</label>
                <textarea 
                  rows="3"
                  value={feedbackForm.feedback_comments}
                  onChange={e => setFeedbackForm({...feedbackForm, feedback_comments: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="Note any specific operational challenges, weather conditions, or recommendations..."
                />
              </div>
              <div className="flex gap-3 justify-end pt-2">
                <button 
                  type="button" 
                  onClick={() => setResolvingId(null)}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-bold py-2 px-4 rounded-lg text-sm"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg text-sm shadow-sm"
                >
                  Submit & Retrain AI
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Historical Logs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 font-extrabold text-gray-900 text-base">
          Resolved Events & Retraining Log ({resolvedDeps.length})
        </div>
        {resolvedDeps.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">
            No resolved deployments yet. Submit resolution feedback on active events above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className={thClass}>Event Details</th>
                  <th className={thClass}>Prediction</th>
                  <th className={thClass}>Actual Performance</th>
                  <th className={thClass}>Feedback / Notes</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {resolvedDeps.map(d => (
                  <tr key={d.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-bold text-gray-900">{CAUSE_LABELS[d.event_cause] || d.event_cause}</div>
                      <div className="text-xs text-gray-500">{d.corridor} · {d.event_scale}</div>
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-500">
                      <div>⏱️ Duration: {Math.round(d.predicted_duration)}m</div>
                      <div>👮 Personnel: {d.personnel}</div>
                      <div>🚧 Barricades: {d.barricades}</div>
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-800 font-semibold">
                      <div>⏱️ Duration: {d.actual_duration}m</div>
                      <div>👮 Personnel: {d.actual_personnel}</div>
                      <div>🚧 Barricades: {d.actual_barricades}</div>
                      <div className="text-red-500">🔴 Rad: {d.actual_congestion_radius}m</div>
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-600 max-w-xs truncate">
                      {d.feedback_comments || <span className="text-gray-400">None</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 p-4 bg-white border border-green-200 rounded-xl shadow-lg animate-bounce">
          <span className="text-2xl">⚡</span>
          <div>
            <div className="font-bold text-gray-900 text-sm">Feedback Received!</div>
            <div className="text-xs text-gray-500 font-medium">Model retraining scheduled in the background.</div>
          </div>
        </div>
      )}
    </div>
  )
}
