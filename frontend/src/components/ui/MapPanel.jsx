import React from 'react';
import { MapPin, Navigation, Layers } from 'lucide-react';

const MapPanel = ({ title = "Intersection Spatial Overview", height = "h-[450px]" }) => {
  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col ${height}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-bold text-white text-sm flex items-center gap-2">
          <MapPin className="w-4 h-4 text-indigo-400" /> {title}
        </h3>
        <div className="flex items-center gap-2">
          <button className="p-1.5 bg-slate-800 text-slate-300 hover:text-white rounded-lg border border-slate-700 text-xs flex items-center gap-1">
            <Layers className="w-3.5 h-3.5" /> Heatmap
          </button>
        </div>
      </div>

      {/* Simulated Map View Canvas */}
      <div className="flex-1 bg-slate-950 border border-slate-800 rounded-xl relative overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:20px_20px] opacity-60"></div>
        
        {/* Mock Pins */}
        <div className="absolute top-1/3 left-1/4 p-2 bg-rose-500/20 border border-rose-500 rounded-full animate-bounce">
          <MapPin className="w-5 h-5 text-rose-500" />
        </div>
        <div className="absolute top-1/2 right-1/3 p-2 bg-emerald-500/20 border border-emerald-500 rounded-full">
          <MapPin className="w-5 h-5 text-emerald-400" />
        </div>
        <div className="absolute bottom-1/4 left-1/2 p-2 bg-amber-500/20 border border-amber-500 rounded-full">
          <Navigation className="w-5 h-5 text-amber-400" />
        </div>

        <div className="relative text-center z-10 bg-slate-900/80 backdrop-blur-md border border-slate-800 p-4 rounded-xl max-w-xs">
          <p className="text-xs font-semibold text-slate-200">GIS Telemetry Active</p>
          <p className="text-[10px] text-slate-400 mt-1">Real-time coordinates synced with FastAPI spatial endpoints.</p>
        </div>
      </div>
    </div>
  );
};

export default MapPanel;