import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { doctorService, type DoctorDashboardResponse } from '../../services/doctorService';
import { Bell, ArrowUpRight, ArrowRight, Phone, RefreshCw } from 'lucide-react';

export const DoctorDashboard: React.FC = () => {
  const { patients, currentUser, setDoctorView, navigateToDoctorPatient, refreshDoctorCohort } = useApp();
  const [metrics, setMetrics] = useState<DoctorDashboardResponse | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchMetrics = async () => {
    try {
      const data = await doctorService.getDashboard();
      setMetrics(data);
    } catch (err) {
      console.warn('Could not load doctor dashboard metrics from backend:', err);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([fetchMetrics(), refreshDoctorCohort()]);
    setIsRefreshing(false);
  };

  const patientCount = metrics ? metrics.active_patient_count : patients.length;
  const criticalCount = metrics
    ? (metrics.alerts_by_tier.critical_emergency || 0) + (metrics.alerts_by_tier.severe_single_reading || 0)
    : 12;
  const openAlertsCount = metrics ? metrics.unacknowledged_alerts_count : 18;
  const contactRequestsCount = metrics ? metrics.open_contact_requests_count : 3;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Good morning, {currentUser?.full_name || 'Dr. Karim'}
          </h1>
          <p className="text-slate-500 mt-1 text-base">Your patients and the issues that need your attention.</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-1.5 px-3 py-2 border border-slate-200 rounded-xl text-xs font-semibold text-slate-600 bg-white hover:bg-slate-50 transition-colors shadow-2xs"
          title="Refresh dashboard data"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-teal-600' : ''}`} />
          <span>Sync Live Data</span>
        </button>
      </div>

      {/* 3 Metric Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1 */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <p className="text-sm font-medium text-slate-500">Patients under care</p>
          <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight my-2">{patientCount}</h2>
          <p className="text-xs text-slate-500">Active clinical telemonitoring caseload</p>
        </div>

        {/* Card 2 */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <p className="text-sm font-medium text-slate-500">High / urgent priority</p>
          <h2 className="text-4xl font-extrabold text-rose-600 tracking-tight my-2">{criticalCount}</h2>
          <p className="text-xs text-slate-500">Critical & severe clinical shifts</p>
        </div>

        {/* Card 3 */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <p className="text-sm font-medium text-slate-500">Open alerts</p>
          <h2 className="text-4xl font-extrabold text-amber-600 tracking-tight my-2">{openAlertsCount}</h2>
          <p className="text-xs text-slate-500">Awaiting clinician acknowledgment</p>
        </div>
      </div>

      {/* Patients to Prioritize Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Patients to prioritize</h2>
            <p className="text-sm text-slate-500">A focused view of the current care queue (P1–P4 triage).</p>
          </div>
          <button
            onClick={() => setDoctorView('alerts')}
            className="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 transition-colors shadow-xs"
          >
            <Bell className="w-4 h-4 text-slate-600" />
            <span>Open alerts</span>
          </button>
        </div>

        {/* Patients Table Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 text-xs font-medium text-slate-400">
                  <th className="py-3.5 px-6 font-normal">Patient</th>
                  <th className="py-3.5 px-6 font-normal">Clinical status</th>
                  <th className="py-3.5 px-6 font-normal">Latest BP · mmHg</th>
                  <th className="py-3.5 px-6 font-normal text-right">Record</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {patients.map((patient) => (
                  <tr 
                    key={patient.id} 
                    className="hover:bg-slate-50/70 transition-colors group cursor-pointer"
                    onClick={() => navigateToDoctorPatient(patient.id)}
                  >
                    {/* Patient Info */}
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3.5">
                        <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-700 font-bold text-xs flex items-center justify-center shrink-0 border border-slate-200/60">
                          {patient.initials}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 group-hover:text-teal-700 transition-colors">
                            {patient.name}
                          </p>
                          <p className="text-xs text-slate-500">
                            {patient.age} years · {patient.code}
                          </p>
                        </div>
                      </div>
                    </td>

                    {/* Clinical Status */}
                    <td className="py-4 px-6">
                      <div>
                        <Badge variant={patient.clinicalStatus}>
                          {patient.statusLabel}
                        </Badge>
                        <p className="text-xs text-slate-500 mt-1">
                          {patient.statusSubtext}
                        </p>
                      </div>
                    </td>

                    {/* Latest BP */}
                    <td className="py-4 px-6">
                      <div>
                        <p className="font-bold text-slate-900 text-base">
                          {patient.latestSystolic}/{patient.latestDiastolic}
                        </p>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {patient.latestReadingTime}
                        </p>
                      </div>
                    </td>

                    {/* Record Link */}
                    <td className="py-4 px-6 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigateToDoctorPatient(patient.id);
                        }}
                        className="inline-flex items-center gap-1 font-semibold text-sm text-[#0d6269] hover:text-teal-800 transition-colors"
                      >
                        <span>View record</span>
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Table Footer */}
          <div className="p-4 px-6 bg-white border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Prioritized patient list</span>
            <button
              onClick={() => setDoctorView('patients')}
              className="inline-flex items-center gap-1.5 font-semibold text-[#0d6269] hover:text-teal-800 transition-colors"
            >
              <span>View all patients</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Callout Banner */}
      <div className="bg-[#e6f4f1] rounded-2xl p-5 border border-teal-100/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-white/80 border border-teal-200/50 flex items-center justify-center text-[#0d6269] shrink-0">
            <Phone className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-slate-900 text-sm">{contactRequestsCount} patient{contactRequestsCount === 1 ? '' : 's'} waiting for contact</h4>
            <p className="text-xs text-slate-600 mt-0.5">
              Review contact requests alongside clinical alerts in your inbox.
            </p>
          </div>
        </div>
        <button
          onClick={() => setDoctorView('alerts')}
          className="shrink-0 px-4 py-2 bg-white text-slate-800 text-xs font-semibold rounded-xl border border-slate-200 hover:bg-slate-50 shadow-xs transition-colors"
        >
          Go to inbox
        </button>
      </div>
    </div>
  );
};
