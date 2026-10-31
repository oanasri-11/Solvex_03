import { describe, it, expect, vi, beforeEach } from 'vitest';
import { readingService } from '../services/readingService';
import { apiClient } from '../services/apiClient';

describe('readingService Unit Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('createReading posts vital signs observation to /readings', async () => {
    const payload: any = {
      systolic: 135,
      diastolic: 85,
      pulse: 72,
      capture_method: 'manual',
      arm: 'left',
      posture: 'sitting',
      symptoms_reported: ['none'],
    };
    const mockCreated = {
      id: 201,
      patient_id: 1,
      ...payload,
      is_crisis: false,
      verification_status: 'verified',
      created_at: new Date().toISOString(),
    };
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: mockCreated });

    const result = await readingService.createReading(payload);
    expect(apiClient.post).toHaveBeenCalledWith(
      '/readings',
      expect.objectContaining({
        systolic: 135,
        diastolic: 85,
        pulse: 72,
      }),
      expect.any(Object)
    );
    expect(result.id).toBe(201);
    expect(result.systolic).toBe(135);
  });

  it('getOwnReadings retrieves reading collection for patient', async () => {
    const mockList = [
      { id: 1, systolic: 128, diastolic: 82, pulse: 70 },
      { id: 2, systolic: 132, diastolic: 84, pulse: 72 },
    ];
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockList });

    const result = await readingService.getOwnReadings(10);
    expect(apiClient.get).toHaveBeenCalledWith('/patients/me/readings', { params: { limit: 10 } });
    expect(result.length).toBe(2);
  });

  it('getPatientReadings retrieves reading collection for doctor view', async () => {
    const mockList = [{ id: 5, systolic: 160, diastolic: 98, pulse: 80 }];
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockList });

    const result = await readingService.getPatientReadings(3, 20);
    expect(apiClient.get).toHaveBeenCalledWith('/doctor/patients/3/readings', { params: { limit: 20 } });
    expect(result[0].systolic).toBe(160);
  });

  it('getOwnTrends queries longitudinal trend series', async () => {
    const mockTrend = {
      patient_id: 1,
      time_range: '7d',
      readings: [{ date: '2026-10-24', systolic: 128, diastolic: 82 }],
    };
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockTrend });

    const result = await readingService.getOwnTrends('7d');
    expect(apiClient.get).toHaveBeenCalledWith('/patients/me/trends', { params: { range: '7d' } });
    expect(result.time_range).toBe('7d');
  });
});
