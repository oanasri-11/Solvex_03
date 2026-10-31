import { apiClient } from './apiClient';

export interface AlertOut {
  id: number;
  patient_id: number;
  alert_type: string;
  severity: string;
  tier?: string; // routine_out_of_range, persistent_elevation, severe_single_reading, critical_emergency
  trigger_type?: string;
  status: string;
  lifecycle?: string; // raised, delivered, acknowledged, escalated, closed
  rule_version_id?: number | null;
  justification?: Record<string, any> | null;
  message?: string | null;
  created_at: string;
  acknowledged_by?: number | null;
  acknowledged_at?: string | null;
  escalated_at?: string | null;
  escalated_to_user_id?: number | null;
  closed_by?: number | null;
  closed_at?: string | null;
  patient_acknowledged_at?: string | null;
  resolved_at?: string | null;
}

export interface AlertFilterParams {
  tier?: string;
  lifecycle?: string;
  unacknowledged?: boolean;
}

export const alertService = {
  /**
   * Get alerts across assigned patients for the logged-in doctor
   */
  async getDoctorAlerts(params?: AlertFilterParams): Promise<AlertOut[]> {
    const response = await apiClient.get<AlertOut[]>('/doctor/me/alerts', { params });
    return response.data;
  },

  /**
   * Get alerts for a specific patient (doctor view)
   */
  async getPatientAlerts(patientId: number): Promise<AlertOut[]> {
    const response = await apiClient.get<AlertOut[]>(`/doctor/patients/${patientId}/alerts`);
    return response.data;
  },

  /**
   * Get own active safety alerts for the logged-in patient
   */
  async getOwnAlerts(): Promise<AlertOut[]> {
    const response = await apiClient.get<AlertOut[]>('/patients/me/alerts');
    return response.data;
  },

  /**
   * Get alert evidence packet (triggering readings, baseline window, rule version)
   */
  async getAlertEvidence(id: number): Promise<any> {
    const response = await apiClient.get<any>(`/alerts/${id}`);
    return response.data;
  },

  /**
   * Clinician acknowledges alert (stops SLA escalation timer)
   */
  async acknowledgeAlert(id: number, note?: string): Promise<AlertOut> {
    const response = await apiClient.post<AlertOut>(`/alerts/${id}/acknowledge`, { note });
    return response.data;
  },

  /**
   * Clinician closes/resolves an alert following clinical action
   */
  async closeAlert(id: number, clinical_note?: string): Promise<AlertOut> {
    const response = await apiClient.post<AlertOut>(`/alerts/${id}/close`, { clinical_note });
    return response.data;
  },

  /**
   * Patient confirms reading emergency guidance (UC09b / RS-1)
   */
  async patientAcknowledgeAlert(id: number, payload: { confirmed?: boolean; action_taken?: string } = { confirmed: true }): Promise<AlertOut> {
    const response = await apiClient.post<AlertOut>(`/alerts/${id}/patient-acknowledge`, payload);
    return response.data;
  },
};

