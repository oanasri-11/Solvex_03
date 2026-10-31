import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { 
  Role, 
  DoctorView, 
  PatientView, 
  AuthView, 
  AppView, 
  Patient, 
  DoctorAlert, 
  PatientAlert, 
  BPReading, 
  SettingsState 
} from '../types';
const defaultEmptyPatient: Patient = {
  id: '',
  code: '',
  name: 'No patient selected',
  initials: '--',
  age: 0,
  birthDate: '',
  gender: 'Unknown',
  clinicalStatus: 'within_target',
  statusLabel: 'Normal',
  statusSubtext: '',
  latestSystolic: 0,
  latestDiastolic: 0,
  latestPulse: 0,
  latestReadingTime: 'No readings',
  isTelemonitoring: false,
};

const defaultEmptyDoctorAlert: DoctorAlert = {
  id: '',
  patientId: '',
  patientName: 'No Alert',
  patientInitials: '--',
  patientAge: 0,
  patientCode: '',
  title: 'No Alerts',
  description: 'No active clinical alerts.',
  priority: 'under_follow_up',
  priorityLabel: 'Normal',
  timeAgo: '',
  isAcknowledged: true,
  telemonitoring: false,
};

const defaultEmptyPatientAlert: PatientAlert = {
  id: '',
  code: '',
  category: 'Readings',
  title: 'No Active Alerts',
  description: 'Your readings are within expected clinical range.',
  dateTime: '',
  level: 'information',
  levelLabel: 'Normal',
  status: 'review_needed',
  statusLabel: 'Active',
};
import { authService, type UserMe } from '../services/authService';
import { doctorService } from '../services/doctorService';
import { alertService } from '../services/alertService';
import { readingService } from '../services/readingService';
import { userService } from '../services/userService';
import { 
  mapBackendPriorityQueueItemToPatient, 
  mapBackendReadingToBPReading, 
  mapBackendAlertToDoctorAlert, 
  mapBackendAlertToPatientAlert,
  mapBackendSettingsToFrontend,
  mapFrontendSettingsToBackend
} from '../utils/mappers';

interface AppContextType {
  role: Role;
  setRole: (role: Role) => void;
  appView: AppView;
  setAppView: (view: AppView) => void;
  authView: AuthView;
  setAuthView: (view: AuthView) => void;
  authRole: Role;
  setAuthRole: (role: Role) => void;
  doctorView: DoctorView;
  setDoctorView: (view: DoctorView) => void;
  patientView: PatientView;
  setPatientView: (view: PatientView) => void;
  
  // Auth & Session
  currentUser: UserMe | null;
  isAuthenticated: boolean;
  authLoading: boolean;
  login: (email: string, password: string, targetRole?: Role) => Promise<void>;
  loginAsDoctor: () => Promise<void>;
  loginAsPatient: () => Promise<void>;
  logout: () => Promise<void>;
  resetToSplash: () => void;

  // Data
  patients: Patient[];
  selectedPatient: Patient;
  setSelectedPatient: (p: Patient) => void;
  selectPatientById: (id: string) => void;

  doctorAlerts: DoctorAlert[];
  selectedDoctorAlert: DoctorAlert;
  setSelectedDoctorAlert: (alert: DoctorAlert) => void;
  acknowledgeAlert: (alertId: string) => Promise<void>;
  resolveAlert: (alertId: string) => Promise<void>;

  patientAlerts: PatientAlert[];
  selectedPatientAlert: PatientAlert;
  setSelectedPatientAlert: (alert: PatientAlert) => void;

  aminaReadings: BPReading[];
  addAminaReading: (reading: Omit<BPReading, 'id'>) => Promise<void>;
  marcDpuisReadings: BPReading[];

  settings: SettingsState;
  updateSettings: (newSettings: Partial<SettingsState>) => void;

  // Data Refresh
  refreshDoctorCohort: () => Promise<void>;
  refreshPatientReadings: () => Promise<void>;
  refreshAlerts: () => Promise<void>;

  // Navigation helpers
  navigateToDoctorPatient: (patientId: string) => void;
  navigateToDoctorReview: (patientId: string) => void;
  navigateToPatientAlertDetail: (alertId: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRole] = useState<Role>('doctor');
  const [appView, setAppView] = useState<AppView>('auth');
  const [authView, setAuthView] = useState<AuthView>('splash');
  const [authRole, setAuthRole] = useState<Role>('doctor');
  const [doctorView, setDoctorView] = useState<DoctorView>('home');
  const [patientView, setPatientView] = useState<PatientView>('home');

  // Auth state
  const [currentUser, setCurrentUser] = useState<UserMe | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [authLoading, setAuthLoading] = useState<boolean>(true);

  // Cohort & alerts data (Live Backend Driven)
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient>(defaultEmptyPatient);

  const [doctorAlerts, setDoctorAlerts] = useState<DoctorAlert[]>([]);
  const [selectedDoctorAlert, setSelectedDoctorAlert] = useState<DoctorAlert>(defaultEmptyDoctorAlert);

