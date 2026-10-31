import type { Patient, ClinicalStatus, BPReading, DoctorAlert, PatientAlert, SettingsState } from '../types';
import type { UserOut } from '../services/userService';

/**
 * Format relative time string from ISO date string
 */
export function formatTimeAgo(isoString?: string): string {
  if (!isoString) return 'recently';
  const date = new Date(isoString);
  const now = new Date();
  const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffSec < 60) return 'Just now';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

/**
 * Map backend Priority Queue Item (from /doctor/me/priority-queue) to frontend Patient
 */
export function mapBackendPriorityQueueItemToPatient(item: any): Patient {
  const patientId = String(item.patient_id);
  const firstName = item.first_name || '';
  const lastName = item.last_name || '';
  const fullName = `${firstName} ${lastName}`.trim() || `Patient #${patientId}`;
  const initials = `${firstName[0] || 'P'}${lastName[0] || ''}`.toUpperCase();

  // Clinical Status Mapping
  let clinicalStatus: ClinicalStatus = 'within_target';
  let statusLabel = 'Within Target';
  if (item.priority_level === 'P1_critical') {
    clinicalStatus = 'crisis';
    statusLabel = 'Crisis';
  } else if (item.priority_level === 'P2_high') {
    clinicalStatus = 'high_priority';
    statusLabel = 'High Priority';
  } else if (item.priority_level === 'P3_moderate') {
    clinicalStatus = 'urgent';
    statusLabel = 'Urgent';
  }

  const latestSystolic = item.last_reading?.systolic ?? 120;
  const latestDiastolic = item.last_reading?.diastolic ?? 80;
  const latestPulse = item.last_reading?.pulse ?? 72;
  const latestReadingTime = formatTimeAgo(item.last_reading?.measured_at);

  const targetSystolic = item.target?.systolic ?? 135;
  const targetDiastolic = item.target?.diastolic ?? 85;

  const reasons = Array.isArray(item.reasons) ? item.reasons.join(', ') : '';

  return {
    id: patientId,
    code: `P-${patientId.padStart(3, '0')}`,
    name: fullName,
    initials,
    age: item.age || 55,
    birthDate: item.birthDate || '1970-01-01',
    gender: item.gender ? (item.gender === 'male' ? 'Male' : 'Female') : 'Other',
    clinicalStatus,
    statusLabel,
    statusSubtext: reasons || (item.alert_tier && item.alert_tier !== 'none' ? `Active alert: ${item.alert_tier}` : 'Protocol active'),
    latestSystolic,
    latestDiastolic,
    latestPulse,
    latestReadingTime,
    isTelemonitoring: true,
    targetBP: `<${targetSystolic}/${targetDiastolic}`,
    baselineBP: item.baseline ? `${item.baseline.systolic}/${item.baseline.diastolic}` : '140/90',
    adherenceRate: item.adherence_rate ?? 85,
    condition: item.condition || 'Hypertension',
    medication: item.medication || 'Prescribed anti-hypertensive regimen',
  };
}

/**
 * Map backend BloodPressureReading to frontend BPReading
 */
export function mapBackendReadingToBPReading(r: any): BPReading {
  const measuredDate = r.measured_at ? new Date(r.measured_at) : new Date();
  const hours = measuredDate.getHours();
  const period: 'Morning' | 'Evening' = hours < 14 ? 'Morning' : 'Evening';
  const time = measuredDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const date = measuredDate.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });

  // Classify reading
  let classification: 'normal' | 'borderline' | 'moderately_high' | 'high' | 'crisis' = 'normal';
  let classificationLabel = 'Normal';
  if (r.systolic >= 180 || r.diastolic >= 120 || r.is_crisis) {
    classification = 'crisis';
    classificationLabel = 'Crisis';
  } else if (r.systolic >= 160 || r.diastolic >= 100) {
    classification = 'high';
    classificationLabel = 'Stage 2 HTN';
  } else if (r.systolic >= 140 || r.diastolic >= 90) {
    classification = 'moderately_high';
    classificationLabel = 'Stage 1 HTN';
  } else if (r.systolic >= 130 || r.diastolic >= 85) {
    classification = 'borderline';
    classificationLabel = 'Elevated';
  }

  const symptoms = Array.isArray(r.symptoms_reported) && r.symptoms_reported.length > 0
    ? r.symptoms_reported.join(', ')
    : undefined;

  return {
    id: String(r.id),
    date,
    time,
    period,
    systolic: r.systolic,
    diastolic: r.diastolic,
    pulse: r.pulse || 72,
    context: symptoms,
    classification,
    classificationLabel,
    isManual: r.capture_method === 'manual',
  };
}

/**
 * Map backend Alert to frontend DoctorAlert
 */
