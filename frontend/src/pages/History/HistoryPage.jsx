import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import StatusBadge from '../../components/ui/StatusBadge';
import { trafficService } from '../../services/api';
import { Search } from 'lucide-react';

const HistoryPage = () => {
  const [incidents, setIncidents] = useState([]);

  useEffect(() => {
    trafficService.getIncidents().then(setIncidents);
  }, []);

  return (
    <DashboardLayout title="Incident History Log">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-6">
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by Incident ID or location..."
              className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Incident ID</th>
                <th className="py-3.5 px-4">Type</th>
                <th className="py-3.5 px-4">Location</th>
                <th className="py-3.5 px-4">Severity</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {incidents.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/40">
                  <td className="py-3.5 px-4 font-mono text-indigo-400 font-medium">{item.id}</td>
                  <td className="py-3.5 px-4 font-medium text-slate-200">{item.type}</td>
                  <td className="py-3.5 px-4">{item.location}</td>
                  <td className="py-3.5 px-4">{item.severity}</td>
                  <td className="py-3.5 px-4"><StatusBadge status={item.status} /></td>
                  <td className="py-3.5 px-4 text-slate-500 text-xs">{item.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default HistoryPage;