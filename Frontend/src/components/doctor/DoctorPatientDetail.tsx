import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { BPLineChart } from '../charts/BPLineChart';
import { Badge } from '../common/Badge';
import { 
  Phone, 
  TrendingUp, 
  ArrowRight, 
  Check, 
  CheckCircle
} from 'lucide-react';

export const DoctorPatientDetail: React.FC = () => {
  const { 
    selectedPatient, 
    setDoctorView, 
    marcDpuisReadings 
  } = useApp();

  const [reviewed, setReviewed] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleMarkReviewed = () => {
    setReviewed(true);
    setToastMessage('Patient record marked as reviewed for this clinical cycle.');
    setTimeout(() => setToastMessage(null), 3000);
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-lg flex items-center gap-2 text-sm z-50">
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
              {selectedPatient.age} years · {selectedPatient.birthDate} · {selectedPatient.code} · Telemonitoring
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            setToastMessage(`Initiating contact with ${selectedPatient.name}...`);
            setTimeout(() => setToastMessage(null), 3000);
          }}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm bg-[#0d6269] text-white hover:bg-teal-800 shadow-xs transition-colors shrink-0"
        >
          <Phone className="w-4 h-4" />
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
              Worsening blood pressure over 10 days
            </h4>
            <p className="text-xs text-rose-700/90 mt-0.5">
              Morning average 154/94 mmHg over 7 days, compared with a 142/86 baseline.
            </p>
          </div>
        </div>

        <div className="text-left md:text-right shrink-0 pl-8 md:pl-0">
          <p className="text-xs text-slate-500">Current reading adherence</p>
          <p className="text-2xl font-black text-slate-900">78%</p>
        </div>
      </div>

      {/* Blood Pressure Trend Chart Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Blood pressure trend</h3>
            <p className="text-xs text-slate-500">Recent recorded readings · Oct 18–25, 2024 · mmHg</p>
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
          <BPLineChart />
        </div>
      </div>

      {/* Two Column Grid: Recent Readings & Active Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Readings (Left 7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
          <h3 className="text-lg font-bold text-slate-900">Recent readings</h3>

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
                {marcDpuisReadings.map((reading) => (
                  <tr key={reading.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5">
                      <p className="font-semibold text-slate-900">
                        {reading.date} · {reading.time}
                      </p>
                      <p className="text-xs text-slate-400">{reading.period}</p>
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
              {/* Alert 1 */}
              <div className="space-y-1.5">
                <Badge variant="crisis">
                  High · Unacknowledged
                </Badge>
                <h4 className="font-bold text-slate-900 text-sm">
                  Persistent systolic elevation
                </h4>
                <p className="text-xs text-slate-500">
                  5-day mean: 156 ± 4 mmHg
                </p>
              </div>

              <hr className="border-slate-100" />

              {/* Alert 2 */}
              <div className="space-y-1.5">
                <Badge variant="under_follow_up">
                  Under follow-up
                </Badge>
                <h4 className="font-bold text-slate-900 text-sm">
                  2 missed evening measurements
                </h4>
                <p className="text-xs text-slate-500">
                  Acknowledged by Dr. Karim B.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Medical Banner and Review Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-slate-200/80 text-xs">
        <span className="text-slate-500 font-medium">
          HTN Stage 2 · Dyslipidemia · Amlodipine 5mg QD · Target &lt;135/85 mmHg
        </span>

        <button
          onClick={handleMarkReviewed}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold border transition-all shadow-xs ${
            reviewed
              ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
              : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
          }`}
        >
          <Check className={`w-4 h-4 ${reviewed ? 'text-emerald-600' : 'text-slate-500'}`} />
          <span>{reviewed ? 'Reviewed' : 'Mark reviewed'}</span>
        </button>
      </div>
    </div>
  );
};
