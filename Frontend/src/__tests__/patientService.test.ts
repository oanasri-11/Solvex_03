import { describe, it, expect, vi, beforeEach } from 'vitest';
import { patientService } from '../services/patientService';
import { apiClient } from '../services/apiClient';

describe('patientService Unit Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('getOwnSummary fetches summary for logged-in patient', async () => {
    const mockSummary = {
      patient_id: 1,
      plain_language_status: 'Within target range',
      target: { systolic: 135, diastolic: 85 },
      fourteen_day_average: { systolic: 128, diastolic: 81 },
      total_readings_last_14d: 14,
    };
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockSummary });

    const result = await patientService.getOwnSummary();
    expect(apiClient.get).toHaveBeenCalledWith('/patients/me/summary');
    expect(result.plain_language_status).toBe('Within target range');
    expect(result.fourteen_day_average?.systolic).toBe(128);
  });

  it('getOwnFollowUp fetches assigned clinician and monitoring mode', async () => {
    const mockFollowUp = {
      patient_id: 1,
      monitoring_mode: 'telemonitoring',
      schedule_owner: 'doctor',
      assigned_doctor: {
        name: 'Dr. Karim B.',
        speciality: 'Cardiology',
      },
      target: { systolic: 135, diastolic: 85 },
      active_consents: ['data_sharing'],
      enrolment_status: 'active',
    };
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockFollowUp });

    const result = await patientService.getOwnFollowUp();
    expect(apiClient.get).toHaveBeenCalledWith('/patients/me/follow-up');
    expect(result.assigned_doctor?.name).toBe('Dr. Karim B.');
    expect(result.monitoring_mode).toBe('telemonitoring');
  });

  it('getPreReviewSummary retrieves 14-day digest for doctor review', async () => {
    const mockPreReview = {
      patient_id: 1,
      first_name: 'Amina',
      last_name: 'Benali',
      under_treatment: true,
      target: { systolic: 135, diastolic: 85 },
      active_alerts_count: 2,
      adherence_30d: 0.86,
    };
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockPreReview });

    const result = await patientService.getPreReviewSummary(1);
    expect(apiClient.get).toHaveBeenCalledWith('/doctor/patients/1/summary');
    expect(result.first_name).toBe('Amina');
    expect(result.active_alerts_count).toBe(2);
  });

  it('submitCaseReview posts completed review with string or object payload', async () => {
    const mockReviewOut = {
      id: 50,
      patient_id: 1,
      doctor_user_id: 2,
      status: 'completed',
      summary: '14-day protocol review signed off',
      created_at: new Date().toISOString(),
    };
    vi.spyOn(apiClient, 'post').mockResolvedValue({ data: mockReviewOut });

    // String argument
    const res1 = await patientService.submitCaseReview(1, '14-day protocol review signed off');
    expect(apiClient.post).toHaveBeenCalledWith('/doctor/patients/1/reviews', {
      patient_id: 1,
      summary: '14-day protocol review signed off',
      status: 'completed',
    });
    expect(res1.id).toBe(50);

    // Object argument
    await patientService.submitCaseReview(1, {
      summary: 'Object summary',
      status: 'completed',
      clinical_notes: 'Stable control',
    });
    expect(apiClient.post).toHaveBeenCalledWith('/doctor/patients/1/reviews', {
      patient_id: 1,
      summary: 'Object summary',
      status: 'completed',
      clinical_notes: 'Stable control',
    });
  });

  it('requestModeChange posts requested mode to backend', async () => {
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: { message: 'Mode change requested' } });

    const res = await patientService.requestModeChange('self_monitoring', 'Patient prefers self tracking');
    expect(apiClient.post).toHaveBeenCalledWith('/patients/me/monitoring-mode-requests', {
      requested_mode: 'self_monitoring',
      reason: 'Patient prefers self tracking',
    });
    expect(res.message).toBe('Mode change requested');
  });
});

