import { apiClient } from './apiClient';

export interface PatientProfileData {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  gender?: string;
  age_band?: string;
  under_treatment: boolean;
  target_systolic?: number;
  target_diastolic?: number;
  baseline_systolic?: number;
  baseline_diastolic?: number;
  enrolment_status: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
}

export interface PatientSummary {
  patient_id: number;
  enrolment_status: string;
  latest_reading?: {
    systolic: number;
    diastolic: number;
    pulse: number;
    measured_at: string;
  } | null;
  target?: {
    systolic: number;
    diastolic: number;
  };
  is_within_target?: boolean;
  adherence_rate?: number;
  active_alert_count?: number;
}

export interface PatientFollowUp {
  patient_id: number;
  monitoring_mode: string;
  schedule_owner: string;
  assigned_doctor?: {
    name: string;
    speciality?: string;
  } | null;
  target?: {
    systolic: number;
    diastolic: number;
  };
  active_consents: string[];
  enrolment_status: string;
}

export interface PreReviewSummary {
  patient_id: number;
  first_name: string;
  last_name: string;
  age_band?: string;
  under_treatment: boolean;
  target: {
    systolic: number;
    diastolic: number;
  };
  priority?: {
    level: string;
    score: number;
    reasons: string[];
  };
  cycle_progress?: {
    total_slots: number;
    completed_slots: number;
    cycle_day: number;
    cycle_length: number;
  };
  adherence_30d: number;
  active_alerts_count: number;
  data_quality_prompts: Array<{
    reading_id: number;
    measured_at: string;
    flags: string[];
  }>;
  recent_medication_events?: number;
}

export interface CaseReviewOut {
  id: number;
  patient_id: number;
  doctor_user_id: number;
  status: string;
  summary?: string;
  clinical_notes?: string;
  created_at: string;
}

export const patientService = {
  async getOwnSummary(): Promise<PatientSummary> {
    const response = await apiClient.get<PatientSummary>('/patients/me/summary');
    return response.data;
  },

  async getOwnFollowUp(): Promise<PatientFollowUp> {
    const response = await apiClient.get<PatientFollowUp>('/patients/me/follow-up');
    return response.data;
  },

  async getOwnProfile(): Promise<PatientProfileData> {
    const response = await apiClient.get<PatientProfileData>('/patients/me');
    return response.data;
  },

  async getPatientDetail(id: number): Promise<PatientProfileData> {
    const response = await apiClient.get<PatientProfileData>(`/doctor/patients/${id}`);
    return response.data;
  },

  async getPreReviewSummary(id: number): Promise<PreReviewSummary> {
    const response = await apiClient.get<PreReviewSummary>(`/doctor/patients/${id}/summary`);
    return response.data;
  },

  async submitCaseReview(patientId: number, summary: string, status: string = 'completed'): Promise<CaseReviewOut> {
    const response = await apiClient.post<CaseReviewOut>(`/doctor/patients/${patientId}/reviews`, {
      patient_id: patientId,
      summary,
      status,
    });
    return response.data;
  },

  async requestModeChange(requested_mode: string, reason?: string) {
    const response = await apiClient.post('/patients/me/monitoring-mode-requests', {
      requested_mode,
      reason,
    });
    return response.data;
  },

  async getCurrentMode() {
    const response = await apiClient.get('/patients/me/monitoring-mode');
    return response.data;
  },
};

