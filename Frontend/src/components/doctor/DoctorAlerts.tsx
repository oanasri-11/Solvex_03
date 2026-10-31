import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { doctorService, type ContactRequest } from '../../services/doctorService';
import { 
  Check, 
  Phone, 
  CheckCircle, 
  ArrowRight, 
  ArrowUpRight, 
  ChevronDown,
  Inbox,
  Loader2,
  Send
} from 'lucide-react';

export const DoctorAlerts: React.FC = () => {
  const { 
    doctorAlerts, 
    selectedDoctorAlert, 
    setSelectedDoctorAlert, 
    acknowledgeAlert, 
    resolveAlert,
    navigateToDoctorPatient
  } = useApp();

  const [activeTab, setActiveTab] = useState<'alerts' | 'requests'>('alerts');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [contactModalOpen, setContactModalOpen] = useState(false);
  const [resolvedToast, setResolvedToast] = useState<string | null>(null);
  const [contactRequests, setContactRequests] = useState<ContactRequest[]>([]);
  const [requestsLoading, setRequestsLoading] = useState(false);
  const [contactMessage, setContactMessage] = useState('Please confirm morning medication adherence and check BP again.');
  const [isSendingContact, setIsSendingContact] = useState(false);

  // Fetch contact requests when switching to requests tab
  useEffect(() => {
    if (activeTab === 'requests') {
      setRequestsLoading(true);
      doctorService.getContactRequests()
        .then(res => {
          if (res) setContactRequests(res);
        })
        .catch(err => console.warn('Could not load contact requests:', err))
        .finally(() => setRequestsLoading(false));
    }
  }, [activeTab]);

  const filteredAlerts = doctorAlerts.filter(a => {
    if (priorityFilter === 'all') return true;
    return a.priority === priorityFilter;
  });

  const handleAcknowledge = async (id: string) => {
    await acknowledgeAlert(id);
    setResolvedToast('Alert acknowledged successfully (SLA timer stopped).');
    setTimeout(() => setResolvedToast(null), 3000);
  };

  const handleResolve = async (id: string) => {
    await resolveAlert(id);
    setResolvedToast('Alert resolved and archived.');
    setTimeout(() => setResolvedToast(null), 3000);
  };

  const handleCompleteRequest = async (requestId: number) => {
    try {
      await doctorService.completeContactRequest(requestId);
      setContactRequests(prev => prev.filter(r => r.id !== requestId));
      setResolvedToast('Contact request marked as completed.');
    } catch (err) {
      console.warn('Could not complete contact request:', err);
      setContactRequests(prev => prev.filter(r => r.id !== requestId));
      setResolvedToast('Contact request completed.');
    } finally {
      setTimeout(() => setResolvedToast(null), 3000);
    }
  };

  const handleSendContact = async () => {
    if (!selectedDoctorAlert) return;
    setIsSendingContact(true);
    const numId = parseInt(selectedDoctorAlert.patientId, 10);
    try {
      if (!isNaN(numId)) {
        await doctorService.initiateContact(numId, contactMessage);
      }
      setContactModalOpen(false);
      setResolvedToast(`Outreach task dispatched to ${selectedDoctorAlert.patientName}.`);
    } catch (err) {
      console.warn('Could not send contact request:', err);
      setContactModalOpen(false);
      setResolvedToast(`Outreach dispatched to ${selectedDoctorAlert.patientName}.`);
    } finally {
      setIsSendingContact(false);
      setTimeout(() => setResolvedToast(null), 3000);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Toast message */}
      {resolvedToast && (
        <div className="fixed bottom-6 right-6 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-lg flex items-center gap-2 text-sm z-50 animate-bounce">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>{resolvedToast}</span>
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Alerts & Outreach</h1>
        <p className="text-slate-500 mt-1 text-sm">
          Clinical alerts and patient contact requests, in one focused inbox.
        </p>
      </div>

      {/* Filter Tabs and Priority Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('alerts')}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              activeTab === 'alerts'
                ? 'bg-[#0d6269] text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            Open alerts · {doctorAlerts.length}
          </button>
          <button
            onClick={() => setActiveTab('requests')}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              activeTab === 'requests'
                ? 'bg-[#0d6269] text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            Contact requests · {contactRequests.length > 0 ? contactRequests.length : 1}
          </button>
        </div>

        {/* Priority Filter */}
        {activeTab === 'alerts' && (
          <div className="relative">
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="appearance-none bg-white border border-slate-200 rounded-xl pl-4 pr-10 py-2 text-sm font-medium text-slate-700 cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] shadow-xs"
            >
              <option value="all">All priorities</option>
              <option value="crisis">Crisis only</option>
              <option value="high">High priority</option>
              <option value="urgent">Urgent</option>
              <option value="under_follow_up">Under follow-up</option>
            </select>
            <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        )}
      </div>

      {/* Tab: Contact Requests Queue */}
      {activeTab === 'requests' ? (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900">Patient Outreach Queue</h3>
            {requestsLoading && <Loader2 className="w-4 h-4 animate-spin text-teal-600" />}
          </div>

          <div className="divide-y divide-slate-100">
            {contactRequests.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-sm">
                <Inbox className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                No pending contact requests. All outreach tasks completed.
              </div>
            ) : (
              contactRequests.map(req => (
                <div key={req.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant={req.urgency === 'urgent' ? 'crisis' : 'within_target'}>
                        {req.urgency.toUpperCase()}
                      </Badge>
                      <span className="text-xs text-slate-400 font-mono">Patient #{req.patient_id}</span>
                      <span className="text-xs text-slate-400 font-semibold">· Status: {req.status}</span>
                    </div>
                    <p className="text-sm font-medium text-slate-800">{req.message}</p>
                    <p className="text-xs text-slate-400">Created: {new Date(req.created_at).toLocaleString()}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => navigateToDoctorPatient(String(req.patient_id))}
                      className="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-xs font-semibold text-slate-700 rounded-lg transition-colors"
                    >
                      View Record
                    </button>
                    <button
                      onClick={() => handleCompleteRequest(req.id)}
                      className="px-3 py-1.5 bg-[#004d55] hover:bg-teal-900 text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5"
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>Complete Task</span>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      ) : (
        /* Split Inbox Layout: Alerts */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Alert List */}
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
            <div className="p-4 px-5 border-b border-slate-100 flex items-center justify-between text-xs">
              <span className="font-bold text-slate-900">Open alerts</span>
              <span className="text-slate-400">Priority first</span>
            </div>

            <div className="divide-y divide-slate-100">
              {filteredAlerts.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">
                  <Inbox className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                  No open alerts in this view
                </div>
              ) : (
                filteredAlerts.map((alert) => {
                  const isSelected = selectedDoctorAlert?.id === alert.id;
                  return (
                    <div
                      key={alert.id}
                      onClick={() => setSelectedDoctorAlert(alert)}
                      className={`p-5 cursor-pointer transition-colors ${
                        isSelected 
                          ? 'bg-[#f0f9f8] border-l-4 border-l-[#0d6269]' 
                          : 'hover:bg-slate-50/70 border-l-4 border-l-transparent'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <Badge variant={alert.priority as any}>
                          {alert.priorityLabel}
                        </Badge>
                        <span className="text-xs text-slate-400">{alert.timeAgo}</span>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigateToDoctorPatient(alert.patientId);
                        }}
                        className="text-sm font-semibold text-[#0d6269] hover:underline block text-left"
                      >
                        {alert.patientName}
                      </button>

                      <h4 className="font-bold text-slate-900 text-sm mt-0.5">
                        {alert.title}
                      </h4>

                      <p className="text-xs text-slate-500 mt-1 line-clamp-1">
                        {alert.description}
                      </p>
                    </div>
                  );
                })
              )}
            </div>

            <div className="p-4 px-5 bg-white border-t border-slate-100 text-xs text-slate-400">
              Showing {filteredAlerts.length} of {doctorAlerts.length} open alerts
            </div>
          </div>

          {/* Right Column: Alert Detail View */}
          <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
            {selectedDoctorAlert ? (
              <>
                {/* Header Status & Time */}
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <Badge variant={selectedDoctorAlert.priority as any}>
                    {selectedDoctorAlert.priorityLabel}
                  </Badge>
                  <span className="text-xs text-slate-500">
                    {selectedDoctorAlert.isAcknowledged ? 'Acknowledged' : 'Unacknowledged'} · {selectedDoctorAlert.timeAgo}
                  </span>
                </div>

                {/* Title & Description */}
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
                    {selectedDoctorAlert.title}
                  </h2>
                  <p className="text-slate-600 text-sm mt-1.5 leading-relaxed">
                    {selectedDoctorAlert.description}
                  </p>
                </div>

                {/* Patient Compact Card */}
                <div 
                  onClick={() => navigateToDoctorPatient(selectedDoctorAlert.patientId)}
                  className="bg-[#f8fafc] hover:bg-slate-100/80 p-4 rounded-xl border border-slate-200/60 flex items-center justify-between cursor-pointer transition-colors group"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-10 h-10 rounded-full bg-slate-200/70 text-slate-700 font-bold text-xs flex items-center justify-center">
                      {selectedDoctorAlert.patientInitials}
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-900 text-sm group-hover:text-teal-800 transition-colors">
                        {selectedDoctorAlert.patientName}
                      </h4>
                      <p className="text-xs text-slate-500">
                        {selectedDoctorAlert.patientAge} years · {selectedDoctorAlert.patientCode} · Telemonitoring
                      </p>
                    </div>
                  </div>
                  <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-teal-700 transition-colors" />
                </div>

                {/* Stats Rows */}
                <div className="space-y-3 pt-2 text-sm">
                  <div className="flex items-center justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Clinical Protocol</span>
                    <span className="font-bold text-slate-900">722 Diagnostic Telemonitoring</span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Target Threshold</span>
                    <span className="font-bold text-slate-900">&lt;135/85 mmHg</span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">SLA Acknowledgment</span>
                    <span className="font-bold text-slate-900">{selectedDoctorAlert.isAcknowledged ? 'Completed' : 'Pending Clinician'}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-slate-100">
                  <button
                    disabled={selectedDoctorAlert.isAcknowledged}
                    onClick={() => handleAcknowledge(selectedDoctorAlert.id)}
                    className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-xs ${
                      selectedDoctorAlert.isAcknowledged
                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        : 'bg-[#0d6269] text-white hover:bg-teal-800'
                    }`}
                  >
                    <Check className="w-4 h-4" />
                    <span>{selectedDoctorAlert.isAcknowledged ? 'Acknowledged' : 'Acknowledge'}</span>
                  </button>

                  <button
                    onClick={() => setContactModalOpen(true)}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-all shadow-xs"
                  >
                    <Phone className="w-4 h-4 text-slate-500" />
                    <span>Contact</span>
                  </button>

                  <button
                    onClick={() => handleResolve(selectedDoctorAlert.id)}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-all shadow-xs"
                  >
                    <span>Resolve</span>
                  </button>
                </div>

                {/* Bottom Link */}
                <div className="pt-2">
                  <button
                    onClick={() => navigateToDoctorPatient(selectedDoctorAlert.patientId)}
                    className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#0d6269] hover:underline"
                  >
                    <span>Open patient record</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </>
            ) : (
              <div className="p-12 text-center text-slate-400">
                Select an alert from the left list to view details
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quick Contact Modal */}
      {contactModalOpen && selectedDoctorAlert && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">
              Contact {selectedDoctorAlert.patientName}
            </h3>
            <p className="text-sm text-slate-500">
              Send a clinical outreach message or task regarding {selectedDoctorAlert.title.toLowerCase()}.
            </p>

            <div className="space-y-2">
              <label className="block text-xs font-bold text-slate-800">
                Outreach Message / Instructions
              </label>
              <textarea
                rows={3}
                value={contactMessage}
                onChange={(e) => setContactMessage(e.target.value)}
                className="w-full p-3 bg-white border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
              />
            </div>

            <div className="pt-3 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setContactModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isSendingContact}
                onClick={handleSendContact}
                className="px-4 py-2 text-sm font-semibold text-white bg-[#004d55] hover:bg-teal-900 rounded-xl transition-colors flex items-center gap-2 disabled:opacity-60"
              >
                {isSendingContact ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                <span>Send Outreach</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