  const [patientAlerts, setPatientAlerts] = useState<PatientAlert[]>([]);
  const [selectedPatientAlert, setSelectedPatientAlert] = useState<PatientAlert>(defaultEmptyPatientAlert);

  const [aminaReadings, setAminaReadings] = useState<BPReading[]>([]);
  const [marcDpuisReadings] = useState<BPReading[]>([]);

  const [settings, setSettings] = useState<SettingsState>({
    textSize: 'large',
    theme: 'light',
    language: 'en'
  });

  // Apply font size & RTL when settings change
  useEffect(() => {
    const root = document.documentElement;
    if (settings.textSize === 'standard') {
      root.style.fontSize = '14px';
    } else if (settings.textSize === 'large') {
      root.style.fontSize = '16px';
    } else if (settings.textSize === 'extra_large') {
      root.style.fontSize = '18px';
    }

    if (settings.language === 'ar') {
      document.body.dir = 'rtl';
      document.body.lang = 'ar';
    } else {
      document.body.dir = 'ltr';
      document.body.lang = 'en';
    }
  }, [settings]);

  // Refresh Doctor Cohort & Alerts from backend
  const refreshDoctorCohort = useCallback(async () => {
    try {
      const queueRes = await doctorService.getPriorityQueue();
      if (queueRes && queueRes.items && queueRes.items.length > 0) {
        const mappedPatients = queueRes.items.map(mapBackendPriorityQueueItemToPatient);
        setPatients(mappedPatients);
        setSelectedPatient(prev => {
          const stillThere = mappedPatients.find(p => p.id === prev.id);
          return stillThere || mappedPatients[0];
        });
      }
    } catch (err) {
      console.warn('Could not fetch doctor priority queue from backend:', err);
    }

    try {
      const alertsRes = await alertService.getDoctorAlerts();
      if (alertsRes && alertsRes.length > 0) {
        const mappedAlerts = alertsRes.map(a => mapBackendAlertToDoctorAlert(a));
        setDoctorAlerts(mappedAlerts);
        setSelectedDoctorAlert(prev => {
          const stillThere = mappedAlerts.find(a => a.id === prev.id);
          return stillThere || mappedAlerts[0];
        });
      }
    } catch (err) {
      console.warn('Could not fetch doctor alerts from backend:', err);
    }
  }, []);

  // Refresh Patient Readings & Alerts from backend
  const refreshPatientReadings = useCallback(async () => {
    try {
      const readingsRes = await readingService.getOwnReadings();
      if (readingsRes && readingsRes.length > 0) {
        const mappedReadings = readingsRes.map(mapBackendReadingToBPReading);
        setAminaReadings(mappedReadings);
      }
    } catch (err) {
      console.warn('Could not fetch patient readings from backend:', err);
    }

    try {
      const alertsRes = await alertService.getOwnAlerts();
      if (alertsRes && alertsRes.length > 0) {
        const mappedAlerts = alertsRes.map(mapBackendAlertToPatientAlert);
        setPatientAlerts(mappedAlerts);
        setSelectedPatientAlert(prev => {
          const stillThere = mappedAlerts.find(a => a.id === prev.id);
          return stillThere || mappedAlerts[0];
        });
      }
    } catch (err) {
      console.warn('Could not fetch patient alerts from backend:', err);
    }
  }, []);

  const refreshAlerts = useCallback(async () => {
    if (role === 'doctor') {
      await refreshDoctorCohort();
    } else {
      await refreshPatientReadings();
    }
  }, [role, refreshDoctorCohort, refreshPatientReadings]);

  // Check auth session on boot
  useEffect(() => {
    const checkAuthSession = async () => {
      setAuthLoading(true);
      if (authService.isAuthenticated()) {
        try {
          const user = await authService.getMe();
          setCurrentUser(user);
          setIsAuthenticated(true);
          const activeRole: Role = user.role === 'doctor' ? 'doctor' : 'patient';
          setRole(activeRole);
          setAuthRole(activeRole);
          setAppView(activeRole);
          setSettings(mapBackendSettingsToFrontend(user));

          if (activeRole === 'doctor') {
            await refreshDoctorCohort();
          } else {
            await refreshPatientReadings();
          }
        } catch (err) {
          console.warn('Session hydration failed, clearing invalid credentials:', err);
          await authService.logout();
          setCurrentUser(null);
          setIsAuthenticated(false);
          setAppView('auth');
          setAuthView('login');
        }
      }
      setAuthLoading(false);
    };

    checkAuthSession();
  }, [refreshDoctorCohort, refreshPatientReadings]);

