import React from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import StatCard from '../../components/ui/StatCard';
import { BarChart3, TrendingUp, Clock, ShieldCheck } from 'lucide-react';

const AnalyticsPage = () => {
  return (
    <DashboardLayout title="Traffic Analytics & Insights">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <StatCard title="Avg Delay Time" value="4.2 mins" icon={Clock} change="-18%" changeType="positive" description="Citywide average" />
        <StatCard title="Peak Congestion" value="08:30 AM" icon={TrendingUp} description="Daily peak window" />
        <StatCard title="Traffic Flow Rate" value="4,820 v/h" icon={BarChart3} change="+8%" changeType="positive" description="Vehicles per hour" />
        <StatCard title="Safety Index" value="96.4/100" icon={ShieldCheck} change="+3.2%" changeType="positive" description="Incidents reduced" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="font-bold text-white mb-4">Congestion Trend (24h)</h3>
          <div className="h-64 bg-slate-950 border border-slate-800 rounded-xl flex items-end justify-between p-4 gap-2">
            {[40, 30, 20, 15, 25, 65, 90, 85, 60, 50, 55, 70, 95, 80, 60, 45].map((val, idx) => (
              <div key={idx} className="flex-1 bg-indigo-600/40 hover:bg-indigo-500 transition-all rounded-t-sm" style={{ height: `${val}%` }}></div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="font-bold text-white mb-4">Incident Category Breakdown</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Vehicle Collisions</span>
                <span>45%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-red-500 h-full w-[45%]"></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Signal / Hardware Failure</span>
                <span>30%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-amber-500 h-full w-[30%]"></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Road Obstructions / Debris</span>
                <span>25%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full w-[25%]"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AnalyticsPage;