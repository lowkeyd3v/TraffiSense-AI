import React from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { User, Shield } from 'lucide-react';

const ProfilePage = () => {
  return (
    <DashboardLayout title="Operator Profile">
      <div className="max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-4 border-b border-slate-800 pb-6 mb-6">
          <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center text-xl font-bold text-white">
            AD
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Authorized Dispatch Operator</h3>
            <p className="text-xs text-indigo-400">Level 3 Grid Controller</p>
          </div>
        </div>

        <div className="space-y-4 text-sm text-slate-300">
          <div className="flex justify-between py-2 border-b border-slate-800/60">
            <span className="text-slate-500">Operator ID</span>
            <span className="font-mono text-white">OP-99824</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-800/60">
            <span className="text-slate-500">Email</span>
            <span className="text-white">dispatcher@traffisense.ai</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-500">Security Access</span>
            <span className="text-emerald-400 font-semibold flex items-center gap-1">
              <Shield className="w-4 h-4" /> Clear
            </span>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ProfilePage;