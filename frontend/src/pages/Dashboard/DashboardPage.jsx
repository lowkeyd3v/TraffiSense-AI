import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import StatCard from '../../components/ui/StatCard';
import StatusBadge from '../../components/ui/StatusBadge';
import { trafficService } from '../../services/api';
import { Radio, AlertOctagon, Cpu, Activity, MapPin } from 'lucide-react';

const DashboardPage = () => {
  const [metrics, setMetrics] = useState({
    activeSignals: 142,
    congestionIndex: '64%',
    activeIncidents: 18,
    aiOptimizationScore: '92%',
  });
  const [incidents, setIncidents] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const liveMetrics = await trafficService.getRealtimeMetrics();
      const liveIncidents = await trafficService.getIncidents();
      setMetrics(liveMetrics);
      setIncidents(liveIncidents);
    };
    fetchData();
  }, []);

  return (
    <DashboardLayout title="Live Traffic Command Center">
      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard title="Active Signals" value={metrics.activeSignals} icon={Radio} change="98.5%" changeType="positive" description="Operational" />
        <StatCard title="Grid Congestion" value={metrics.congestionIndex} icon={Activity} change="-4.2%" changeType="positive" description="vs peak hour" />
        <StatCard title="Active Incidents" value={metrics.activeIncidents} icon={AlertOctagon} change="+2" changeType="negative" description="Requires Dispatch" />
        <StatCard title="AI Signal Optimization" value={metrics.aiOptimizationScore} icon={Cpu} change="+12%" changeType="positive" description="Efficiency Boost" />
      </div>

      {/* Main Panel Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map Panel (2 Cols) */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col h-[500px]">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold text-white flex items-center gap-2">
              <MapPin className="w-5 h-5 text-indigo-400" /> Live Grid Geographic Feed
            </h3>
            <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full">Live Simulation</span>
          </div>
          
          <div className="flex-1 bg-slate-950 border border-slate-800 rounded-xl relative overflow-hidden flex items-center justify-center">
            {/* Visual Grid Simulation Placeholder */}
            <div className="absolute inset-0 bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:16px_1px] opacity-40"></div>
            <div className="relative text-center z-10 p-6">
              <div className="w-16 h-16 bg-indigo-600/20 border border-indigo-500/30 rounded-full flex items-center justify-center mx-auto mb-3 animate-ping">
                <Radio className="w-8 h-8 text-indigo-400" />
              </div>
              <p className="text-slate-300 font-semibold text-sm">Grid Intersection Overlay Active</p>
              <p className="text-xs text-slate-500 mt-1">Monitoring 142 intersections in Sector 4-A</p>
            </div>
          </div>
        </div>

        {/* Live Incident Stream */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col h-[500px]">
          <h3 className="font-bold text-white mb-4 flex items-center justify-between">
            <span>Recent Incident Feeds</span>
            <span className="text-xs text-slate-400 font-normal">Real-time</span>
          </h3>

          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {incidents.map((incident) => (
              <div key={incident.id} className="p-3.5 bg-slate-950 border border-slate-800/80 rounded-xl hover:border-slate-700 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-mono text-indigo-400 font-semibold">{incident.id}</span>
                  <StatusBadge status={incident.status} />
                </div>
                <h4 className="text-sm font-semibold text-slate-200">{incident.type}</h4>
                <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-slate-500" /> {incident.location}
                </p>
                <div className="mt-2 flex justify-between items-center text-[10px] text-slate-500">
                  <span>Severity: <strong className="text-slate-300">{incident.severity}</strong></span>
                  <span>{incident.timestamp}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;