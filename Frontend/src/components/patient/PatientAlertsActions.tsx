import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { 
  Info, 
  Phone, 
  Search, 
  ChevronDown, 
  ArrowUpDown, 
  ArrowRight,
  AlertTriangle
} from 'lucide-react';

export const PatientAlertsActions: React.FC = () => {
  const { patientAlerts, navigateToPatientAlertDetail } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const filtered = patientAlerts.filter((a) => {
    const matchesSearch = 
      a.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || a.category.toLowerCase() === categoryFilter.toLowerCase();
    const matchesStatus = statusFilter === 'all' || a.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Demonstration notice banner */}
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

      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-[#0d6269] tracking-tight">
          Alerts & Actions
        </h1>
        <p className="text-slate-500 mt-1 text-sm">
          Understand your alerts and find the right actions for each situation.
        </p>
      </div>

      {/* Emergency Hotline Banner */}
      <div className="bg-[#fff1f2] border border-rose-200/80 rounded-2xl p-5 flex items-start gap-4">
        <div className="p-1 rounded-lg text-rose-600 mt-0.5">
          <Phone className="w-5 h-5" />
        </div>
        <div>
          <h4 className="font-bold text-rose-900 text-sm">
            Chest pain, shortness of breath or another severe symptom? Call 15 or 112.
          </h4>
          <p className="text-xs text-rose-700 mt-0.5">
            Do not wait for a portal response. روض is not an emergency service.
          </p>
        </div>
      </div>

      {/* Main Alerts Table Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        {/* Card Header & Controls */}
        <div className="p-6 border-b border-slate-100 space-y-4">
          <div className="flex items-center justify-between text-xs">
            <h3 className="text-base font-bold text-slate-900">
              {patientAlerts.length} example alerts
            </h3>
            <span className="text-slate-400">Most urgent to least urgent</span>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-1">
            {/* Search */}
            <div className="relative flex-1 max-w-sm">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search alerts"
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs placeholder:text-slate-400 focus:outline-none focus:bg-white focus:ring-2 focus:ring-[#0d6269]/20"
              />
            </div>

            {/* Category Dropdown */}
            <div className="relative">
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="appearance-none bg-slate-50 border border-slate-200 rounded-xl pl-3.5 pr-8 py-2 text-xs font-semibold text-slate-700 cursor-pointer focus:outline-none focus:bg-white"
              >
                <option value="all">All categories</option>
                <option value="symptoms">Symptoms</option>
                <option value="readings">Readings</option>
                <option value="device">Device</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            {/* Status Dropdown */}
            <div className="relative">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="appearance-none bg-slate-50 border border-slate-200 rounded-xl pl-3.5 pr-8 py-2 text-xs font-semibold text-slate-700 cursor-pointer focus:outline-none focus:bg-white"
              >
                <option value="all">All statuses</option>
                <option value="action_needed">Action needed</option>
                <option value="review_needed">Review needed</option>
                <option value="check_needed">Check needed</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            {/* Severity Sort Button */}
            <button className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100">
              <span>Highest severity first</span>
              <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#f0f7f9] border-b border-slate-200/60 text-slate-600 font-bold">
                <th className="py-3 px-6">Level ↓</th>
                <th className="py-3 px-6">Category</th>
                <th className="py-3 px-6">Alert</th>
                <th className="py-3 px-6">Date / time</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((alert) => (
                <tr 
                  key={alert.id}
                  onClick={() => navigateToPatientAlertDetail(alert.id)}
                  className="hover:bg-slate-50/70 transition-colors cursor-pointer group"
                >
                  <td className="py-4 px-6">
                    <Badge variant={alert.level as any}>
                      {alert.level === 'emergency' && <AlertTriangle className="w-3 h-3 text-rose-600" />}
                      {alert.level === 'caution' && <AlertTriangle className="w-3 h-3 text-amber-600" />}
                      {alert.level === 'information' && <Info className="w-3 h-3 text-sky-600" />}
                      {alert.levelLabel}
                    </Badge>
                  </td>
                  <td className="py-4 px-6 font-medium text-slate-600">
                    {alert.category}
                  </td>
                  <td className="py-4 px-6">
                    <p className="font-bold text-slate-900 group-hover:text-teal-800 transition-colors text-sm">
                      {alert.title}
                    </p>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Example {alert.code}
                    </p>
                  </td>
                  <td className="py-4 px-6 text-slate-600 whitespace-pre-line font-medium">
                    {alert.dateTime}
                  </td>
                  <td className="py-4 px-6">
                    <Badge variant={alert.status}>
                      {alert.statusLabel}
                    </Badge>
                  </td>
                  <td className="py-4 px-6 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigateToPatientAlertDetail(alert.id);
                      }}
                      className="inline-flex items-center gap-1 font-bold text-xs text-[#0d6269] hover:text-teal-900 transition-colors"
                    >
                      <span>View details</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="p-4 px-6 bg-white border-t border-slate-100 text-xs text-slate-400">
          Showing {filtered.length} of {patientAlerts.length} alerts • Demonstration scenarios only
        </div>
      </div>

      {/* Explainer Cards Grid (2 cols) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-2">
          <h4 className="font-bold text-slate-900 text-sm">Level indicates priority</h4>
          <p className="text-xs text-slate-600 leading-relaxed">
            Emergency: act immediately. Caution: request a review. Information: check a practical issue.
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-2">
          <h4 className="font-bold text-slate-900 text-sm">Status indicates follow-up</h4>
          <p className="text-xs text-slate-600 leading-relaxed">
            “Action needed,” “Review needed” and “Check needed” describe the pending action, not alert severity.
          </p>
        </div>
      </div>
    </div>
  );
};
