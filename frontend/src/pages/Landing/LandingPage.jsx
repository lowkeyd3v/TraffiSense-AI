import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Cpu, Activity, ArrowRight, Radio } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Navbar */}
      <nav className="border-b border-slate-800 px-8 py-4 flex justify-between items-center bg-slate-900/50 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-600 rounded-lg">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-wider text-white">TraffiSense AI</span>
        </div>
        <div className="flex gap-4">
          <Link to="/login" className="px-5 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors">
            Sign In
          </Link>
          <Link to="/dashboard" className="px-5 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors">
            Launch Command Center
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="flex-1 flex flex-col justify-center items-center text-center px-6 my-16 max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-6">
          <Cpu className="w-4 h-4" /> Next-Gen AI Traffic Management System
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          Intelligent Urban Traffic Regulation & Incident Control
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mb-8">
          Predict congestion, optimize traffic light sequences in real-time, and dispatch emergency response teams with precision AI intelligence.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Link to="/dashboard" className="px-8 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/30">
            Enter Live Command Dashboard <ArrowRight className="w-5 h-5" />
          </Link>
          <Link to="/report-incident" className="px-8 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold rounded-xl transition-all">
            Report Emergency Incident
          </Link>
        </div>
      </header>

      {/* Feature Grid */}
      <section className="max-w-6xl mx-auto px-6 mb-20 grid md:grid-cols-3 gap-8">
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <Activity className="w-8 h-8 text-indigo-400 mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">Real-Time Monitoring</h3>
          <p className="text-slate-400 text-sm">Automated live grid surveillance tracking congestion metrics, signal health, and vehicle density.</p>
        </div>
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <Cpu className="w-8 h-8 text-indigo-400 mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">Predictive AI Control</h3>
          <p className="text-slate-400 text-sm">Neural network models forecast grid bottleneck locations up to 45 minutes ahead of occurrence.</p>
        </div>
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <Radio className="w-8 h-8 text-indigo-400 mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">Automated Dispatch</h3>
          <p className="text-slate-400 text-sm">Instant routing & resource deployment for traffic responders, tow trucks, and medical services.</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        &copy; 2026 TraffiSense AI Command Center. All Rights Reserved.
      </footer>
    </div>
  );
};

export default LandingPage;