  const selectPatientById = (id: string) => {
    const found = patients.find(p => p.id === id || p.code === id);
    if (found) {
      setSelectedPatient(found);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    // Optimistic UI update
    setDoctorAlerts(prev => prev.map(a => a.id === alertId ? { ...a, isAcknowledged: true } : a));
    if (selectedDoctorAlert.id === alertId) {
      setSelectedDoctorAlert(prev => ({ ...prev, isAcknowledged: true }));
    }
    const numId = parseInt(alertId, 10);
    if (!isNaN(numId)) {
      try {
        await alertService.acknowledgeAlert(numId);
      } catch (err) {
        console.error('Failed to acknowledge alert on backend:', err);
      }
    }
  };

  const resolveAlert = async (alertId: string) => {
    // Optimistic UI update
    setDoctorAlerts(prev => prev.filter(a => a.id !== alertId));
    if (doctorAlerts.length > 0) {
      setSelectedDoctorAlert(doctorAlerts.filter(a => a.id !== alertId)[0] || null);
    }
    const numId = parseInt(alertId, 10);
    if (!isNaN(numId)) {
      try {
        await alertService.closeAlert(numId, 'Resolved by clinician in dashboard');
      } catch (err) {
        console.error('Failed to close alert on backend:', err);
      }
    }
  };

  const addAminaReading = async (reading: Omit<BPReading, 'id'>) => {
    // Optimistic UI insertion
    const tempReading: BPReading = {
      ...reading,
      id: `ar-${Date.now()}`
    };
    setAminaReadings(prev => [tempReading, ...prev]);

    // Send to backend
    try {
      await readingService.createReading({
        systolic: reading.systolic,
        diastolic: reading.diastolic,
        pulse: reading.pulse,
        capture_method: reading.isManual ? 'manual' : 'device',
        arm: 'left',
        posture: 'sitting',
        symptoms_reported: reading.context ? [reading.context] : [],
      });
      // Re-hydrate patient readings & alerts
      await refreshPatientReadings();
    } catch (err) {
      console.warn('Could not persist reading to backend:', err);
    }
  };

  const updateSettings = (newSettings: Partial<SettingsState>) => {
    const updated = { ...settings, ...newSettings };
    setSettings(updated);
    if (currentUser) {
      userService.updatePreferences(mapFrontendSettingsToBackend(updated)).catch(err => {
        console.warn('Could not persist preferences to backend:', err);
      });
    }
  };

  const login = async (email: string, password: string, targetRole?: Role) => {
    await authService.login(email, password);
    const user = await authService.getMe();
    setCurrentUser(user);
    setIsAuthenticated(true);
    const resolvedRole: Role = (targetRole || (user.role === 'doctor' ? 'doctor' : 'patient'));
    setRole(resolvedRole);
    setAuthRole(resolvedRole);
    setAppView(resolvedRole);
    setSettings(mapBackendSettingsToFrontend(user));

    if (resolvedRole === 'doctor') {
      await refreshDoctorCohort();
    } else {
      await refreshPatientReadings();
    }
  };

  const loginAsDoctor = async () => {
    try {
      await login('dr.karim@clinic.com', 'Password123!', 'doctor');
    } catch (err) {
      console.error('Backend login for dr.karim@clinic.com failed:', err);
    }
  };

  const loginAsPatient = async () => {
    try {
      await login('amina.benali@email.com', 'Password123!', 'patient');
    } catch (err) {
      console.error('Backend login for amina.benali@email.com failed:', err);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (err) {
      console.warn('Error during logout:', err);
    } finally {
      setCurrentUser(null);
      setIsAuthenticated(false);
      setAppView('auth');
      setAuthView('login');
    }
  };

  const resetToSplash = () => {
    setAppView('auth');
    setAuthView('splash');
  };

  const navigateToDoctorPatient = (patientId: string) => {
    selectPatientById(patientId);
    setAppView('doctor');
    setRole('doctor');
    setDoctorView('patient_detail');
  };

  const navigateToDoctorReview = (patientId: string) => {
    selectPatientById(patientId);
    setAppView('doctor');
    setRole('doctor');
    setDoctorView('patient_review');
  };

  const navigateToPatientAlertDetail = (alertId: string) => {
    const found = patientAlerts.find(a => a.id === alertId || a.code === alertId);
    if (found) {
      setSelectedPatientAlert(found);
    }
    setAppView('patient');
    setRole('patient');
    setPatientView('alert_detail');
  };

  return (
    <AppContext.Provider
      value={{
        role,
        setRole,
        appView,
        setAppView,
        authView,
        setAuthView,
        authRole,
        setAuthRole,
        doctorView,
        setDoctorView,
        patientView,
        setPatientView,
        currentUser,
        isAuthenticated,
        authLoading,
        login,
        loginAsDoctor,
        loginAsPatient,
        logout,
        resetToSplash,
        patients,
        selectedPatient,
        setSelectedPatient,
        selectPatientById,
        doctorAlerts,
        selectedDoctorAlert,
        setSelectedDoctorAlert,
        acknowledgeAlert,
        resolveAlert,
        patientAlerts,
        selectedPatientAlert,
        setSelectedPatientAlert,
        aminaReadings,
        addAminaReading,
        marcDpuisReadings,
        settings,
        updateSettings,
        refreshDoctorCohort,
        refreshPatientReadings,
        refreshAlerts,
        navigateToDoctorPatient,
        navigateToDoctorReview,
        navigateToPatientAlertDetail
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
