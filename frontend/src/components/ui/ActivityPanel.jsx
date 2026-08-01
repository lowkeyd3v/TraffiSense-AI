import React from 'react';
import { Activity, ArrowUpRight } from 'lucide-react';

const ActivityPanel = ({ activities = [] }) => {
  const defaultActivities = [
    { id: 1, text: 'Signal #104 timing auto-adjusted by AI model', time: '2 mins ago', level: 'info' },
    { id: 2, text: 'Dispatch Unit #3 confirmed arrival at 42nd St', time: '8 mins ago', level: 'success' },
    { id: 3, text: 'Congestion spike detected on Sector 4 Highway', time: '14 mins ago', level: 'warning' },
  ];

  const list = activities.length > 0 ? activities : defaultActivities;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-white flex items-center gap-2 text-sm">
          <Activity className="w-4 h-4 text-indigo-400" /> Real-time System Audit Feed
        </h3>
        <span className="text-[10px] text-slate-500">Live Updates</span>
      </div>

      <div className="space-y-3">
        {list.map((act) => (
          <div key={act.id} className="p-3 bg-slate-950 border border-slate-800/60 rounded-xl flex items-start gap-3">
            <div className="p-1.5 bg-indigo-500/10 text-indigo-400 rounded-md mt-0.5">
              <ArrowUpRight className="w-3.5 h-3.5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-slate-200 font-medium leading-snug">{act.text}</p>
              <span className="text-[10px] text-slate-500 mt-1 block">{act.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ActivityPanel;