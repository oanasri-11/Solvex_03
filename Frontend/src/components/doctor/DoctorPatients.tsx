import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { Search, ChevronDown, ArrowUpRight, ArrowRight } from 'lucide-react';

export const DoctorPatients: React.FC = () => {
  const { patients, navigateToDoctorPatient } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [page, setPage] = useState(1);

  const filteredPatients = patients.filter((p) => {
    const matchesSearch = 
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || p.clinicalStatus === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Patients</h1>
        <p className="text-slate-500 mt-1 text-sm">Find a patient and open their clinical record.</p>
      </div>

      {/* Search and Filters Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by patient name or ID"
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] transition-all"
          />
        </div>

        {/* Status Dropdown */}
        <div className="relative">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="appearance-none bg-white border border-slate-200 rounded-xl pl-4 pr-10 py-2.5 text-sm font-medium text-slate-700 cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] transition-all shadow-xs"
          >
            <option value="all">All clinical statuses</option>
            <option value="crisis">Crisis only</option>
            <option value="high_priority">High priority</option>
            <option value="urgent">Urgent</option>
            <option value="within_target">Within target</option>
          </select>
          <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>

      {/* Table Section Header */}
      <div className="flex items-center justify-between text-sm">
        <h3 className="font-bold text-slate-900">148 patients under care</h3>
        <span className="text-xs text-slate-400">Sorted by clinical priority</span>
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
              {filteredPatients.map((patient) => (
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
                          {patient.id === 'p4' ? 'Telemonitoring' : `${patient.age} years · ${patient.code}`}
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

                  {/* Action */}
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

        {/* Pagination Footer */}
        <div className="p-4 px-6 bg-white border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {filteredPatients.length} of 148 patients</span>
          <div className="flex items-center gap-3 font-medium">
            <button
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              className="text-slate-500 hover:text-slate-900 disabled:opacity-40 transition-colors"
            >
              Previous
            </button>
            <span className={`px-2 py-0.5 rounded ${page === 1 ? 'font-bold text-slate-900' : 'text-slate-500'}`}>
              1
            </span>
            <span className={`px-2 py-0.5 rounded ${page === 2 ? 'font-bold text-slate-900' : 'text-slate-500'}`}>
              2
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              className="inline-flex items-center gap-1 text-[#0d6269] hover:text-teal-900 font-semibold transition-colors"
            >
              <span>Next</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom informational note */}
      <p className="text-xs text-slate-400">
        Blood pressure is shown in mmHg. Open a patient record for readings and active alerts.
      </p>
    </div>
  );
};
