import React from 'react';
import StatusBadge from './StatusBadge';
import { MapPin, Eye } from 'lucide-react';

const IncidentTable = ({ incidents = [], onViewDetail }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm text-slate-300">
        <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
          <tr>
            <th className="py-3.5 px-4">Incident ID</th>
            <th className="py-3.5 px-4">Category</th>
            <th className="py-3.5 px-4">Location</th>
            <th className="py-3.5 px-4">Severity</th>
            <th className="py-3.5 px-4">Status</th>
            <th className="py-3.5 px-4">Time</th>
            <th className="py-3.5 px-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {incidents.map((item) => (
            <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
              <td className="py-3.5 px-4 font-mono text-indigo-400 font-semibold">{item.id}</td>
              <td className="py-3.5 px-4 font-medium text-slate-200">{item.type}</td>
              <td className="py-3.5 px-4 flex items-center gap-1.5 text-slate-300">
                <MapPin className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
                {item.location}
              </td>
              <td className="py-3.5 px-4 font-semibold">{item.severity}</td>
              <td className="py-3.5 px-4">
                <StatusBadge status={item.status} />
              </td>
              <td className="py-3.5 px-4 text-xs text-slate-500">{item.timestamp}</td>
              <td className="py-3.5 px-4 text-right">
                <button
                  onClick={() => onViewDetail && onViewDetail(item)}
                  className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition-colors inline-flex items-center gap-1 text-xs"
                >
                  <Eye className="w-4 h-4" /> View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default IncidentTable;