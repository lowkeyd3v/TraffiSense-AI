import React, { useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { predictionService } from '../../services/api';
import { BrainCircuit, Cpu } from 'lucide-react';

const PredictionPage = () => {
  const [params, setParams] = useState({ corridor: 'Main Arterial A', timeframe: '30m' });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    setLoading(true);
    const result = await predictionService.getTrafficPrediction(params);
    setPrediction(result);
    setLoading(false);
  };

  return (
    <DashboardLayout title="AI Predictive Traffic Forecasting">
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="font-bold text-white mb-4 flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-indigo-400" /> Forecast Settings
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase mb-2">Target Corridor</label>
              <select
                value={params.corridor}
                onChange={(e) => setParams({ ...params, corridor: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="Main Arterial A">Main Arterial Corridor A</option>
                <option value="Downtown Ring B">Downtown Ring B</option>
                <option value="Expressway Connector">Expressway Connector</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase mb-2">Time Window</label>
              <select
                value={params.timeframe}
                onChange={(e) => setParams({ ...params, timeframe: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="15m">15 Minutes Ahead</option>
                <option value="30m">30 Minutes Ahead</option>
                <option value="60m">60 Minutes Ahead</option>
              </select>
            </div>
            <button
              onClick={handlePredict}
              disabled={loading}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <Cpu className="w-4 h-4" /> {loading ? 'Computing Model...' : 'Run Neural Forecast'}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-center">
          {prediction ? (
            <div className="space-y-6">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">
                <span className="text-xs text-slate-500 uppercase font-semibold">Predicted Congestion Index</span>
                <p className="text-3xl font-extrabold text-indigo-400 mt-1">{prediction.predictedCongestion}</p>
              </div>
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">
                <span className="text-xs text-slate-500 uppercase font-semibold">Recommended AI Signal Adjustment</span>
                <p className="text-lg font-semibold text-emerald-400 mt-1">{prediction.recommendedSignalTiming}</p>
              </div>
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center">
                <span className="text-xs text-slate-500 uppercase font-semibold">Model Confidence Score</span>
                <span className="text-sm font-bold text-slate-200">{prediction.confidenceScore}</span>
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-500">
              <BrainCircuit className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm">Configure parameters and run the prediction model to view AI forecast outputs.</p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default PredictionPage;