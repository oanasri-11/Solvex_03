import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { BPLineChart } from '../charts/BPLineChart';
import { Badge } from '../common/Badge';
import { patientService, type PatientSummary } from '../../services/patientService';
import { 
  Activity, 
  CheckCircle2, 
  ArrowDown, 
  Heart,
  TrendingDown,
  AlertTriangle,
  Loader2
} from 'lucide-react';

export const PatientHome: React.FC = () => {
  const { setPatientView, aminaReadings, currentUser } = useApp();
  const [summary, setSummary] = useState<PatientSummary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    setLoadingSummary(true);
    patientService.getOwnSummary()
      .then(res => {
        if (res) setSummary(res);
      })
      .catch(err => {
        console.warn('Could not load patient summary:', err);
      })
      .finally(() => setLoadingSummary(false));
  }, []);

  const latestReading = aminaReadings && aminaReadings.length > 0 ? aminaReadings[0] : null;
  const systolic = latestReading ? latestReading.systolic : 128;
  const diastolic = latestReading ? latestReading.diastolic : 82;
  const pulse = latestReading ? latestReading.pulse : 72;
  const isHigh = systolic >= 140 || diastolic >= 90;

  // Transform readings to trend points for chart
  const chartPoints = aminaReadings && aminaReadings.length > 0
    ? aminaReadings.slice(0, 7).reverse().map(r => ({
        label: r.date.split(',')[0] || r.date,
        systolic: r.systolic,
        diastolic: r.diastolic,
        isManual: r.isManual,
      }))
    : [];

  const firstName = currentUser?.full_name ? currentUser.full_name.split(' ')[0] : 'Amina';

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Greeting Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Hello, {firstName}
          </h1>
          <p className="text-slate-500 mt-1 text-sm font-medium">
            {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
        {loadingSummary && <Loader2 className="w-4 h-4 animate-spin text-teal-600" />}
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
                {latestReading ? `${latestReading.date}, ${latestReading.time}` : 'Recent measurement'}
              </Badge>
            </div>

            {/* Reading Value */}
            <div className="flex items-baseline gap-2 my-2">
              <span className="text-5xl font-black text-slate-900 tracking-tight">{systolic}</span>
              <span className="text-3xl font-light text-slate-400">/</span>
              <span className="text-5xl font-black text-slate-900 tracking-tight">{diastolic}</span>
              <span className="text-sm font-medium text-slate-500 ml-1">mmHg</span>
            </div>

            {/* Pulse */}
            <div className="flex items-center gap-2 text-sm text-slate-600 mt-2 mb-6">
              <Heart className="w-4 h-4 text-rose-500 fill-rose-500" />
              <span className="font-bold text-slate-900">{pulse} bpm</span>
              <span className="text-xs text-slate-400">({latestReading?.isManual ? 'Manual input' : 'Connected BLE monitor'})</span>
            </div>
          </div>

          {/* Target Status Banner */}
          <div className={`${isHigh ? 'bg-amber-50 border-amber-200/70 text-amber-950' : 'bg-[#dcf4ed] border-teal-200/70 text-emerald-950'} border rounded-xl p-4 flex items-start gap-3`}>
            {isHigh ? (
              <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
            ) : (
              <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
            )}
            <div>
              <h4 className="font-bold text-sm">
                {summary?.plain_language_status || (isHigh ? 'Slightly above target threshold' : 'Within target range')}
              </h4>
              <p className="text-xs mt-0.5 leading-relaxed opacity-90">
                Target agreed with your clinical team: &lt;{summary?.target?.systolic || 135}/{summary?.target?.diastolic || 85} mmHg.
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
              <p className="text-xs text-slate-500 mt-0.5">Continuous telemonitoring curve</p>
            </div>

            <Badge variant="within_target" icon={<ArrowDown className="w-3 h-3 text-teal-700" />}>
              Active protocol cycle
            </Badge>
          </div>

          {/* Chart Container */}
          <div className="bg-[#f8fafd] rounded-xl p-4 border border-slate-100">
            <BPLineChart 
              data={chartPoints}
              showTargetZone={true}
              targetMin={summary?.target ? summary.target.diastolic : 80}
              targetMax={summary?.target ? summary.target.systolic : 135}
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
              {aminaReadings.length} reading{aminaReadings.length === 1 ? '' : 's'} recorded
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Weekly Summary Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-8 text-center space-y-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900">Your health trend summary</h3>
          <p className="text-xs text-slate-500 mt-1">
            {summary?.fourteen_day_average
              ? `14-day average: ${Math.round(summary.fourteen_day_average.systolic)}/${Math.round(summary.fourteen_day_average.diastolic)} mmHg across ${summary.total_readings_last_14d || aminaReadings.length} readings`
              : 'Review your complete log of home blood pressure measurements.'}
          </p>
        </div>

        <div>
          <button
            onClick={() => setPatientView('history')}
            className="px-6 py-3 rounded-xl font-semibold text-sm bg-[#0d6269] text-white hover:bg-teal-800 shadow-xs transition-colors"
          >
            View Full Readings History
          </button>
        </div>
      </div>
    </div>
  );
};
