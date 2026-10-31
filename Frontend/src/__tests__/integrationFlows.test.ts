import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authService } from '../services/authService';
import { doctorService } from '../services/doctorService';
import { patientService } from '../services/patientService';
import { readingService } from '../services/readingService';
import { alertService } from '../services/alertService';
import { deviceService } from '../services/deviceService';
import { userService } from '../services/userService';
import { apiClient, parseApiError } from '../services/apiClient';
import {
  mapBackendPriorityQueueItemToPatient,
  mapBackendAlertToDoctorAlert,
  mapBackendReadingToBPReading,
  mapBackendSettingsToFrontend,
  mapFrontendSettingsToBackend,
} from '../utils/mappers';

describe('Frontend-Backend End-to-End Integration Scenarios (Vitest)', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  describe('Scenario 1: Doctor Triage & Clinical Review Workflow', () => {
    it('executes the full clinician triage cycle from login to case review sign-off', async () => {
      // 1. Doctor Authenticates
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
        data: {
          access_token: 'doc_token_abc',
          refresh_token: 'doc_refresh_xyz',
          token_type: 'bearer',
          expires_in: 1800,
        },
      });
      const tokens = await authService.login('dr.karim@clinic.com', 'Password123!');
      expect(tokens.access_token).toBe('doc_token_abc');
      expect(localStorage.getItem('rawd_access_token')).toBe('doc_token_abc');

      // 2. Doctor Dashboard Hydration
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce({
        data: {
          doctor_id: 1,
          active_patient_count: 148,
          unacknowledged_alerts_count: 12,
          alerts_by_tier: {
            critical_emergency: 2,
            severe_single_reading: 5,
            persistent_elevation: 3,
            routine_out_of_range: 2,
          },
          open_contact_requests_count: 1,
        },
      });
      const dashboard = await doctorService.getDashboard();
      expect(dashboard.active_patient_count).toBe(148);
      expect(dashboard.unacknowledged_alerts_count).toBe(12);

      // 3. Fetch Prioritized Care Queue (P1–P4 Triage)
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce({
        data: {
          items: [
            {
              patient_id: 3,
              first_name: 'Fatima',
              last_name: 'Zahra',
              priority_level: 'P1_critical',
              score: 133.5,
              reasons: ['ACTIVE_SEVERE_READING_ALERT'],
              last_reading: { systolic: 184, diastolic: 118, measured_at: new Date().toISOString() },
            },
            {
              patient_id: 1,
              first_name: 'Amina',
              last_name: 'Benali',
              priority_level: 'P2_high',
              score: 74.7,
              reasons: ['ACTIVE_PERSISTENT_ELEVATION_ALERT'],
              last_reading: { systolic: 158, diastolic: 96, measured_at: new Date().toISOString() },
            },
          ],
          page: 1,
          page_size: 20,
          total: 2,
        },
      });
      const queue = await doctorService.getPriorityQueue();
      expect(queue.items.length).toBe(2);

      // Transform top patient to UI model
      const topPatient = mapBackendPriorityQueueItemToPatient(queue.items[0]);
      expect(topPatient.name).toBe('Fatima Zahra');
      expect(topPatient.clinicalStatus).toBe('crisis');
      expect(topPatient.statusLabel).toBe('Crisis');

      // 4. Inspect Patient Alerts & Acknowledge
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce({
        data: [
          {
            id: 88,
            patient_id: 3,
            tier: 'severe_single_reading',
            alert_type: 'severe_hypertension_crisis',
            message: 'Blood pressure 184/118 exceeds safety threshold',
            lifecycle: 'raised',
            created_at: new Date().toISOString(),
          },
        ],
      });
      const patientAlerts = await alertService.getPatientAlerts(3);
      expect(patientAlerts.length).toBe(1);

      const uiAlert = mapBackendAlertToDoctorAlert(patientAlerts[0], topPatient.name);
      expect(uiAlert.priority).toBe('high');
      expect(uiAlert.isAcknowledged).toBe(false);

      // Acknowledge alert (stops SLA timer)
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
        data: {
          id: 88,
          lifecycle: 'acknowledged',
          acknowledged_at: new Date().toISOString(),
        },
      });
      const ackRes = await alertService.acknowledgeAlert(88, 'Clinician reviewing patient history');
      expect(ackRes.lifecycle).toBe('acknowledged');

      // 5. Initiate Patient Outreach Task
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
        data: {
          id: 15,
          patient_id: 3,
          doctor_id: 1,
          status: 'open',
          urgency: 'urgent',
          message: 'Please take repeat measurement on left arm immediately.',
        },
      });
      const outreach = await doctorService.initiateContact(
        3,
        'Please take repeat measurement on left arm immediately.',
        'urgent'
      );
      expect(outreach.status).toBe('open');

      // 6. Complete 14-day Case Review Sign-off
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce({
        data: {
          patient_id: 3,
          first_name: 'Fatima',
          last_name: 'Zahra',
          target: { systolic: 130, diastolic: 80 },
          active_alerts_count: 1,
          adherence_30d: 0.82,
        },
      });
      const preReview = await patientService.getPreReviewSummary(3);
      expect(preReview.target.systolic).toBe(130);

      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
        data: {
          id: 99,
          patient_id: 3,
          status: 'completed',
          summary: 'Cycle review signed off. Antihypertensive therapy titrated.',
        },
      });
      const signoff = await patientService.submitCaseReview(3, {
        summary: 'Cycle review signed off. Antihypertensive therapy titrated.',
        status: 'completed',
      });
      expect(signoff.status).toBe('completed');
    });
  });

  describe('Scenario 2: Patient Telemonitoring & Safety Guidance Workflow', () => {
    it('executes patient vitals ingestion, safety alert reception, and hardware pairing', async () => {
      // 1. Patient Login
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
        data: {
          access_token: 'pat_token_def',
          refresh_token: 'pat_refresh_uvw',
          token_type: 'bearer',
          expires_in: 1800,
        },
      });
      await authService.login('amina.benali@email.com', 'Password123!');
      expect(localStorage.getItem('rawd_access_token')).toBe('pat_token_def');

      // 2. Hydrate Patient Summary & Assigned Clinician
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce({
        data: {
          patient_id: 1,
          plain_language_status: 'Within target range',
          target: { systolic: 135, diastolic: 85 },
          fourteen_day_average: { systolic: 129, diastolic: 82 },
          total_readings_last_14d: 14,
        },
      });
      const summary = await patientService.getOwnSummary();
      expect(summary.plain_language_status).toBe('Within target range');

      // 3. Patient Ingests Vital Signs Reading (Triggers Server Multi-Tier Evaluation)
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
        data: {
          id: 301,
          patient_id: 1,
          systolic: 182,
          diastolic: 112,
          pulse: 88,
          capture_method: 'device',
          is_crisis: true,
          verification_status: 'verified',
          symptoms_reported: ['headache', 'dizziness'],
          created_at: new Date().toISOString(),
        },
      });
      const reading = await readingService.createReading({
        systolic: 182,
        diastolic: 112,
        pulse: 88,
        capture_method: 'device',
        symptoms_reported: ['headache', 'dizziness'],
      });
      expect(reading.id).toBe(301);
      expect(reading.is_crisis).toBe(true);

      const uiReading = mapBackendReadingToBPReading(reading);
      expect(uiReading.classification).toBe('crisis');
      expect(uiReading.classificationLabel).toBe('Crisis');

      // 4. Patient Receives Safety Alert & Confirms Guidance (UC09b / RS-1)
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce({
        data: [
          {
            id: 120,
            patient_id: 1,
            tier: 'critical_emergency',
            alert_type: 'severe_hypertension_crisis',
            message: 'Blood pressure is critically elevated. Follow safety steps.',
            created_at: new Date().toISOString(),
          },
        ],
      });
      const activeAlerts = await alertService.getOwnAlerts();
      expect(activeAlerts.length).toBe(1);

      // Confirm guidance
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
        data: {
          id: 120,
          patient_acknowledged_at: new Date().toISOString(),
        },
      });
      const patientAck = await alertService.patientAcknowledgeAlert(120, {
        confirmed: true,
        action_taken: 'Rested 5 min, repeated measurement',
      });
      expect(patientAck.patient_acknowledged_at).toBeDefined();

      // 5. Patient Pairs Bluetooth Health Hardware
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
        data: {
          id: 4,
          patient_id: 1,
          device_model: 'OMRON HEM-7361T-EBK',
          serial_number: 'OM-8839210',
          validation_status: 'stride_bp_validated',
          paired_at: new Date().toISOString(),
        },
      });
      const device = await deviceService.pairDevice({
        device_model: 'OMRON HEM-7361T-EBK',
        serial_number: 'OM-8839210',
      });
      expect(device.validation_status).toBe('stride_bp_validated');

      // 6. Patient Updates Accessibility Preferences (Persisted to Backend)
      const newSettings = {
        textSize: 'extra_large' as const,
        theme: 'dark' as const,
        language: 'ar' as const,
      };
      const backendPayload = mapFrontendSettingsToBackend(newSettings);

      vi.spyOn(apiClient, 'patch').mockResolvedValueOnce({
        data: {
          id: 1,
          full_name: 'Amina Benali',
          email: 'amina.benali@email.com',
          role: 'patient',
          is_active: true,
          ...backendPayload,
        },
      });
      const updatedUser = await userService.updatePreferences(backendPayload);
      expect(updatedUser.locale).toBe('ar');
      expect(updatedUser.text_size).toBe(150);
      expect(updatedUser.theme).toBe('calm_dark');

      const remapped = mapBackendSettingsToFrontend(updatedUser as any);
      expect(remapped.textSize).toBe('extra_large');
      expect(remapped.theme).toBe('dark');
      expect(remapped.language).toBe('ar');
    });
  });

  describe('Scenario 3: Resiliency & Error Recovery Flow', () => {
    it('handles 422 validation failure with informative error parsing', () => {
      const pydanticError: any = {
        isAxiosError: true,
        response: {
          status: 422,
          data: {
            detail: [
              { loc: ['body', 'systolic'], msg: 'ensure this value is greater than 50', type: 'value_error.number.not_gt' },
            ],
          },
        },
      };

      const parsed = parseApiError(pydanticError);
      expect(parsed.status).toBe(422);
      expect(parsed.message).toContain('ensure this value is greater than 50');
    });

    it('handles network disconnection gracefully', () => {
      const netError = new Error('Network Error: ECONNREFUSED');
      const parsed = parseApiError(netError);
      expect(parsed.status).toBe(500);
      expect(parsed.message).toBe('Network Error: ECONNREFUSED');
    });
  });
});

