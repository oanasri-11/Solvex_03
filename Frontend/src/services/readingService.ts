import { apiClient } from './apiClient';

export interface ReadingCreatePayload {
  systolic: number;
  diastolic: number;
  pulse: number;
  measured_at?: string;
  capture_method?: 'manual' | 'device' | 'assisted';
  arm?: 'left' | 'right';
  posture?: 'sitting' | 'standing' | 'supine';
  symptoms_reported?: string[];
  patient_id?: number;
}

export interface ReadingOut {
  id: number;
  patient_id: number;
  systolic: number;
  diastolic: number;
  pulse: number;
  measured_at: string;
  capture_method: string;
  verification_status: string;
  is_crisis: boolean;
  classification?: string;
  symptoms_reported?: string[];
  data_quality_flags?: string[];
  created_at: string;
}

export interface PatientTrendPoint {
  label?: string;
  date: string;
  period?: 'morning' | 'evening';
  systolic: number;
  diastolic: number;
  pulse?: number;
  is_manual?: boolean;
  isManual?: boolean;
}

export interface PatientTrendResponse {
  patient_id: number;
  time_range: string;
  target_band?: {
    min: number;
    max: number;
  };
  readings: PatientTrendPoint[];
  delta_from_baseline?: number;
}

export const readingService = {
  async createReading(payload: ReadingCreatePayload, idempotencyKey?: string): Promise<ReadingOut> {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    const response = await apiClient.post<ReadingOut>('/readings', {
      measured_at: new Date().toISOString(),
      capture_method: 'manual',
      ...payload,
    }, { headers });
    return response.data;
  },

  async getOwnReadings(params?: {
    from?: string;
    to?: string;
    page?: number;
    page_size?: number;
  }): Promise<ReadingOut[]> {
    const response = await apiClient.get<ReadingOut[]>('/patients/me/readings', { params });
    return response.data;
  },

  async getPatientReadings(patientId: number, params?: {
    from?: string;
    to?: string;
    page?: number;
    page_size?: number;
  }): Promise<ReadingOut[]> {
    const response = await apiClient.get<ReadingOut[]>(`/doctor/patients/${patientId}/readings`, { params });
    return response.data;
  },

  async getOwnTrends(range: string = '7d'): Promise<PatientTrendResponse> {
    const response = await apiClient.get<PatientTrendResponse>('/patients/me/trends', {
      params: { range },
    });
    return response.data;
  },

  async getDoctorTrends(patientId: number, range: string = '30d') {
    const response = await apiClient.get(`/doctor/patients/${patientId}/trends`, {
      params: { range },
    });
    return response.data;
  },

  async confirmReading(id: number, note?: string): Promise<ReadingOut> {
    const response = await apiClient.post<ReadingOut>(`/readings/${id}/confirm`, { note });
    return response.data;
  },
};

