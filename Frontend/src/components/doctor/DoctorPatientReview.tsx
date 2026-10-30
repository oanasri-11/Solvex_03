import React from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { 
  ArrowLeft, 
  TrendingUp, 
  Calendar, 
  MessageSquare 
} from 'lucide-react';

export const DoctorPatientReview: React.FC = () => {
  const { selectedPatient, setDoctorView } = useApp();

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
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
          onClick={() => setDoctorView('patient_detail')}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-xs transition-colors shrink-0"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to patient record</span>
        </button>
      </div>

      {/* Review Section Heading with Summary Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-2">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">14-day patient review</h2>
          <p className="text-xs text-slate-500 mt-0.5">Oct 11–25, 2024 · 24 readings</p>
        </div>
        <Badge variant="within_target">
          Patient summary
        </Badge>
      </div>

      {/* 3 Metric Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1 */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <p className="text-xs font-medium text-slate-500">Average blood pressure</p>
          <h3 className="text-4xl font-extrabold text-slate-900 tracking-tight my-2">154/94</h3>
          <p className="text-xs text-slate-500">mmHg · baseline 142/86</p>
        </div>

        {/* Card 2 */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <p className="text-xs font-medium text-slate-500">Reading adherence · 14 days</p>
          <h3 className="text-4xl font-extrabold text-slate-900 tracking-tight my-2">86%</h3>
          <p className="text-xs text-slate-500">24 of 28 scheduled readings</p>
        </div>

        {/* Card 3 */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <p className="text-xs font-medium text-slate-500">Alerts in this period</p>
          <h3 className="text-4xl font-extrabold text-amber-600 tracking-tight my-2">2</h3>
          <p className="text-xs text-slate-500">Persistent elevation and Oct 21 spike</p>
        </div>
      </div>

      {/* Core Clinical Findings Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
        <h3 className="text-lg font-bold text-slate-900">Core clinical findings</h3>

        <div className="space-y-5">
          {/* Finding 1 */}
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-xl bg-rose-50 text-rose-600 shrink-0">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-sm">
                Blood pressure control has worsened
              </h4>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                Average BP increased by 12/8 mmHg from baseline. A spike of 168/102 mmHg was recorded on Oct 21.
              </p>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Finding 2 */}
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-xl bg-amber-50 text-amber-600 shrink-0">
              <Calendar className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-sm">
                Evening readings need follow-up
              </h4>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                Two consecutive evening readings were missed on Oct 22 and 23 during this review period.
              </p>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Finding 3 */}
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-xl bg-slate-100 text-slate-600 shrink-0">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-sm">
                Morning symptoms reported
              </h4>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                Two morning occipital headaches were reported, aligning with systolic readings above 165 mmHg.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Morning and Evening Readings Breakdown */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-5">
        <h3 className="text-lg font-bold text-slate-900">Morning and evening readings</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Morning Column */}
          <div className="bg-[#f8fafc] border border-slate-200/60 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-900">Morning</span>
              <span className="text-slate-500 font-mono">07:00–10:30</span>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-900">156/95</span>
              <span className="text-xs text-slate-500">mmHg mean</span>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-200/50">
              <span>13/14 readings captured</span>
              <span className="font-medium text-slate-700">75 bpm</span>
            </div>
          </div>

          {/* Evening Column */}
          <div className="bg-[#f8fafc] border border-slate-200/60 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-900">Evening</span>
              <span className="text-slate-500 font-mono">18:30–21:30</span>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-900">151/91</span>
              <span className="text-xs text-slate-500">mmHg mean</span>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-200/50">
              <span>11/14 readings captured</span>
              <span className="font-medium text-slate-700">71 bpm</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
