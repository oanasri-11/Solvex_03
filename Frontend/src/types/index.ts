export type Role = 'doctor' | 'patient';

export type DoctorView = 'home' | 'alerts' | 'patients' | 'patient_detail' | 'patient_review';
export type PatientView = 'home' | 'tracking' | 'history' | 'alerts' | 'alert_detail' | 'settings';
export type AuthView = 'splash' | 'login' | 'signup_doctor' | 'signup_patient';
export type AppView = 'auth' | 'doctor' | 'patient';

export type ClinicalStatus = 'crisis' | 'high_priority' | 'urgent' | 'within_target';

export interface Patient {
  id: string;
  code: string;
  name: string;
  initials: string;
  age: number;
  birthDate: string;
  gender: string;
  clinicalStatus: ClinicalStatus;
  statusLabel: string;
  statusSubtext: string;
  latestSystolic: number;
  latestDiastolic: number;
  latestPulse?: number;
  latestReadingTime: string;
  isTelemonitoring: boolean;
  baselineBP?: string;
  targetBP?: string;
  adherenceRate?: number;
  protocol?: string;
  condition?: string;
  medication?: string;
}

export type AlertPriority = 'crisis' | 'high' | 'urgent' | 'under_follow_up' | 'caution' | 'information';
export type AlertStatus = 'unacknowledged' | 'acknowledged' | 'under_follow_up' | 'resolved' | 'action_needed' | 'review_needed' | 'check_needed';
export type AlertCategory = 'symptoms' | 'readings' | 'device';

export interface DoctorAlert {
  id: string;
  patientId: string;
  patientName: string;
  patientInitials: string;
  patientAge: number;
  patientCode: string;
  priority: 'crisis' | 'high' | 'urgent' | 'under_follow_up';
  priorityLabel: string;
  title: string;
  description: string;
  timeAgo: string;
  isAcknowledged: boolean;
  morningBPAvg?: string;
  targetRange?: string;
  adherenceRate?: number;
  reportedSymptom?: string;
  telemonitoring: boolean;
}

export interface PatientAlert {
  id: string;
  code: string;
  level: 'emergency' | 'caution' | 'information';
  levelLabel: string;
  category: 'Symptoms' | 'Readings' | 'Device';
  title: string;
  description: string;
  dateTime: string;
  status: 'action_needed' | 'review_needed' | 'check_needed';
  statusLabel: string;
  steps?: { step: number; title: string; description: string }[];
}

export interface BPReading {
  id: string;
  date: string;
  time: string;
  period: 'Morning' | 'Evening';
  systolic: number;
  diastolic: number;
  pulse: number;
  context?: string;
  classification: 'normal' | 'borderline' | 'moderately_high' | 'high' | 'crisis';
  classificationLabel: string;
  isManual?: boolean;
}

export interface SettingsState {
  textSize: 'standard' | 'large' | 'extra_large';
  theme: 'light' | 'dark' | 'high_contrast';
  language: 'en' | 'ar';
}
