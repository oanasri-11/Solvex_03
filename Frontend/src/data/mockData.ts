import type { Patient, DoctorAlert, PatientAlert, BPReading } from '../types';

export const initialPatients: Patient[] = [
  {
    id: 'p1',
    code: 'FZ-891',
    name: 'Fatima Zahra',
    initials: 'FZ',
    age: 58,
    birthDate: '12/03/1966',
    gender: 'Female',
    clinicalStatus: 'crisis',
    statusLabel: 'Crisis',
    statusSubtext: '3 active alerts',
    latestSystolic: 184,
    latestDiastolic: 118,
    latestPulse: 88,
    latestReadingTime: '42 min ago',
    isTelemonitoring: true,
    baselineBP: '148/92',
    targetBP: '<130/80',
    adherenceRate: 64,
    condition: 'Refractory Hypertension',
    medication: 'Ramipril 10mg + Amlodipine 10mg'
  },
  {
    id: 'p2',
    code: 'MD-104',
    name: 'Marc Dupuis',
    initials: 'MD',
    age: 71,
    birthDate: '14/05/1953',
    gender: 'Male',
    clinicalStatus: 'high_priority',
    statusLabel: 'High priority',
    statusSubtext: 'Persistent systolic elevation',
    latestSystolic: 158,
    latestDiastolic: 96,
    latestPulse: 74,
    latestReadingTime: '2 hours ago',
    isTelemonitoring: true,
    baselineBP: '142/86',
    targetBP: '<135/85',
    adherenceRate: 78,
    condition: 'HTN Stage 2 · Dyslipidemia',
    medication: 'Amlodipine 5mg QD'
  },
  {
    id: 'p3',
    code: 'JM-331',
    name: 'Jean-Luc M.',
    initials: 'JM',
    age: 67,
    birthDate: '28/09/1957',
    gender: 'Male',
    clinicalStatus: 'urgent',
    statusLabel: 'Urgent',
    statusSubtext: '1 active alert',
    latestSystolic: 174,
    latestDiastolic: 104,
    latestPulse: 82,
    latestReadingTime: '3 hours ago',
    isTelemonitoring: true,
    baselineBP: '145/90',
    targetBP: '<135/85',
    adherenceRate: 82,
    condition: 'Hypertension Stage 2',
    medication: 'Perindopril 5mg'
  },
  {
    id: 'p4',
    code: 'AC-502',
    name: 'Amina Cherif',
    initials: 'AC',
    age: 62,
    birthDate: '19/11/1961',
    gender: 'Female',
    clinicalStatus: 'within_target',
    statusLabel: 'Within target',
    statusSubtext: 'No active alerts',
    latestSystolic: 128,
    latestDiastolic: 82,
    latestPulse: 72,
    latestReadingTime: 'Yesterday',
    isTelemonitoring: true,
    baselineBP: '136/84',
    targetBP: '<135/85',
    adherenceRate: 94,
    condition: 'Essential Hypertension',
    medication: 'Amlodipine 5mg'
  }
];

export const initialDoctorAlerts: DoctorAlert[] = [
  {
    id: 'alert-1',
    patientId: 'p2',
    patientName: 'Marc Dupuis',
    patientInitials: 'MD',
    patientAge: 71,
    patientCode: 'MD-104',
    priority: 'high',
    priorityLabel: 'High priority',
    title: 'Persistent systolic elevation',
    description: 'Systolic pressure has remained elevated over 5 days, with a mean of 156 ± 4 mmHg.',
    timeAgo: '22 min ago',
    isAcknowledged: false,
    morningBPAvg: '154/94 mmHg',
    targetRange: '<135/85 mmHg',
    adherenceRate: 78,
    reportedSymptom: 'Mild occipital headache on waking.',
    telemonitoring: true
  },
  {
    id: 'alert-2',
    patientId: 'p1',
    patientName: 'Fatima Zahra',
    patientInitials: 'FZ',
    patientAge: 58,
    patientCode: 'FZ-891',
    priority: 'crisis',
    priorityLabel: 'Crisis',
    title: 'Elevated blood pressure',
    description: 'Latest BP 184/118 mmHg measured 42 min ago with elevated diastolic threshold exceeded.',
    timeAgo: '42 min ago',
    isAcknowledged: false,
    morningBPAvg: '178/112 mmHg',
    targetRange: '<130/80 mmHg',
    adherenceRate: 64,
    reportedSymptom: 'Dizziness and blurred vision.',
    telemonitoring: true
  },
  {
    id: 'alert-3',
    patientId: 'p3',
    patientName: 'Jean-Luc M.',
    patientInitials: 'JM',
    patientAge: 67,
    patientCode: 'JM-331',
    priority: 'urgent',
    priorityLabel: 'Urgent',
    title: 'Very high blood pressure',
    description: 'Latest BP 174/104 mmHg. Single reading spike above safety alert limit.',
    timeAgo: '3 hours ago',
    isAcknowledged: false,
    morningBPAvg: '162/98 mmHg',
    targetRange: '<135/85 mmHg',
    adherenceRate: 82,
    reportedSymptom: 'None reported.',
    telemonitoring: true
  },
  {
    id: 'alert-4',
    patientId: 'p2',
    patientName: 'Marc Dupuis',
    patientInitials: 'MD',
    patientAge: 71,
    patientCode: 'MD-104',
    priority: 'under_follow_up',
    priorityLabel: 'Under follow-up',
    title: 'Missed evening measurements',
    description: '2 consecutive evening readings missed on Oct 22 and Oct 23.',
    timeAgo: 'Oct 23 · 21:00',
    isAcknowledged: true,
    morningBPAvg: '154/94 mmHg',
    targetRange: '<135/85 mmHg',
    adherenceRate: 78,
    reportedSymptom: 'Acknowledged by Dr. Karim B.',
    telemonitoring: true
  }
];

