import React from 'react';

export const PrimaryButton = ({ children, onClick, icon: Icon, type = 'button', disabled = false, className = '' }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/20 cursor-pointer ${className}`}
    >
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  );
};

export const SecondaryButton = ({ children, onClick, icon: Icon, type = 'button', disabled = false, className = '' }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-sm font-semibold rounded-lg flex items-center justify-center gap-2 transition-all cursor-pointer ${className}`}
    >
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  );
};

export const DangerButton = ({ children, onClick, icon: Icon, type = 'button', disabled = false, className = '' }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2.5 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-rose-600/20 cursor-pointer ${className}`}
    >
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  );
};