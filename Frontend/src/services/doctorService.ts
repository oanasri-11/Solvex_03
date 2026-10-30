import { apiClient } from './apiClient';

export interface DoctorDashboardMetrics {
  doctor_id: number;
  active_patient_count: number;
  unacknowledged_alerts_count: number;
  alerts_by_tier: {
    critical_emergency: number;
    severe_single_reading: number;
    persistent_elevation: number;
    routine_out_of_range: number;
  };
  open_contact_requests_count: number;
}

export interface PriorityQueueItem {
  patient_id: number;
  first_name: string;
  last_name: string;
  priority_level: 'P1_critical' | 'P2_high' | 'P3_moderate' | 'P4_routine' | 'not_triaged';
  score: number;
  reasons: string[];
  alert_tier: string;
  last_reading?: {
    systolic: number;
    diastolic: number;
    measured_at: string;
  } | null;
  target: {
    systolic: number;
    diastolic: number;
  };
}

export interface PriorityQueueResponse {
  items: PriorityQueueItem[];
  page: number;
  page_size: number;
  total: number;
}

export interface AssignedPatientItem {
  patient_id: number;
  first_name: string;
  last_name: string;
  age_band?: string;
  target?: {
    systolic: number;
    diastolic: number;
  };
  assigned_at?: string;
}

export interface ContactRequest {
  id: number;
  patient_id: number;
  doctor_id: number;
  status: 'open' | 'in_progress' | 'completed' | 'cancelled';
  urgency: 'routine' | 'urgent';
  message: string;
  created_at: string;
  completed_at?: string;
}

export const doctorService = {
  async getDashboard(): Promise<DoctorDashboardMetrics> {
    const response = await apiClient.get<DoctorDashboardMetrics>('/doctor/me/dashboard');
    return response.data;
  },

  async getPriorityQueue(params?: {
    search?: string;
    priority_level?: string[];
    alert_tier?: string[];
    page?: number;
    page_size?: number;
  }): Promise<PriorityQueueResponse> {
    const response = await apiClient.get<PriorityQueueResponse>('/doctor/me/priority-queue', {
      params,
    });
    return response.data;
  },

  async getAssignedPatients(): Promise<AssignedPatientItem[]> {
    const response = await apiClient.get<AssignedPatientItem[]>('/doctor/me/patients');
    return response.data;
  },

  async getContactRequests(status?: string): Promise<ContactRequest[]> {
    const response = await apiClient.get<ContactRequest[]>('/doctor/me/contact-requests', {
      params: { status },
    });
    return response.data;
  },

  async initiateContact(patientId: number, message: string, urgency: 'routine' | 'urgent' = 'routine'): Promise<ContactRequest> {
    const response = await apiClient.post<ContactRequest>(`/doctor/patients/${patientId}/contact-requests`, {
      patient_id: patientId,
      message,
      urgency,
    });
    return response.data;
  },

  async completeContactRequest(id: number, notes?: string): Promise<ContactRequest> {
    const response = await apiClient.post<ContactRequest>(`/contact-requests/${id}/complete`, {
      resolution_notes: notes,
    });
    return response.data;
  },
};

