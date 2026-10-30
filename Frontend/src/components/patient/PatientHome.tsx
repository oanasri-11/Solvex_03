import React from 'react';
import { useApp } from '../../context/AppContext';
import { BPLineChart } from '../charts/BPLineChart';
import { Badge } from '../common/Badge';
import { 
  Activity, 
  CheckCircle2, 
  ArrowDown, 
  Heart,
  TrendingDown
} from 'lucide-react';

export const PatientHome: React.FC = () => {
  const { setPatientView } = useApp();

  const patientTrendData = [
    { label: '18 Oct', systolic: 134, diastolic: 88 },
    { label: '19 Oct', systolic: 133, diastolic: 86 },
    { label: '20 Oct', systolic: 132, diastolic: 85 },
    { label: '21 Oct', systolic: 130, diastolic: 84, isManual: true },
    { label: '22 Oct', systolic: 129, diastolic: 83 },
    { label: '23 Oct', systolic: 128, diastolic: 82 },
    { label: '24 Oct', systolic: 128, diastolic: 82, isManual: true }
  ];

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Greeting Title */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Hello, Amina</h1>
        <p className="text-slate-500 mt-1 text-sm font-medium">Thursday, 24 October 2024</p>
      </div>

      {/* Top 2 Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Latest Reading Card (5 cols) */}
        <div className="lg:col-span-5 bg-gradient-to-br from-white to-[#f0fbf9] rounded-2xl border border-teal-100/80 shadow-xs p-7 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-xs font-bold text-[#0d6269] uppercase tracking-wider">
                <Activity className="w-4 h-4" />
                <span>Latest Reading</span>
              </div>
              <Badge variant="outline">
                Today, 08:10
              </Badge>
            </div>

            {/* Reading Value */}
            <div className="flex items-baseline gap-2 my-2">
              <span className="text-5xl font-black text-slate-900 tracking-tight">128</span>
              <span className="text-3xl font-light text-slate-400">/</span>
              <span className="text-5xl font-black text-slate-900 tracking-tight">82</span>
              <span className="text-sm font-medium text-slate-500 ml-1">mmHg</span>
            </div>

            {/* Pulse */}
            <div className="flex items-center gap-2 text-sm text-slate-600 mt-2 mb-6">
              <Heart className="w-4 h-4 text-rose-500 fill-rose-500" />
              <span className="font-bold text-slate-900">72 bpm</span>
              <span className="text-xs text-slate-400">(Regular resting pulse)</span>
            </div>
          </div>

          {/* Target Status Banner */}
          <div className="bg-[#dcf4ed] border border-teal-200/70 rounded-xl p-4 flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-emerald-950 text-sm">Within target range</h4>
              <p className="text-xs text-emerald-800/90 mt-0.5 leading-relaxed">
                Your blood pressure is within the range agreed with Dr. Laurent.
              </p>
            </div>
          </div>
        </div>

        {/* 7-day Trend Card (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 flex flex-col justify-between space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-teal-700" />
                <h3 className="text-lg font-bold text-slate-900">7-day trend</h3>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">Average morning readings</p>
            </div>

            <Badge variant="within_target" icon={<ArrowDown className="w-3 h-3 text-teal-700" />}>
              -6 mmHg toward target
            </Badge>
          </div>

          {/* Chart Container */}
          <div className="bg-[#f8fafd] rounded-xl p-4 border border-slate-100">
            <BPLineChart 
              data={patientTrendData}
              showTargetZone={true}
              targetMin={115}
              targetMax={130}
              height={180}
              showLegend={false}
              variant="patient"
            />
          </div>

          {/* Legend and Subtext */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs pt-1 border-t border-slate-100">
            <div className="flex items-center gap-4 text-slate-600">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#0d6269] inline-block"></span>
                <span>Systolic</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-slate-400 inline-block"></span>
                <span>Diastolic</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full border border-slate-700 inline-block bg-white"></span>
                <span>Manual reading</span>
              </div>
            </div>

            <span className="font-bold text-[#0d6269]">
              Consistently improving trend
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Weekly Summary Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-8 text-center space-y-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900">Your weekly summary</h3>
          <p className="text-xs text-slate-500 mt-1">18–24 October 2024</p>
        </div>

        <div>
          <button
            onClick={() => setPatientView('history')}
            className="px-6 py-3 rounded-xl font-semibold text-sm bg-[#0d6269] text-white hover:bg-teal-800 shadow-xs transition-colors"
          >
            Overall summary
          </button>
        </div>
      </div>
    </div>
  );
};
