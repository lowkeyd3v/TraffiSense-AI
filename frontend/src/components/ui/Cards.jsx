import React from 'react';

export const Card = ({ children, className = '' }) => {
  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-6 ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader = ({ title, subtitle, action }) => {
  return (
    <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
      <div>
        <h3 className="text-lg font-bold text-white tracking-wide">{title}</h3>
        {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
};