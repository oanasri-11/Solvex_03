import React, { useMemo } from 'react';
import { useApp } from '../../context/AppContext';
import { BPLineChart } from '../charts/BPLineChart';
import { CheckCheck, Send, AlertTriangle } from 'lucide-react';

interface BadgeProps {
  variant: 'normal' | 'borderline' | 'moderately_high' | 'high' | 'crisis';
  children: React.ReactNode;
}

const Badge: React.FC<BadgeProps> = ({ variant, children }) => {
  const variantStyles: Record<string, string> = {
    normal: 'bg-emerald-50 text-emerald-800 border-emerald-100',
    borderline: 'bg-amber-50 text-amber-800 border-amber-100',
    moderately_high: 'bg-orange-50 text-orange-800 border-orange-100',
    high: 'bg-red-50 text-red-800 border-red-100',
    crisis: 'bg-rose-50 text-rose-800 border-rose-100',
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${variantStyles[variant] || variantStyles.normal}`}>
      {children}
    </span>
  );
};

export const PatientHistoryTrends: React.FC = () => {
  const { aminaReadings, patientSummary, doctorName, doctorSpeciality } = useApp();

  // Transform readings for chart (last 14 days, chronological order for BPLineChart)
  const chartData = useMemo(() => {
    if (!aminaReadings || aminaReadings.length === 0) return [];
    // Take last 14 readings, reverse to chronological order (oldest first)
    return aminaReadings
      .slice(0, 14)
      .reverse()
      .map((r) => ({
        label: r.date,
        systolic: r.systolic,
        diastolic: r.diastolic,
        isManual: r.isManual,
      }));
  }, [aminaReadings]);

  // Compute stats from real readings
  const computedStats = useMemo(() => {
    if (!aminaReadings || aminaReadings.length === 0) {
      return {
        morningAvgSys: 0,
        morningAvgDia: 0,
        eveningAvgSys: 0,
        eveningAvgDia: 0,
        adherencePct: 0,
        consistencyPct: 0,
      };
    }

    const recent14 = aminaReadings.slice(0, 14);
    const morningReadings = recent14.filter(r => r.period === 'Morning');
    const eveningReadings = recent14.filter(r => r.period === 'Evening');

    const morningAvgSys = morningReadings.length > 0
      ? Math.round(morningReadings.reduce((sum, r) => sum + r.systolic, 0) / morningReadings.length)
      : 0;
    const morningAvgDia = morningReadings.length > 0
      ? Math.round(morningReadings.reduce((sum, r) => sum + r.diastolic, 0) / morningReadings.length)
      : 0;
    const eveningAvgSys = eveningReadings.length > 0
      ? Math.round(eveningReadings.reduce((sum, r) => sum + r.systolic, 0) / eveningReadings.length)
      : 0;
    const eveningAvgDia = eveningReadings.length > 0
      ? Math.round(eveningReadings.reduce((sum, r) => sum + r.diastolic, 0) / eveningReadings.length)
      : 0;

    // Adherence: expected 2 readings/day * 14 days = 28, actual = recent14.length
    const expectedReadings = 28;
    const adherencePct = Math.min(100, Math.round((recent14.length / expectedReadings) * 100));

    // Consistency: percentage of readings within target (using summary target or default 130/80)
    const targetSys = patientSummary?.target?.systolic ?? 130;
    const targetDia = patientSummary?.target?.diastolic ?? 80;
    const withinTarget = recent14.filter(r => r.systolic < targetSys && r.diastolic < targetDia).length;
    const consistencyPct = recent14.length > 0 ? Math.round((withinTarget / recent14.length) * 100) : 0;

    return {
      morningAvgSys,
      morningAvgDia,
      eveningAvgSys,
      eveningAvgDia,
      adherencePct,
      consistencyPct,
    };
  }, [aminaReadings, patientSummary]);

  // Get target from summary or use default
  const targetSys = patientSummary?.target?.systolic ?? 130;
  const targetDia = patientSummary?.target?.diastolic ?? 80;

  // Get latest reading from summary or compute from readings
  const latestReading = patientSummary?.latest_reading ?? (aminaReadings?.[0] ? {
    systolic: aminaReadings[0].systolic,
    diastolic: aminaReadings[0].diastolic,
    pulse: aminaReadings[0].pulse,
    classification: aminaReadings[0].classification,
  } : null);

  // Get next appointment from summary or use placeholder
  const nextAppointment = patientSummary?.next_appointment;

  // Get doctor info from summary or use layout state
  const doctorInfo = patientSummary?.doctor ?? {
    name: doctorName || 'Doctor',
    speciality: doctorSpeciality || 'Telemonitoring',
  };

  const handleSendReport = () => {
    // TODO: Implement report sending to doctor
    alert('Report sent to Dr. ' + doctorInfo.name);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold text-teal-800 uppercase tracking-wider block mb-1">
            CLINICAL HISTORY & TRENDS
          </span>
          <h1 className="text-2xl font-bold text-slate-900">Blood Pressure History</h1>
          <p className="text-sm text-slate-500 mt-1">
            14-day longitudinal view · Interactive chart · Consultation-ready summary
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="px-4 py-2 rounded-xl font-semibold text-sm bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 shadow-xs transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Chart (7 cols) + Consultation Summary (5 cols) */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left Column: Interactive Chart & Reading Log (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Interactive Blood Pressure Chart */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <div>
                <span className="text-[10px] font-bold text-teal-800 uppercase tracking-wider block mb-1">
                  TREND ANALYSIS
                </span>
                <h3 className="text-lg font-bold text-slate-900">14-Day Blood Pressure Trend</h3>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-xs">
                  <span className="w-3 h-3 rounded-full bg-[#0d6269]"></span>
                  <span className="text-slate-600">Systolic</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="w-3 h-3 rounded-full bg-teal-400"></span>
                  <span className="text-slate-600">Diastolic</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="w-3 h-3 rounded-full bg-amber-400"></span>
                  <span className="text-slate-600">Target: {targetSys}/{targetDia}</span>
                </div>
              </div>
            </div>

            {/* BPLineChart Component - Interactive SVG with hover tooltips */}
            <div className="h-[380px]">
              <BPLineChart
                data={chartData}
                showTargetZone={true}
                targetMin={targetDia}
                targetMax={targetSys}
                height={380}
                showLegend={true}
                variant="patient"
              />
            </div>

            {/* Chart Insights */}
            <div className="mt-6 pt-6 border-t border-slate-100 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="p-3 bg-slate-50/50 rounded-xl">
                <p className="text-2xl font-bold text-slate-900">{computedStats.morningAvgSys}/{computedStats.morningAvgDia}</p>
                <p className="text-[11px] text-slate-500">Morning Average</p>
              </div>
              <div className="p-3 bg-slate-50/50 rounded-xl">
                <p className="text-2xl font-bold text-slate-900">{computedStats.eveningAvgSys}/{computedStats.eveningAvgDia}</p>
                <p className="text-[11px] text-slate-500">Evening Average</p>
              </div>
              <div className="p-3 bg-slate-50/50 rounded-xl">
                <p className="text-2xl font-bold text-teal-700">{computedStats.adherencePct}%</p>
                <p className="text-[11px] text-slate-500">Adherence (14 days)</p>
              </div>
              <div className="p-3 bg-slate-50/50 rounded-xl">
                <p className="text-2xl font-bold text-emerald-700">{computedStats.consistencyPct}%</p>
                <p className="text-[11px] text-slate-500">Within Target</p>
              </div>
            </div>
          </div>

          {/* Reading Log Table */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <span className="text-[10px] font-bold text-teal-800 uppercase tracking-wider block mb-1">
                  READING LOG
                </span>
                <h3 className="text-lg font-bold text-slate-900">Recent Measurements</h3>
              </div>
              <span className="text-xs text-slate-400">
                Showing {aminaReadings?.length || 0} of 28 readings (14 days)
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50/50 text-left text-[10px] font-bold uppercase tracking-wider text-slate-500">
                    <th className="p-3">DATE & TIME</th>
                    <th className="p-3">BP (mmHg)</th>
                    <th className="p-3">PULSE</th>
                    <th className="p-3">CONTEXT</th>
                    <th className="p-3 text-right">CLASSIFICATION</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {aminaReadings?.map((reading) => (
                    <tr key={reading.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="p-3.5">
                        <p className="font-bold text-slate-900">{reading.date}</p>
                        <p className="text-[11px] text-slate-400">{reading.time} ({reading.period})</p>
                      </td>
                      <td className="p-3.5 font-bold text-slate-900 text-sm">
                        {reading.systolic} / {reading.diastolic} <span className="text-[10px] text-slate-400 font-normal">mmHg</span>
                      </td>
                      <td className="p-3.5 text-slate-600 font-medium">
                        {reading.pulse} bpm
                      </td>
                      <td className="p-3.5 text-slate-600">
                        {reading.context || 'Regular activity'}
                      </td>
                      <td className="p-3.5 text-right">
                        <Badge variant={reading.classification}>
                          ● {reading.classificationLabel}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-3 bg-white border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
              <span>Showing {aminaReadings?.length || 0} of 28 readings (14 days)</span>
              <button className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50">
                Load full history
              </button>
            </div>
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

          {/* Summary Metadata */}
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Next appointment:</span>
              <span className="font-bold text-slate-900">
                {nextAppointment
                  ? `${nextAppointment.date} at ${nextAppointment.time}`
                  : 'Not scheduled'}
              </span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Reading period:</span>
              <span className="font-bold text-slate-900">
                {aminaReadings?.length > 0
                  ? `${aminaReadings[aminaReadings.length - 1]?.date} – ${aminaReadings[0]?.date} (${Math.min(14, aminaReadings.length)} days)`
                  : 'No readings yet'}
              </span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Supervising doctor:</span>
              <span className="font-bold text-slate-900">
                Dr. {doctorInfo.name} ({doctorInfo.speciality})
              </span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500">Data transfer status:</span>
              <span className="font-bold text-emerald-700 flex items-center gap-1">
                <CheckCheck className="w-4 h-4" />
                Updated in real time
              </span>
            </div>
          </div>

          {/* Key Clinical Metrics */}
          <div className="p-4 bg-slate-50/50 rounded-xl space-y-3">
            <h4 className="text-sm font-bold text-slate-700">Key Metrics for Dr. {doctorInfo.name}</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-slate-500 block">Target BP</span>
                <span className="font-bold text-slate-900">{targetSys}/{targetDia} mmHg</span>
              </div>
              <div>
                <span className="text-slate-500 block">Current Average</span>
                <span className="font-bold text-slate-900">
                  {computedStats.morningAvgSys > 0 || computedStats.eveningAvgSys > 0
                    ? `${Math.round((computedStats.morningAvgSys + computedStats.eveningAvgSys) / 2)}/${Math.round((computedStats.morningAvgDia + computedStats.eveningAvgDia) / 2)} mmHg`
                    : '—'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block">Adherence</span>
                <span className="font-bold text-teal-700">{computedStats.adherencePct}%</span>
              </div>
              <div>
                <span className="text-slate-500 block">Control Rate</span>
                <span className="font-bold text-emerald-700">{computedStats.consistencyPct}%</span>
              </div>
            </div>
          </div>

          {/* Latest Reading Alert */}
          {latestReading && latestReading.classification && latestReading.classification !== 'normal' && (
            <div className="p-3 bg-amber-50 border border-amber-100 rounded-xl flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
              <div className="text-xs text-amber-800">
                <p className="font-bold">Latest reading: {latestReading.classification}</p>
                <p>{latestReading.systolic}/{latestReading.diastolic} mmHg</p>
                <p className="mt-1">Consider discussing with Dr. {doctorInfo.name} at next consultation.</p>
              </div>
            </div>
          )}

          {/* Send Full Report Button */}
          <button
            type="button"
            onClick={handleSendReport}
            className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-bold text-sm bg-[#0d6269] text-white hover:bg-teal-800 shadow-sm transition-colors"
          >
            <Send className="w-4 h-4" />
            <span>Send full report to Dr. {doctorInfo.name}</span>
          </button>

          <p className="text-[11px] text-slate-400 text-center leading-relaxed">
            A structured summary following the SFHT protocol will be added to your medical record
            and shared with <strong>Dr. {doctorInfo.name}</strong> ({doctorInfo.speciality}).
          </p>
        </div>
      </div>
    </div>
  );
};