export const initialPatientAlerts: PatientAlert[] = [
  {
    id: 'pa-1',
    code: 'EX-001',
    level: 'emergency',
    levelLabel: 'Emergency',
    category: 'Symptoms',
    title: 'Chest pain with shortness of breath reported',
    description: 'Reported symptoms require prompt medical intervention.',
    dateTime: '30/10/2026\n09:40',
    status: 'action_needed',
    statusLabel: 'Action needed'
  },
  {
    id: 'pa-2',
    code: 'EX-002',
    level: 'caution',
    levelLabel: 'Caution',
    category: 'Readings',
    title: 'Repeated readings above personal target',
    description: 'Several morning readings exceeded the 135 mmHg threshold set with your doctor.',
    dateTime: '29/10/2026\n18:30',
    status: 'review_needed',
    statusLabel: 'Review needed'
  },
  {
    id: 'pa-3',
    code: 'EX-003',
    level: 'information',
    levelLabel: 'Information',
    category: 'Device',
    title: 'Blood pressure monitor sync interrupted',
    description: 'Bluetooth transfer from OMRON Evolv has stopped. New readings are not updating.',
    dateTime: '28/10/2026\n08:15',
    status: 'check_needed',
    statusLabel: 'Check needed',
    steps: [
      {
        step: 1,
        title: 'Check connections',
        description: 'Enable Bluetooth on the connecting device. Check internet access and permissions for the companion app.'
      },
      {
        step: 2,
        title: 'Check the BP monitor',
        description: 'Check the batteries and turn on the monitor. Move it closer to the connecting device, following its instructions.'
      },
      {
        step: 3,
        title: 'Restart syncing',
        description: 'Reopen the companion app and try again. If the issue persists, keep the displayed readings and enter them manually.'
      }
    ]
  }
];

export const initialMarcDupuisReadings: BPReading[] = [
  {
    id: 'mr-1',
    date: 'Today',
    time: '08:14',
    period: 'Morning',
    systolic: 164,
    diastolic: 98,
    pulse: 76,
    classification: 'high',
    classificationLabel: 'High'
  },
  {
    id: 'mr-2',
    date: 'Oct 24',
    time: '20:05',
    period: 'Evening',
    systolic: 158,
    diastolic: 96,
    pulse: 72,
    classification: 'high',
    classificationLabel: 'High'
  },
  {
    id: 'mr-3',
    date: 'Oct 24',
    time: '08:30',
    period: 'Morning',
    systolic: 152,
    diastolic: 92,
    pulse: 75,
    classification: 'moderately_high',
    classificationLabel: 'Moderately high'
  }
];

export const initialAminaReadings: BPReading[] = [
  {
    id: 'ar-1',
    date: '24 Oct 2024',
    time: '08:10',
    period: 'Morning',
    systolic: 128,
    diastolic: 82,
    pulse: 68,
    context: 'Amlodipine 5mg',
    classification: 'normal',
    classificationLabel: 'Normal'
  },
  {
    id: 'ar-2',
    date: '23 Oct 2024',
    time: '19:15',
    period: 'Evening',
    systolic: 132,
    diastolic: 84,
    pulse: 72,
    context: 'After a light dinner',
    classification: 'normal',
    classificationLabel: 'Normal'
  },
  {
    id: 'ar-3',
    date: '23 Oct 2024',
    time: '08:05',
    period: 'Morning',
    systolic: 135,
    diastolic: 86,
    pulse: 74,
    context: 'Restless waking',
    classification: 'moderately_high',
    classificationLabel: 'Moderately high'
  },
  {
    id: 'ar-4',
    date: '22 Oct 2024',
    time: '08:12',
    period: 'Morning',
    systolic: 127,
    diastolic: 80,
    pulse: 66,
    context: 'Medication taken',
    classification: 'normal',
    classificationLabel: 'Normal'
  },
  {
    id: 'ar-5',
    date: '21 Oct 2024',
    time: '19:40',
    period: 'Evening',
    systolic: 129,
    diastolic: 83,
    pulse: 70,
    context: 'At rest',
    classification: 'normal',
    classificationLabel: 'Normal'
  }
];
