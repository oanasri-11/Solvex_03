import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { BPLineChart } from '../charts/BPLineChart';
import { Badge } from '../common/Badge';
import { readingService } from '../../services/readingService';
import { alertService, type AlertOut } from '../../services/alertService';
import { doctorService } from '../../services/doctorService';
import { patientService } from '../../services/patientService';
import { mapBackendReadingToBPReading } from '../../utils/mappers';
import type { BPReading } from '../../types';
import { 
  Phone, 
  TrendingUp, 
  ArrowRight, 
  Check, 
  CheckCircle,
  Loader2
} from 'lucide-react';

export const DoctorPatientDetail: React.FC = () => {
  const { 
    selectedPatient, 
    setDoctorView, 
    marcDpuisReadings 
  } = useApp();

  const [reviewed, setReviewed] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [readings, setReadings] = useState<BPReading[]>(marcDpuisReadings);
  const [alerts, setAlerts] = useState<AlertOut[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [isContacting, setIsContacting] = useState(false);

  const numericId = parseInt(selectedPatient.id, 10);

  useEffect(() => {
    if (!isNaN(numericId)) {
      setIsLoading(true);
      Promise.all([
        readingService.getPatientReadings(numericId)
          .then(res => {
            if (res && res.length > 0) {
              setReadings(res.map(mapBackendReadingToBPReading));
            }
          })
          .catch(err => console.warn('Could not load patient readings:', err)),
        alertService.getPatientAlerts(numericId)
          .then(res => {
            if (res) setAlerts(res);
          })
          .catch(err => console.warn('Could not load patient alerts:', err))
      ]).finally(() => {
        setIsLoading(false);
      });
    } else {
      setReadings(marcDpuisReadings);
    }
  }, [selectedPatient.id, numericId, marcDpuisReadings]);

  const handleMarkReviewed = async () => {
    if (isNaN(numericId)) {
      setReviewed(true);
      setToastMessage('Patient record marked as reviewed for this clinical cycle.');
      setTimeout(() => setToastMessage(null), 3500);
      return;
    }

    setIsSubmittingReview(true);
    try {
      await patientService.submitCaseReview(numericId, {
        summary: `Cycle review completed for ${selectedPatient.name}. Protocol adherence: ${selectedPatient.adherenceRate || 80}%.`,
        status: 'completed',
        clinical_notes: 'All readings reviewed. Regimen maintained.',
      });
      setReviewed(true);
      setToastMessage('Patient case review signed off and persisted.');
    } catch (err: any) {
      console.warn('Could not submit case review:', err);
      setReviewed(true);
      setToastMessage('Patient record marked as reviewed.');
    } finally {
      setIsSubmittingReview(false);
      setTimeout(() => setToastMessage(null), 3500);
    }
  };

  const handleContactPatient = async () => {
    if (isNaN(numericId)) {
      setToastMessage(`Initiating contact with ${selectedPatient.name}...`);
      setTimeout(() => setToastMessage(null), 3000);
      return;
    }

    setIsContacting(true);
    try {
      await doctorService.initiateContact(
        numericId,
        'Please review your latest blood pressure readings and confirm adherence.'
      );
      setToastMessage(`Contact task created for ${selectedPatient.name}.`);
    } catch (err) {
      console.warn('Could not initiate contact request:', err);
      setToastMessage(`Initiating contact with ${selectedPatient.name}...`);
    } finally {
      setIsContacting(false);
      setTimeout(() => setToastMessage(null), 3000);
    }
  };

  // Transform patient readings for BP trend chart
  const chartPoints = readings && readings.length > 0
    ? readings.slice(0, 14).reverse().map(r => ({
        label: r.date.split(',')[0] || r.date,
        systolic: r.systolic,
        diastolic: r.diastolic,
        isManual: r.isManual,
        tooltipText: `${r.date} · ${r.systolic}/${r.diastolic} mmHg`,
      }))
    : undefined;

  if (!selectedPatient || !selectedPatient.id) {
    return (
      <div className="p-12 text-center text-slate-500">
        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-teal-600" />
        <p>Loading patient record from live backend...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-lg flex items-center gap-2 text-sm z-50 animate-fadeIn">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Patient Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-[#d1ebe8] text-[#0d6269] font-bold text-lg flex items-center justify-center shrink-0 border border-teal-200">
            {selectedPatient.initials}
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              {selectedPatient.name}
            </h1>
            <p className="text-sm text-slate-500 mt-0.5">
              {selectedPatient.age} years · {selectedPatient.birthDate} · {selectedPatient.code} · {selectedPatient.isTelemonitoring ? 'Telemonitoring' : 'Self-monitoring'}
            </p>
          </div>
        </div>

        <button
          onClick={handleContactPatient}
          disabled={isContacting}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm bg-[#0d6269] text-white hover:bg-teal-800 shadow-xs transition-colors shrink-0 disabled:opacity-60"
        >
          {isContacting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Phone className="w-4 h-4" />
          )}
          <span>Contact patient</span>
        </button>
      </div>

      {/* Alert Warning Banner */}
      <div className="bg-[#fff1f2] border border-rose-200/80 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="p-1 rounded-lg text-rose-600 mt-0.5">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-rose-900 text-sm">
              Clinical Priority: {selectedPatient.statusLabel}
            </h4>
            <p className="text-xs text-rose-700/90 mt-0.5">
              Latest reading {selectedPatient.latestSystolic}/{selectedPatient.latestDiastolic} mmHg ({selectedPatient.latestReadingTime}).
            </p>
          </div>
        </div>

        <div className="text-left md:text-right shrink-0 pl-8 md:pl-0">
          <p className="text-xs text-slate-500">Current reading adherence</p>
          <p className="text-2xl font-black text-slate-900">{selectedPatient.adherenceRate || 85}%</p>
        </div>
      </div>

      {/* Blood Pressure Trend Chart Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Blood pressure trend</h3>
            <p className="text-xs text-slate-500">Target {selectedPatient.targetBP || '<135/85 mmHg'} · Baseline {selectedPatient.baselineBP || '140/90 mmHg'}</p>
          </div>
          <button
            onClick={() => setDoctorView('patient_review')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#0d6269] hover:underline"
          >
            <span>Review 14-day summary</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="pt-2">
          <BPLineChart data={chartPoints} />
        </div>
      </div>

      {/* Two Column Grid: Recent Readings & Active Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Readings (Left 7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900">Recent readings</h3>
            {isLoading && <Loader2 className="w-4 h-4 animate-spin text-teal-600" />}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-100 text-xs text-slate-400 font-normal">
                  <th className="pb-3 font-normal">Date & time</th>
                  <th className="pb-3 font-normal">BP · mmHg</th>
                  <th className="pb-3 font-normal text-right">Pulse · bpm</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {readings.slice(0, 7).map((reading) => (
                  <tr key={reading.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5">
                      <p className="font-semibold text-slate-900">
                        {reading.date} · {reading.time}
                      </p>
                      <p className="text-xs text-slate-400">{reading.period} {reading.isManual ? '· Manual' : '· BLE'}</p>
                    </td>
                    <td className="py-3.5 font-bold text-slate-900 text-base">
                      {reading.systolic}/{reading.diastolic}
                    </td>
                    <td className="py-3.5 text-right font-medium text-slate-600">
                      {reading.pulse}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Active Alerts (Right 5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900">Active alerts</h3>
              <button
                onClick={() => setDoctorView('alerts')}
                className="inline-flex items-center gap-1 text-xs font-semibold text-[#0d6269] hover:underline"
              >
                <span>Open inbox</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-4 pt-1">
              {alerts.length > 0 ? (
                alerts.slice(0, 3).map((a) => (
                  <div key={a.id} className="space-y-1.5 border-b border-slate-100 pb-3 last:border-none">
                    <Badge variant={a.tier === 'critical_emergency' || a.severity === 'critical' ? 'crisis' : 'urgent'}>
                      {a.lifecycle === 'acknowledged' ? 'Acknowledged' : 'Unacknowledged'}
                    </Badge>
                    <h4 className="font-bold text-slate-900 text-sm">
                      {a.alert_type.replace(/_/g, ' ').toUpperCase()}
                    </h4>
                    <p className="text-xs text-slate-500">
                      {a.message || 'Elevated blood pressure observed outside target thresholds.'}
                    </p>
                  </div>
                ))
              ) : (
                <>
                  <div className="space-y-1.5">
                    <Badge variant="crisis">
                      High · Unacknowledged
                    </Badge>
                    <h4 className="font-bold text-slate-900 text-sm">
                      Persistent systolic elevation
                    </h4>
                    <p className="text-xs text-slate-500">
                      Multi-reading elevation above protocol target.
                    </p>
                  </div>

                  <hr className="border-slate-100" />

                  <div className="space-y-1.5">
                    <Badge variant="under_follow_up">
                      Under follow-up
                    </Badge>
                    <h4 className="font-bold text-slate-900 text-sm">
                      Schedule compliance monitor
                    </h4>
                    <p className="text-xs text-slate-500">
                      722 protocol slot adherence tracked.
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Medical Banner and Review Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-slate-200/80 text-xs">
        <span className="text-slate-500 font-medium">
          {selectedPatient.condition || 'HTN Stage 2'} · {selectedPatient.medication || 'Amlodipine 5mg QD'} · Target {selectedPatient.targetBP || '<135/85 mmHg'}
        </span>

        <button
          onClick={handleMarkReviewed}
          disabled={isSubmittingReview}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold border transition-all shadow-xs disabled:opacity-60 ${
            reviewed
              ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
              : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
          }`}
        >
          {isSubmittingReview ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Check className={`w-4 h-4 ${reviewed ? 'text-emerald-600' : 'text-slate-500'}`} />
          )}
          <span>{reviewed ? 'Reviewed' : 'Mark reviewed'}</span>
        </button>
      </div>
    </div>
  );
};
