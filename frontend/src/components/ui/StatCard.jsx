import React from 'react';

const StatCard = ({ title, value, change, changeType, icon: Icon, description }) => {
  const isPositive = changeType === 'positive';

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 backdrop-blur-sm relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
        </div>
        {Icon && (
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
      
      {(change || description) && (
        <div className="mt-4 flex items-center text-xs">
          {change && (
            <span className={`font-semibold mr-2 ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
              {isPositive ? '↑' : '↓'} {change}
            </span>
          )}
          {description && <span className="text-slate-500">{description}</span>}
        </div>
      )}
      <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl pointer-events-none"></div>
    </div>
  );
};

export default StatCard;