import { describe, it, expect } from 'vitest';
import {
  formatTimeAgo,
  mapBackendPriorityQueueItemToPatient,
  mapBackendReadingToBPReading,
  mapBackendAlertToDoctorAlert,
  mapBackendAlertToPatientAlert,
  mapBackendSettingsToFrontend,
  mapFrontendSettingsToBackend,
} from '../utils/mappers';

describe('Frontend-Backend Data Mappers', () => {
  describe('formatTimeAgo', () => {
    it('returns "recently" when undefined or empty', () => {
      expect(formatTimeAgo(undefined)).toBe('recently');
      expect(formatTimeAgo('')).toBe('recently');
    });

    it('formats seconds to "Just now"', () => {
      const now = new Date().toISOString();
      expect(formatTimeAgo(now)).toBe('Just now');
    });

    it('formats minutes ago', () => {
      const fiveMinsAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
      expect(formatTimeAgo(fiveMinsAgo)).toBe('5 min ago');
    });

    it('formats hours ago', () => {
      const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString();
      expect(formatTimeAgo(twoHoursAgo)).toBe('2 hours ago');
    });

    it('formats days ago', () => {
      const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString();
      expect(formatTimeAgo(threeDaysAgo)).toBe('3 days ago');
    });
  });

  describe('mapBackendPriorityQueueItemToPatient', () => {
    it('maps P1_critical item to crisis status', () => {
      const item = {
        patient_id: 42,
        first_name: 'Fatima',
        last_name: 'Zahra',
        priority_level: 'P1_critical',
        score: 120.5,
        reasons: ['ACTIVE_SEVERE_READING_ALERT'],
        last_reading: {
          systolic: 184,
          diastolic: 118,
          pulse: 88,
          measured_at: new Date().toISOString(),
        },
        target: { systolic: 130, diastolic: 80 },
        adherence_rate: 65,
      };

      const patient = mapBackendPriorityQueueItemToPatient(item);
      expect(patient.id).toBe('42');
      expect(patient.code).toBe('P-042');
      expect(patient.name).toBe('Fatima Zahra');
      expect(patient.initials).toBe('FZ');
      expect(patient.clinicalStatus).toBe('crisis');
      expect(patient.statusLabel).toBe('Crisis');
      expect(patient.latestSystolic).toBe(184);
      expect(patient.latestDiastolic).toBe(118);
      expect(patient.targetBP).toBe('<130/80');
      expect(patient.adherenceRate).toBe(65);
    });

    it('maps P2_high item to high_priority status', () => {
      const item = {
        patient_id: 1,
        first_name: 'Amina',
        last_name: 'Benali',
        priority_level: 'P2_high',
        last_reading: { systolic: 158, diastolic: 96, pulse: 74 },
      };

      const patient = mapBackendPriorityQueueItemToPatient(item);
      expect(patient.clinicalStatus).toBe('high_priority');
      expect(patient.statusLabel).toBe('High Priority');
      expect(patient.latestSystolic).toBe(158);
    });

    it('maps P3_moderate item to urgent status', () => {
      const item = {
        patient_id: 2,
        first_name: 'Marc',
        last_name: 'Dupuis',
        priority_level: 'P3_moderate',
        last_reading: { systolic: 145, diastolic: 90 },
      };

      const patient = mapBackendPriorityQueueItemToPatient(item);
      expect(patient.clinicalStatus).toBe('urgent');
      expect(patient.statusLabel).toBe('Urgent');
    });

    it('maps P4_routine item to within_target status', () => {
      const item = {
        patient_id: 3,
        first_name: 'Jean',
        last_name: 'Luc',
        priority_level: 'P4_routine',
        last_reading: { systolic: 122, diastolic: 78 },
      };

      const patient = mapBackendPriorityQueueItemToPatient(item);
      expect(patient.clinicalStatus).toBe('within_target');
      expect(patient.statusLabel).toBe('Within Target');
    });
  });

  describe('mapBackendReadingToBPReading', () => {
    it('classifies crisis reading when systolic >= 180', () => {
      const raw = {
        id: 101,
        systolic: 185,
        diastolic: 110,
        pulse: 88,
        measured_at: '2026-10-30T08:15:00Z',
        capture_method: 'device',
        symptoms_reported: ['headache', 'dizziness'],
      };

      const reading = mapBackendReadingToBPReading(raw);
      expect(reading.id).toBe('101');
      expect(reading.systolic).toBe(185);
      expect(reading.classification).toBe('crisis');
      expect(reading.classificationLabel).toBe('Crisis');
      expect(reading.isManual).toBe(false);
      expect(reading.context).toContain('headache');
      expect(reading.period).toBe('Morning');
    });

    it('classifies normal reading correctly', () => {
      const raw = {
        id: 102,
        systolic: 120,
        diastolic: 78,
        pulse: 70,
        measured_at: '2026-10-30T20:30:00Z',
        capture_method: 'manual',
      };

      const reading = mapBackendReadingToBPReading(raw);
      expect(reading.classification).toBe('normal');
      expect(reading.classificationLabel).toBe('Normal');
      expect(reading.isManual).toBe(true);
      expect(reading.period).toBe('Evening');
    });
  });

  describe('mapBackendAlertToDoctorAlert', () => {
    it('maps critical_emergency tier to crisis priority', () => {
      const rawAlert = {
        id: 5,
        patient_id: 1,
        tier: 'critical_emergency',
        alert_type: 'severe_hypertension_crisis',
        message: 'Extreme reading observed',
        lifecycle: 'raised',
        created_at: new Date().toISOString(),
      };

      const docAlert = mapBackendAlertToDoctorAlert(rawAlert, 'Amina Benali');
      expect(docAlert.id).toBe('5');
      expect(docAlert.patientId).toBe('1');
      expect(docAlert.patientName).toBe('Amina Benali');
      expect(docAlert.priority).toBe('crisis');
      expect(docAlert.priorityLabel).toBe('Critical Emergency');
      expect(docAlert.isAcknowledged).toBe(false);
    });

    it('detects acknowledged lifecycle', () => {
      const rawAlert = {
        id: 6,
        patient_id: 2,
        tier: 'routine_out_of_range',
        lifecycle: 'acknowledged',
        created_at: new Date().toISOString(),
      };

      const docAlert = mapBackendAlertToDoctorAlert(rawAlert);
      expect(docAlert.isAcknowledged).toBe(true);
      expect(docAlert.priority).toBe('under_follow_up');
    });
  });

  describe('mapBackendAlertToPatientAlert', () => {
    it('maps severe tier to emergency level for patient', () => {
      const rawAlert = {
        id: 7,
        tier: 'severe_single_reading',
        alert_type: 'high_systolic_alert',
        created_at: new Date().toISOString(),
      };

      const patientAlert = mapBackendAlertToPatientAlert(rawAlert);
      expect(patientAlert.id).toBe('7');
      expect(patientAlert.level).toBe('emergency');
      expect(patientAlert.levelLabel).toBe('Emergency Guidance');
      expect(patientAlert.steps?.length).toBe(3);
    });
  });

  describe('Settings Bidirectional Mapping', () => {
    it('transforms backend user preferences to frontend settings state', () => {
      const backendUser: any = {
        text_size: 150,
        theme: 'calm_dark',
        high_contrast: false,
        locale: 'ar',
      };

      const frontendSettings = mapBackendSettingsToFrontend(backendUser);
      expect(frontendSettings.textSize).toBe('extra_large');
      expect(frontendSettings.theme).toBe('dark');
      expect(frontendSettings.language).toBe('ar');
    });

    it('transforms frontend settings state to backend payload', () => {
      const frontendSettings = {
        textSize: 'standard' as const,
        theme: 'high_contrast' as const,
        language: 'en' as const,
      };

      const backendPayload = mapFrontendSettingsToBackend(frontendSettings);
      expect(backendPayload.text_size).toBe(100);
      expect(backendPayload.high_contrast).toBe(true);
      expect(backendPayload.locale).toBe('en');
    });
  });
});

