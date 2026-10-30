import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { 
  Heart, 
  Sun, 
  Moon, 
  Calendar, 
  Award, 
  Filter, 
  CalendarDays, 
  ArrowUpRight, 
  Send, 
  CheckCheck,
  CheckCircle2
} from 'lucide-react';

export const PatientHistoryTrends: React.FC = () => {
  const { aminaReadings } = useApp();
  const [timeFilter, setTimeFilter] = useState('14 days');
  const [dayPeriodFilter, setDayPeriodFilter] = useState<'both' | 'morning' | 'evening'>('both');
  const [reportSent, setReportSent] = useState(false);

  const handleSendReport = () => {
    setReportSent(true);
    setTimeout(() => setReportSent(false), 3500);
  };

  const chartPoints = [
    { label: '11 Oct', sys: 138, dia: 86, type: 'borderline' },
    { label: '12 Oct', sys: 136, dia: 84, type: 'borderline' },
    { label: '13 Oct', sys: 142, dia: 88, type: 'high' },
    { label: '14 Oct', sys: 139, dia: 87, type: 'borderline' },
    { label: '15 Oct', sys: 128, dia: 80, type: 'target' },
    { label: '16 Oct', sys: 131, dia: 82, type: 'borderline' },
    { label: '17 Oct', sys: 126, dia: 79, type: 'target' },
    { label: '18 Oct', sys: 129, dia: 81, type: 'target' },
    { label: '19 Oct', sys: 136, dia: 83, type: 'borderline' },
    { label: '20 Oct', sys: 125, dia: 78, type: 'target' },
    { label: '21 Oct', sys: 124, dia: 77, type: 'target' },
    { label: '22 Oct', sys: 135, dia: 83, type: 'borderline' },
    { label: '23 Oct', sys: 132, dia: 81, type: 'borderline' },
    { label: 'Today', sys: 128, dia: 80, type: 'target', isToday: true }
  ];

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Toast */}
      {reportSent && (
        <div className="fixed bottom-6 right-6 bg-[#0d6269] text-white px-5 py-3.5 rounded-xl shadow-xl flex items-center gap-2 text-sm z-50 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-emerald-300" />
          <span>Full clinical report successfully dispatched to Dr. Philippe Laurent!</span>
        </div>
      )}

      {/* Top Header & Range Filters */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="text-xs font-bold text-[#0d6269] uppercase tracking-wider mb-1 flex items-center gap-2">
            <span>HOME BLOOD PRESSURE</span>
            <span className="text-slate-400">•</span>
            <span className="text-slate-500 font-normal">3 readings each morning / evening</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            History & Trends
          </h1>
        </div>

        {/* Time Filter Pills */}
        <div className="flex items-center bg-white p-1 rounded-full border border-slate-200/80 shadow-xs text-xs font-semibold">
          {['7 days', '14 days', '30 days', '3 months', 'Custom'].map((period) => (
            <button
              key={period}
              onClick={() => setTimeFilter(period)}
              className={`px-3.5 py-1.5 rounded-full transition-all ${
                timeFilter === period
                  ? 'bg-[#0d6269] text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {period}
            </button>
          ))}
        </div>
      </div>

      {/* Green Banner: Improving trend confirmed */}
      <div className="bg-[#dcf4ed] border border-teal-200/70 rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-full bg-[#0d6269] text-white flex items-center justify-center shrink-0 shadow-xs">
            <Heart className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-extrabold text-slate-900 text-base">
                Improving trend confirmed
              </h3>
              <Badge variant="within_target">
                Optimal stability
              </Badge>
            </div>
            <p className="text-xs text-teal-950/80 leading-relaxed max-w-2xl">
              Gradual decrease of 6 mmHg over the past 14 days. 88% of readings are within the target agreed with Dr. Laurent (SYS &lt; 135 mmHg).
            </p>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-xs rounded-xl p-3 px-5 border border-teal-100 text-right shrink-0">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Latest Reading</p>
          <div className="flex items-center gap-2 justify-end mt-0.5">
            <span className="text-2xl font-black text-slate-900">128 / 82</span>
            <span className="text-xs text-slate-500 font-medium">mmHg</span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block ml-0.5"></span>
          </div>
        </div>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Morning Average */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-bold uppercase tracking-wider">
              <Sun className="w-4 h-4 text-amber-500" />
              <span>Morning Average</span>
            </div>
            <Badge variant="within_target">On target</Badge>
          </div>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-3xl font-black text-slate-900">126/81</span>
            <span className="text-xs text-slate-500">mmHg</span>
          </div>
          <p className="text-xs text-[#0d6269] font-medium">↘ -4 mmHg vs previous fortnight</p>
        </div>

        {/* Evening Average */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-bold uppercase tracking-wider">
              <Moon className="w-4 h-4 text-indigo-500" />
              <span>Evening Average</span>
            </div>
            <Badge variant="outline">Stable</Badge>
          </div>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-3xl font-black text-slate-900">130/84</span>
            <span className="text-xs text-slate-500">mmHg</span>
          </div>
          <p className="text-xs text-slate-500">Moderate physiological variation</p>
        </div>

        {/* Protocol Adherence */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-bold uppercase tracking-wider">
              <Calendar className="w-4 h-4 text-teal-600" />
              <span>Protocol Adherence</span>
            </div>
            <span className="text-xs font-bold text-slate-700">13/14</span>
          </div>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-3xl font-black text-slate-900">92%</span>
            <span className="text-xs text-slate-500">sessions completed</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
            <div className="bg-[#0d6269] h-full rounded-full" style={{ width: '92%' }}></div>
          </div>
        </div>

        {/* Consistency */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-bold uppercase tracking-wider">
              <Award className="w-4 h-4 text-amber-500" />
              <span>Consistency</span>
            </div>
            <Badge variant="within_target">Excellent</Badge>
          </div>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-3xl font-black text-slate-900">7</span>
            <span className="text-xs text-slate-500">consecutive days</span>
          </div>
          <p className="text-xs text-slate-500">No missed readings since last Friday</p>
        </div>
      </div>

      {/* Main Blood Pressure Chart (SYS / DIA) */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-xl font-bold text-slate-900">
              Blood pressure chart (SYS / DIA)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Clinical target range: 115–130 mmHg (Systolic)
            </p>
          </div>

          {/* Time of day toggles */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-semibold border border-slate-200/60">
            <button
              onClick={() => setDayPeriodFilter('both')}
              className={`px-3 py-1.5 rounded-lg transition-all ${dayPeriodFilter === 'both' ? 'bg-white text-slate-900 shadow-xs font-bold' : 'text-slate-600'}`}
            >
              ☀️ Morning & Evening
            </button>
            <button
              onClick={() => setDayPeriodFilter('morning')}
              className={`px-3 py-1.5 rounded-lg transition-all ${dayPeriodFilter === 'morning' ? 'bg-white text-slate-900 shadow-xs font-bold' : 'text-slate-600'}`}
            >
              🌅 Morning only
            </button>
            <button
              onClick={() => setDayPeriodFilter('evening')}
              className={`px-3 py-1.5 rounded-lg transition-all ${dayPeriodFilter === 'evening' ? 'bg-white text-slate-900 shadow-xs font-bold' : 'text-slate-600'}`}
            >
              🌙 Evening only
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-5 text-xs text-slate-600 flex-wrap">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#0d6269]"></span>
            <span>On target (&lt;130)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span>Borderline (130–139)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-600"></span>
            <span>High (≥140)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full border border-slate-600 bg-white"></span>
            <span>Manual entry</span>
          </div>
        </div>

        {/* Chart View with Target Shading and Current Hover Card */}
        <div className="relative pt-4">
          {/* Target Zone & Graph */}
          <div className="h-64 relative bg-[#fafcfb] rounded-xl border border-slate-100 overflow-hidden p-4">
            {/* SVG Interactive Line */}
            <svg viewBox="0 0 700 200" className="w-full h-full">
              {/* Target zone band 115 - 130 */}
              <rect x="0" y="80" width="700" height="40" fill="#e8f6f2" />
              <line x1="0" y1="80" x2="700" y2="80" stroke="#b6e3d6" strokeWidth="1" strokeDasharray="3 3" />
              <line x1="0" y1="120" x2="700" y2="120" stroke="#b6e3d6" strokeWidth="1" strokeDasharray="3 3" />

              {/* Grid lines */}
              <line x1="0" y1="40" x2="700" y2="40" stroke="#f1f5f9" strokeWidth="1" />
              <line x1="0" y1="160" x2="700" y2="160" stroke="#f1f5f9" strokeWidth="1" />

              {/* Diastolic bottom dashed line */}
              <polyline
                fill="none"
                stroke="#64748b"
                strokeWidth="2"
                strokeDasharray="4 3"
                points="20,150 70,156 120,150 170,152 220,165 270,162 320,168 370,165 420,160 470,170 520,172 570,158 620,162 670,164"
              />

              {/* Systolic main line */}
              <polyline
                fill="none"
                stroke="#0d6269"
                strokeWidth="2.5"
                points="20,70 70,75 120,60 170,68 220,105 270,95 320,110 370,100 420,72 470,112 520,115 570,80 620,90 670,102"
              />

              {/* Points */}
              {chartPoints.map((pt, idx) => {
                const x = 20 + idx * 50;
                const sysY = pt.sys === 142 ? 60 : pt.sys >= 135 ? 70 : pt.sys <= 126 ? 115 : 100;
                const color = pt.type === 'high' ? '#e11d48' : pt.type === 'borderline' ? '#f59e0b' : '#0d6269';

                return (
                  <circle
                    key={idx}
                    cx={x}
                    cy={sysY}
                    r={pt.isToday ? 5 : 4}
                    fill={color}
                    stroke="#ffffff"
                    strokeWidth="1.5"
                  />
                );
              })}
            </svg>

            {/* Floating Info card at top right for Today reading */}
            <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-xs border border-slate-200 rounded-xl p-3 shadow-md text-xs space-y-1">
              <div className="flex items-center justify-between gap-2">
                <span className="font-bold text-slate-800">Today • 08:10</span>
                <Badge variant="within_target">On target</Badge>
              </div>
              <div className="flex items-baseline gap-1 text-slate-900 font-extrabold text-sm">
                <span>Blood pressure:</span>
                <span className="text-base text-teal-800">128 / 82</span>
              </div>
              <div className="text-slate-500 flex items-center justify-between text-[11px]">
                <span>Heart rate: 68 bpm</span>
                <span className="text-emerald-600 font-medium">✓ 5-min rest</span>
              </div>
            </div>
          </div>

          {/* Dates Row */}
          <div className="flex justify-between text-[11px] text-slate-400 px-2 pt-2">
            {chartPoints.map((pt, i) => (
              <span key={i} className={pt.isToday ? 'font-bold text-slate-900' : ''}>
                {pt.label}
              </span>
            ))}
          </div>
        </div>

        {/* Footer info link */}
        <div className="flex items-center gap-2 text-xs text-slate-500 pt-2 border-t border-slate-100">
          <span>Reading the trend: The light green area shows the ideal range set in your treatment plan.</span>
          <a href="#thresholds" className="text-[#0d6269] font-bold hover:underline inline-flex items-center gap-1">
            <span>Understand clinical thresholds</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Two Column Grid: Detailed reading log & Consultation summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Detailed Reading Log (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Detailed reading log</h3>
              <p className="text-xs text-slate-500">All submitted readings and notes</p>
            </div>

            <div className="flex items-center gap-2">
              <button className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50">
                <Filter className="w-3.5 h-3.5" />
                <span>Filter</span>
              </button>
              <button className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50">
                <CalendarDays className="w-3.5 h-3.5" />
                <span>All dates</span>
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-bold uppercase tracking-wider">
                  <th className="pb-3 font-medium">DATE & TIME</th>
                  <th className="pb-3 font-medium">BP (SYS/DIA)</th>
                  <th className="pb-3 font-medium">PULSE</th>
                  <th className="pb-3 font-medium">CONTEXT & DOSE</th>
                  <th className="pb-3 font-medium text-right">CLASSIFICATION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {aminaReadings.map((reading) => (
                  <tr key={reading.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5">
                      <p className="font-bold text-slate-900">{reading.date}</p>
                      <p className="text-[11px] text-slate-400">{reading.time} ({reading.period})</p>
                    </td>
                    <td className="py-3.5 font-bold text-slate-900 text-sm">
                      {reading.systolic} / {reading.diastolic} <span className="text-[10px] text-slate-400 font-normal">mmHg</span>
                    </td>
                    <td className="py-3.5 text-slate-600 font-medium">
                      {reading.pulse} bpm
                    </td>
                    <td className="py-3.5 text-slate-600">
                      {reading.context || 'Regular activity'}
                    </td>
                    <td className="py-3.5 text-right">
                      <Badge variant={reading.classification as any}>
                        ● {reading.classificationLabel}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-3 bg-white border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span>Showing {aminaReadings.length} of 28 readings (14 days)</span>
            <button className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50">
              Load full history
            </button>
          </div>
        </div>

        {/* Right Column: Consultation Summary (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-6">
          <div>
            <span className="text-[10px] font-bold text-teal-800 uppercase tracking-wider block mb-1">
              SHARE WITH YOUR DOCTOR
            </span>
            <h3 className="text-xl font-bold text-slate-900">
              Consultation summary
            </h3>
          </div>

          {/* Doctor Profile Card */}
          <div className="bg-[#f8fafc] border border-slate-200/70 rounded-xl p-4 flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-full bg-teal-100 text-teal-900 font-bold text-sm flex items-center justify-center shrink-0 border border-teal-200">
              PL
            </div>
            <div>
              <h4 className="font-bold text-slate-900 text-sm">Dr Philippe Laurent</h4>
              <p className="text-xs text-slate-500">Lead cardiologist • University hospital</p>
              <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 font-semibold mt-0.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                Remote monitoring active
              </span>
            </div>
          </div>

          {/* Summary Metadata */}
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Next appointment:</span>
              <span className="font-bold text-slate-900">12 Nov 2024 at 10:30</span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Reading period:</span>
              <span className="font-bold text-slate-900">11 Oct – 24 Oct (14 days)</span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Data transfer status:</span>
              <span className="font-bold text-emerald-700 flex items-center gap-1">
                <CheckCheck className="w-4 h-4" />
                Updated in real time
              </span>
            </div>
          </div>

          {/* Send Full Report Button */}
          <button
            type="button"
            onClick={handleSendReport}
            className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-bold text-sm bg-[#0d6269] text-white hover:bg-teal-800 shadow-sm transition-colors"
          >
            <Send className="w-4 h-4" />
            <span>Send full report</span>
          </button>

          <p className="text-[11px] text-slate-400 text-center leading-relaxed">
            A structured summary following the SFHT protocol will be added to your medical record.
          </p>
        </div>
      </div>
    </div>
  );
};
