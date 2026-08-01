import React from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import StatusBadge from '../../components/ui/StatusBadge';
import { Radio, Truck, Shield } from 'lucide-react';

const DeploymentPage = () => {
  const units = [
    { id: 'UNIT-1', type: 'Traffic Police Patrol', unitName: 'Patrol Alpha', location: '42nd St & 8th Ave', status: 'Deployed' },
    { id: 'UNIT-2', type: 'Heavy Tow Vehicle', unitName: 'Tow Support #3', location: 'FDR Drive Exit 12', status: 'Dispatched' },
    { id: 'UNIT-3', type: 'Emergency Response', unitName: 'Medic Unit 9', location: 'Station 4 Headquarters', status: 'Standby' },
  ];

  return (
    <DashboardLayout title="Resource & Field Unit Deployment">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h3 className="font-bold text-white mb-6 flex items-center gap-2">
          <Radio className="w-5 h-5 text-indigo-400" /> Active Emergency Dispatch Fleet
        </h3>

        <div className="grid md:grid-cols-3 gap-6">
          {units.map((unit) => (
            <div key={unit.id} className="bg-slate-950 border border-slate-800 rounded-xl p-5">
              <div className="flex justify-between items-start mb-3">
                <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-lg">
                  {unit.type.includes('Tow') ? <Truck className="w-5 h-5" /> : <Shield className="w-5 h-5" />}
                </div>
                <StatusBadge status={unit.status} />
              </div>
              <h4 className="font-bold text-white text-base">{unit.unitName}</h4>
              <p className="text-xs text-slate-400 mt-1">{unit.type}</p>
              <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between text-xs text-slate-500">
                <span>Location:</span>
                <span className="text-slate-300 font-medium">{unit.location}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DeploymentPage;