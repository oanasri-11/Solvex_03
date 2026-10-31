import { describe, it, expect, vi, beforeEach } from 'vitest';
import { doctorService } from '../services/doctorService';
import { apiClient } from '../services/apiClient';

describe('doctorService Unit Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('getDashboard retrieves aggregated metrics', async () => {
    const mockMetrics = {
      doctor_id: 1,
      active_patient_count: 148,
      unacknowledged_alerts_count: 18,
      alerts_by_tier: {
        critical_emergency: 3,
        severe_single_reading: 9,
        persistent_elevation: 4,
        routine_out_of_range: 2,
      },
      open_contact_requests_count: 3,
    };
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockMetrics });

    const result = await doctorService.getDashboard();
    expect(apiClient.get).toHaveBeenCalledWith('/doctor/me/dashboard');
    expect(result.active_patient_count).toBe(148);
    expect(result.alerts_by_tier.critical_emergency).toBe(3);
  });

  it('getPriorityQueue passes query filter parameters', async () => {
    const mockQueue = {
      items: [
        {
          patient_id: 1,
          first_name: 'Amina',
          last_name: 'Benali',
          priority_level: 'P1_critical',
          score: 120,
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
    };
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockQueue });

    const params = { priority_level: ['P1_critical'], search: 'Amina' };
    const result = await doctorService.getPriorityQueue(params);

    expect(apiClient.get).toHaveBeenCalledWith('/doctor/me/priority-queue', { params });
    expect(result.items.length).toBe(1);
    expect(result.items[0].first_name).toBe('Amina');
  });

  it('getAssignedPatients fetches doctor patient cohort', async () => {
    const mockPatients = [
      { id: 1, patient_id: 1, first_name: 'Amina', last_name: 'Benali' },
      { id: 2, patient_id: 2, first_name: 'Marc', last_name: 'Dupuis' },
    ];
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockPatients });

    const result = await doctorService.getAssignedPatients();
    expect(apiClient.get).toHaveBeenCalledWith('/doctor/me/patients');
    expect(result.length).toBe(2);
  });

  it('getContactRequests queries outreach queue with optional status filter', async () => {
    const mockRequests = [
      { id: 10, patient_id: 1, doctor_id: 1, status: 'open', message: 'Call patient' },
    ];
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockRequests });

    const result = await doctorService.getContactRequests('open');
    expect(apiClient.get).toHaveBeenCalledWith('/doctor/me/contact-requests', {
      params: { status: 'open' },
    });
    expect(result[0].status).toBe('open');
  });

  it('initiateContact dispatches new contact request for patient', async () => {
    const mockCreated = {
      id: 11,
      patient_id: 1,
      doctor_id: 1,
      urgency: 'urgent',
      message: 'Urgent follow-up requested',
      status: 'open',
    };
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: mockCreated });

    const result = await doctorService.initiateContact(1, 'Urgent follow-up requested', 'urgent');
    expect(apiClient.post).toHaveBeenCalledWith('/doctor/patients/1/contact-requests', {
      patient_id: 1,
      message: 'Urgent follow-up requested',
      urgency: 'urgent',
    });
    expect(result.id).toBe(11);
  });

  it('completeContactRequest marks outreach task as resolved', async () => {
    const mockCompleted = {
      id: 11,
      status: 'completed',
    };
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: mockCompleted });

    const result = await doctorService.completeContactRequest(11, 'Completed phone call review');
    expect(apiClient.post).toHaveBeenCalledWith('/contact-requests/11/complete', {
      resolution_notes: 'Completed phone call review',
    });
    expect(result.status).toBe('completed');
  });
});

