import React from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';

const SettingsPage = () => {
  return (
    <DashboardLayout title="System Settings & Config">
      <div className="max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
        <div>
          <h3 className="font-bold text-white mb-2">Automated Signal Modulation</h3>
          <p className="text-xs text-slate-400 mb-4">Allow AI engine to modify green phases autonomously.</p>
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" defaultChecked className="w-4 h-4 accent-indigo-600 rounded" />
            <span className="text-sm text-slate-200">Enable Autonomous Light Timing</span>
          </label>
        </div>

        <div className="border-t border-slate-800 pt-6">
          <h3 className="font-bold text-white mb-2">API Refresh Rate</h3>
          <p className="text-xs text-slate-400 mb-4">Set interval rate for live grid telemetry sync.</p>
          <select className="bg-slate-950 border border-slate-800 text-sm text-white rounded-lg p-2.5 w-64 focus:outline-none">
            <option>Every 5 Seconds</option>
            <option>Every 15 Seconds</option>
            <option>Every 30 Seconds</option>
          </select>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default SettingsPage;