import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { 
  ArrowLeft, 
  Info, 
  BluetoothOff, 
  RotateCw, 
  Phone, 
  CheckCircle2
} from 'lucide-react';

export const PatientAlertDetail: React.FC = () => {
  const { selectedPatientAlert, setPatientView } = useApp();
  const [syncing, setSyncing] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);

  const handleRetrySync = () => {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
      setSyncSuccess(true);
      setTimeout(() => setSyncSuccess(false), 4000);
    }, 2000);
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Toast */}
      {syncSuccess && (
        <div className="fixed bottom-6 right-6 bg-[#0d6269] text-white px-5 py-3.5 rounded-xl shadow-xl flex items-center gap-2 text-sm z-50 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-emerald-300" />
          <span>Bluetooth connection re-established! OMRON monitor synced.</span>
        </div>
      )}

      {/* Top Banner Notice */}
      <div className="bg-[#e9f4f9] border border-sky-100 rounded-2xl p-4 flex items-start gap-3.5">
        <Info className="w-5 h-5 text-sky-700 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-slate-900 text-xs">
            Demonstration — example alerts
          </h4>
          <p className="text-xs text-slate-600 mt-0.5">
            Fictional scenarios, unrelated to real events involving Amina Benali.
          </p>
        </div>
      </div>

      {/* Back button */}
      <div>
        <button
          onClick={() => setPatientView('alerts')}
          className="inline-flex items-center gap-2 text-xs font-bold text-[#0d6269] hover:underline"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to alerts & actions</span>
        </button>
      </div>

      {/* Alert Header */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant={selectedPatientAlert.level as any}>
            <Info className="w-3 h-3 text-sky-600" />
            {selectedPatientAlert.levelLabel}
          </Badge>
          <span className="text-xs text-slate-500 font-medium">
            {selectedPatientAlert.category} • {selectedPatientAlert.code}
          </span>
        </div>

        <h1 className="text-3xl font-extrabold text-[#0d6269] tracking-tight">
          {selectedPatientAlert.title}
        </h1>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500">{selectedPatientAlert.dateTime.replace('\n', ' at ')}</span>
          <Badge variant={selectedPatientAlert.status}>
            {selectedPatientAlert.statusLabel}
          </Badge>
        </div>
      </div>

      {/* Blue Informational Callout */}
      <div className="bg-[#e9f4f9] border border-sky-100 rounded-2xl p-5 flex items-start gap-4">
        <div className="p-1 rounded-lg text-sky-700 mt-0.5">
          <BluetoothOff className="w-5 h-5" />
        </div>
        <div>
          <h4 className="font-bold text-slate-900 text-sm">
            No sync does not mean normal blood pressure.
          </h4>
          <p className="text-xs text-slate-600 mt-0.5">
            Missing data cannot confirm your blood pressure. Continue monitoring as prescribed.
          </p>
        </div>
      </div>

      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: What should I do now? (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
          <h3 className="text-lg font-bold text-slate-900">What should I do now?</h3>

          <div className="space-y-4">
            {/* Step 1 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                1
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Check connections</h5>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Enable Bluetooth on the connecting device. Check internet access and permissions for the companion app.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                2
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Check the BP monitor</h5>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Check the batteries and turn on the monitor. Move it closer to the connecting device, following its instructions.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                3
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Restart syncing</h5>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Reopen the companion app and try again. If the issue persists, keep the displayed readings and enter them manually.
                </p>
              </div>
            </div>
          </div>

          {/* Retry sync button */}
          <div className="pt-2">
            <button
              onClick={handleRetrySync}
              disabled={syncing}
              className={`inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm bg-[#0d6269] text-white hover:bg-teal-800 transition-all shadow-xs ${
                syncing ? 'opacity-70 cursor-wait' : ''
              }`}
            >
              <RotateCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
              <span>{syncing ? 'Attempting reconnection...' : 'Retry sync'}</span>
            </button>
          </div>
        </div>

        {/* Right Column: Understanding this alert & Emergency hotline (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Understanding this alert Card */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
            <h4 className="font-bold text-slate-900 text-sm">Understanding this alert</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              In this example, reading transfers from the blood pressure monitor have stopped. New data is unavailable in the portal.
            </p>

            <hr className="border-slate-100" />

            <div className="space-y-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                SOURCE / CONTEXT
              </span>
              <p className="text-xs text-slate-700 font-medium">Connection status — example scenario</p>
              <p className="text-[11px] text-slate-400">Example EX-003 • 28/10/2026 at 08:15</p>
            </div>
          </div>

          {/* Emergency Symptoms Card */}
          <div className="bg-[#fff1f2] border border-rose-200/80 rounded-2xl p-6 space-y-2">
            <div className="flex items-center gap-2 text-rose-700 font-bold text-sm">
              <Phone className="w-4 h-4" />
              <span>For emergency symptoms</span>
            </div>
            <p className="text-xs text-rose-800 leading-relaxed">
              For chest pain or shortness of breath, call 15 or 112 without waiting for sync. TensioCare is not an emergency service.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
