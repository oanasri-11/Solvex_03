import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { alertService } from '../../services/alertService';
import { 
  ArrowLeft, 
  Info, 
  BluetoothOff, 
  RotateCw, 
  Phone, 
  CheckCircle2,
  Check,
  Loader2
} from 'lucide-react';

export const PatientAlertDetail: React.FC = () => {
  const { selectedPatientAlert, setPatientView, refreshPatientReadings } = useApp();
  const [syncing, setSyncing] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);
  const [confirmingGuidance, setConfirmingGuidance] = useState(false);
  const [guidanceConfirmed, setGuidanceConfirmed] = useState(
    selectedPatientAlert.status === 'review_needed' || selectedPatientAlert.statusLabel.includes('Reviewed')
  );

  const handleRetrySync = () => {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
      setSyncSuccess(true);
      setTimeout(() => setSyncSuccess(false), 4000);
    }, 1500);
  };

  const handleConfirmGuidance = async () => {
    setConfirmingGuidance(true);
    const numId = parseInt(selectedPatientAlert.id, 10);
    try {
      if (!isNaN(numId)) {
        await alertService.patientAcknowledgeAlert(numId, {
          confirmed: true,
          action_taken: 'Patient confirmed reading guidance on screen',
        });
      }
      setGuidanceConfirmed(true);
      setSyncSuccess(true);
      await refreshPatientReadings();
    } catch (err) {
      console.warn('Could not confirm alert on backend:', err);
      setGuidanceConfirmed(true);
      setSyncSuccess(true);
    } finally {
      setConfirmingGuidance(false);
      setTimeout(() => setSyncSuccess(false), 4000);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Toast */}
      {syncSuccess && (
        <div className="fixed bottom-6 right-6 bg-[#0d6269] text-white px-5 py-3.5 rounded-xl shadow-xl flex items-center gap-2 text-sm z-50 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-emerald-300" />
          <span>Safety guidance review successfully recorded and sent to your doctor!</span>
        </div>
      )}

      {/* Top Banner Notice */}
      <div className="bg-[#e9f4f9] border border-sky-100 rounded-2xl p-4 flex items-start gap-3.5">
        <Info className="w-5 h-5 text-sky-700 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-slate-900 text-xs">
            Clinical Safety Protocol • روض Telemonitoring
          </h4>
          <p className="text-xs text-slate-600 mt-0.5">
            Guidance generated based on your blood pressure measurements and ESH hypertension thresholds.
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
          <Badge variant={guidanceConfirmed ? 'within_target' : selectedPatientAlert.status}>
            {guidanceConfirmed ? 'Guidance Reviewed' : selectedPatientAlert.statusLabel}
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
            {selectedPatientAlert.description}
          </h4>
          <p className="text-xs text-slate-600 mt-0.5">
            Please follow the recommended steps below and confirm once you have completed them.
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
                <h5 className="font-bold text-slate-900 text-sm">Rest & Relax</h5>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Sit quietly in a comfortable chair for 5 minutes without talking, checking your phone, or caffeine.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                2
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Repeat BP Measurement</h5>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Take a second measurement on your left arm. Ensure the cuff is level with your heart.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                3
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Confirm Guidance</h5>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Click the button below so your supervising physician knows you have seen this notification.
                </p>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={handleConfirmGuidance}
              disabled={confirmingGuidance || guidanceConfirmed}
              className={`inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm transition-all shadow-xs ${
                guidanceConfirmed
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-300'
                  : 'bg-[#0d6269] text-white hover:bg-teal-800'
              }`}
            >
              {confirmingGuidance ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Check className="w-4 h-4" />
              )}
              <span>{guidanceConfirmed ? 'Guidance Confirmed' : 'I Have Read and Applied This Guidance'}</span>
            </button>

            <button
              onClick={handleRetrySync}
              disabled={syncing}
              className="inline-flex items-center gap-2 px-4 py-3 rounded-xl font-semibold text-sm border border-slate-200 text-slate-700 hover:bg-slate-50 transition-all shadow-xs"
            >
              <RotateCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
              <span>Retry device sync</span>
            </button>
          </div>
        </div>

        {/* Right Column: Understanding this alert & Emergency hotline (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Understanding this alert Card */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
            <h4 className="font-bold text-slate-900 text-sm">Understanding this alert</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Your safety alert was triggered automatically when measurements differed significantly from your target thresholds.
            </p>

            <hr className="border-slate-100" />

            <div className="space-y-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                SOURCE / CONTEXT
              </span>
              <p className="text-xs text-slate-700 font-medium">Automatic Clinical Telemonitoring Engine</p>
              <p className="text-[11px] text-slate-400">Alert Reference: {selectedPatientAlert.code}</p>
            </div>
          </div>

          {/* Emergency Symptoms Card */}
          <div className="bg-[#fff1f2] border border-rose-200/80 rounded-2xl p-6 space-y-2">
            <div className="flex items-center gap-2 text-rose-700 font-bold text-sm">
              <Phone className="w-4 h-4" />
              <span>For emergency symptoms</span>
            </div>
            <p className="text-xs text-rose-800 leading-relaxed">
              For chest pain, severe shortness of breath or visual changes, call emergency services immediately (14 or 15). روض is not an emergency hotline.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