export function mapBackendAlertToDoctorAlert(a: any, patientName?: string, patientCode?: string): DoctorAlert {
  let priority: 'crisis' | 'high' | 'urgent' | 'under_follow_up' = 'under_follow_up';
  let priorityLabel = 'Follow-up';

  if (a.tier === 'critical_emergency' || a.severity === 'critical') {
    priority = 'crisis';
    priorityLabel = 'Critical Emergency';
  } else if (a.tier === 'severe_single_reading' || a.severity === 'severe') {
    priority = 'high';
    priorityLabel = 'Severe Elevation';
  } else if (a.tier === 'persistent_elevation' || a.severity === 'moderate') {
    priority = 'urgent';
    priorityLabel = 'Persistent Elevation';
  }

  const isAcknowledged = a.lifecycle === 'acknowledged' || a.lifecycle === 'closed' || !!a.acknowledged_at;
  const patientId = String(a.patient_id);
  const displayName = patientName || `Patient #${patientId}`;
  const displayCode = patientCode || `P-${patientId.padStart(3, '0')}`;
  const initials = displayName.split(' ').map((n: string) => n[0]).join('').slice(0, 2).toUpperCase() || 'PT';

  return {
    id: String(a.id),
    patientId,
    patientName: displayName,
    patientInitials: initials,
    patientAge: 58,
    patientCode: displayCode,
    priority,
    priorityLabel,
    title: a.alert_type ? a.alert_type.replace(/_/g, ' ').toUpperCase() : 'BLOOD PRESSURE ALERT',
    description: a.message || 'Elevated blood pressure observed outside target thresholds.',
    timeAgo: formatTimeAgo(a.created_at),
    isAcknowledged,
    telemonitoring: true,
  };
}

/**
 * Map backend Alert to frontend PatientAlert
 */
export function mapBackendAlertToPatientAlert(a: any): PatientAlert {
  let level: 'emergency' | 'caution' | 'information' = 'information';
  let levelLabel = 'Information';
  if (a.tier === 'critical_emergency' || a.severity === 'critical' || a.tier === 'severe_single_reading') {
    level = 'emergency';
    levelLabel = 'Emergency Guidance';
  } else if (a.tier === 'persistent_elevation' || a.severity === 'severe') {
    level = 'caution';
    levelLabel = 'Action Recommended';
  }

  const isAck = a.lifecycle === 'acknowledged' || !!a.patient_acknowledged_at;

  return {
    id: String(a.id),
    code: `ALT-${String(a.id).padStart(4, '0')}`,
    level,
    levelLabel,
    category: 'Readings',
    title: a.alert_type ? a.alert_type.replace(/_/g, ' ') : 'Blood Pressure Notice',
    description: a.message || 'Your latest reading was outside your target range.',
    dateTime: formatTimeAgo(a.created_at),
    status: isAck ? 'review_needed' : 'action_needed',
    statusLabel: isAck ? 'Guidance Reviewed' : 'Review Required',
    steps: [
      { step: 1, title: 'Rest & Breathe', description: 'Sit quietly for 5 minutes without talking or using your phone.' },
      { step: 2, title: 'Repeat Measurement', description: 'Take a second reading on the same arm using the validated cuff.' },
      { step: 3, title: 'Contact Care Team', description: 'If systolic remains above 180 or symptoms worsen, call the clinic or emergency services.' },
    ],
  };
}

/**
 * Map backend User profile to frontend SettingsState
 */
export function mapBackendSettingsToFrontend(user: UserOut): SettingsState {
  let textSize: 'standard' | 'large' | 'extra_large' = 'large';
  if (user.text_size === 100) textSize = 'standard';
  if (user.text_size === 150) textSize = 'extra_large';

  let theme: 'light' | 'dark' | 'high_contrast' = 'light';
  if (user.high_contrast) {
    theme = 'high_contrast';
  } else if (user.theme === 'calm_dark' || user.theme === 'dark') {
    theme = 'dark';
  }

  const language: 'en' | 'ar' = user.locale === 'ar' ? 'ar' : 'en';

  return {
    textSize,
    theme,
    language,
  };
}

/**
 * Map frontend SettingsState to backend update payload
 */
export function mapFrontendSettingsToBackend(settings: SettingsState) {
  let text_size = 125;
  if (settings.textSize === 'standard') text_size = 100;
  if (settings.textSize === 'extra_large') text_size = 150;

  let theme = 'light';
  let high_contrast = false;
  if (settings.theme === 'dark') theme = 'calm_dark';
  if (settings.theme === 'high_contrast') {
    high_contrast = true;
    theme = 'light';
  }

  return {
    locale: settings.language,
    text_size,
    theme,
    high_contrast,
  };
}

