import React from 'react';
import { BrainCircuit, TrendingUp, Cpu } from 'lucide-react';

const PredictionPanel = ({ prediction, loading, onTrigger }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-indigo-400" />
          <h3 className="font-bold text-white">AI Predictive Engine</h3>
        </div>
        <span className="text-[10px] uppercase font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2.5 py-1 rounded-md">
          Neural Net v4.2
        </span>
      </div>

      {prediction ? (
        <div className="space-y-4">
          <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Predicted Congestion</span>
            <div className="flex items-center justify-between mt-1">
              <span className="text-2xl font-extrabold text-indigo-400">{prediction.predictedCongestion}</span>
              <span className="text-xs text-emerald-400 flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5" /> High Precision
              </span>
            </div>
          </div>

          <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Signal Optimization</span>
            <p className="text-sm font-semibold text-emerald-400 mt-1">{prediction.recommendedSignalTiming}</p>
          </div>

          <div className="flex justify-between items-center text-xs text-slate-400 pt-2 border-t border-slate-800">
            <span>Model Confidence:</span>
            <span className="font-mono text-white font-bold">{prediction.confidenceScore}</span>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-slate-500">
          <Cpu className="w-10 h-10 mx-auto mb-2 opacity-40 animate-pulse" />
          <p className="text-xs">No prediction generated. Trigger inference engine to compute models.</p>
        </div>
      )}

      {onTrigger && (
        <button
          onClick={onTrigger}
          disabled={loading}
          className="w-full mt-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs rounded-lg transition-colors flex items-center justify-center gap-2 cursor-pointer"
        >
          {loading ? 'Running Network Analysis...' : 'Re-Run AI Inference'}
        </button>
      )}
    </div>
  );
};

export default PredictionPanel;