import React from 'react';
import { Bell, Search, UserCheck } from 'lucide-react';

const Navbar = ({ pageTitle = 'Dashboard' }) => {
  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 px-6 flex items-center justify-between">
      <h2 className="text-xl font-bold text-white">{pageTitle}</h2>

      <div className="flex items-center gap-4">
        {/* Search Bar */}
        <div className="relative hidden md:block">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search intersections, signals, or incidents..."
            className="bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-4 py-1.5 text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 w-72"
          />
        </div>

        {/* Notifications */}
        <button className="relative p-2 bg-slate-800 text-slate-300 rounded-lg border border-slate-700 hover:text-white transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-500 rounded-full"></span>
        </button>

        {/* User Pill */}
        <div className="flex items-center gap-3 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-semibold text-sm">
            AD
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-sm font-medium text-slate-200 leading-none">Dispatcher Operator</p>
            <span className="text-xs text-emerald-400 flex items-center gap-1 mt-1">
              <UserCheck className="w-3 h-3 inline" /> Authorized
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;