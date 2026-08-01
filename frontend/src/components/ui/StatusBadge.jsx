import React from 'react';

const StatusBadge = ({ status, type = 'default' }) => {
  const getColors = () => {
    const normalized = (status || '').toLowerCase();
    
    if (normalized.includes('high') || normalized.includes('critical') || normalized.includes('progress')) {
      return 'bg-red-500/10 text-red-400 border-red-500/20';
    }
    if (normalized.includes('med') || normalized.includes('dispatch') || normalized.includes('warning')) {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    }
    if (normalized.includes('low') || normalized.includes('resolve') || normalized.includes('normal') || normalized.includes('active')) {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    }
    return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getColors()}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 animate-pulse"></span>
      {status}
    </span>
  );
};

export default StatusBadge;