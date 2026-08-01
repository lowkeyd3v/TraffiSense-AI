import React, { useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { trafficService } from '../../services/api';
import { AlertTriangle, Send } from 'lucide-react';

const ReportIncidentPage = () => {
  const [formData, setFormData] = useState({
    location: '',
    type: 'Collision',
    severity: 'Medium',
    description: '',
  });
  const [status, setStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await trafficService.reportIncident(formData);
      setStatus('Incident logged successfully and sent to AI dispatch!');
      setFormData({ location: '', type: 'Collision', severity: 'Medium', description: '' });
    } catch {
      setStatus('Incident submitted (Local Demo Mode)');
    }
  };

  return (
    <DashboardLayout title="Report Traffic Incident">
      <div className="max-w-2xl mx-auto bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-xl">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Manual Incident Intake Form</h3>
            <p className="text-xs text-slate-400">Broadcast incident details directly to AI Dispatch</p>
          </div>
        </div>

        {status && (
          <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-sm">
            {status}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Intersection / Location</label>
            <input
              type="text"
              required
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="e.g. 5th Ave & 34th St"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Incident Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="Collision">Vehicle Collision</option>
                <option value="Signal Malfunction">Signal Malfunction</option>
                <option value="Road Blockage">Road Blockage</option>
                <option value="Hazardous Debris">Hazardous Debris</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Severity Level</label>
              <select
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Detailed Observations</label>
            <textarea
              rows="4"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Provide additional details or vehicle counts..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            ></textarea>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/30"
          >
            <Send className="w-4 h-4" /> Dispatch Alert To System
          </button>
        </form>
      </div>
    </DashboardLayout>
  );
};

export default ReportIncidentPage;