import { describe, it, expect, vi, beforeEach } from 'vitest';
import { alertService } from '../services/alertService';
import { apiClient } from '../services/apiClient';

describe('alertService Unit Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('getDoctorAlerts applies tier and lifecycle query params', async () => {
    const mockAlerts = [
      { id: 1, tier: 'critical_emergency', lifecycle: 'raised', patient_id: 1 },
    ];
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockAlerts });

    const result = await alertService.getDoctorAlerts({ tier: 'critical_emergency', unacknowledged: true });
    expect(apiClient.get).toHaveBeenCalledWith('/doctor/me/alerts', {
      params: { tier: 'critical_emergency', unacknowledged: true },
    });
    expect(result.length).toBe(1);
    expect(result[0].tier).toBe('critical_emergency');
  });

  it('getOwnAlerts retrieves patient-facing safety alerts', async () => {
    const mockAlerts = [
      { id: 2, tier: 'severe_single_reading', message: 'Take repeat measurement' },
    ];
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockAlerts });

    const result = await alertService.getOwnAlerts();
    expect(apiClient.get).toHaveBeenCalledWith('/patients/me/alerts');
    expect(result[0].id).toBe(2);
  });

  it('acknowledgeAlert stops clinician SLA escalation timer', async () => {
    const mockAck = {
      id: 2,
      lifecycle: 'acknowledged',
      acknowledged_at: new Date().toISOString(),
    };
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: mockAck });

    const result = await alertService.acknowledgeAlert(2, 'Reviewed by Dr. Karim');
    expect(apiClient.post).toHaveBeenCalledWith('/alerts/2/acknowledge', {
      note: 'Reviewed by Dr. Karim',
    });
    expect(result.lifecycle).toBe('acknowledged');
  });

  it('closeAlert closes resolved alert with clinical note', async () => {
    const mockClosed = {
      id: 2,
      lifecycle: 'closed',
      closed_at: new Date().toISOString(),
    };
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: mockClosed });

    const result = await alertService.closeAlert(2, 'Patient reassessed, BP controlled');
    expect(apiClient.post).toHaveBeenCalledWith('/alerts/2/close', {
      clinical_note: 'Patient reassessed, BP controlled',
    });
    expect(result.lifecycle).toBe('closed');
  });

  it('patientAcknowledgeAlert records emergency guidance confirmation', async () => {
    const mockPatientAck = {
      id: 2,
      patient_acknowledged_at: new Date().toISOString(),
    };
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: mockPatientAck });

    const result = await alertService.patientAcknowledgeAlert(2, { confirmed: true, action_taken: 'Rested for 5 minutes' });
    expect(apiClient.post).toHaveBeenCalledWith('/alerts/2/patient-acknowledge', {
      confirmed: true,
      action_taken: 'Rested for 5 minutes',
    });
    expect(result.patient_acknowledged_at).toBeDefined();
  });
});

