import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  BarChart3, 
  History, 
  AlertTriangle, 
  BrainCircuit, 
  Radio, 
  Settings, 
  User,
  ShieldAlert
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/history', label: 'Incident History', icon: History },
    { path: '/report-incident', label: 'Report Incident', icon: AlertTriangle },
    { path: '/prediction', label: 'AI Prediction', icon: BrainCircuit },
    { path: '/deployment', label: 'Resource Deployment', icon: Radio },
    { path: '/settings', label: 'Settings', icon: Settings },
    { path: '/profile', label: 'Profile', icon: User },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <div className="p-2 bg-indigo-600 rounded-lg text-white shadow-lg shadow-indigo-500/30">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white tracking-wide">TraffiSense AI</h1>
          <p className="text-xs text-indigo-400 font-medium">Command Center</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="p-4 m-4 bg-slate-800/40 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-slate-400">System Engine</span>
          <span className="text-emerald-400 font-semibold">ONLINE</span>
        </div>
        <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
          <div className="bg-emerald-500 h-full w-full animate-pulse"></div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;