import React, { createContext, useContext, useState, useEffect } from 'react';
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
import { 
  initialPatients, 
  initialDoctorAlerts, 
  initialPatientAlerts, 
  initialAminaReadings, 
  initialMarcDupuisReadings 
} from '../data/mockData';

interface AppContextType {
  role: Role;
  setRole: (role: Role) => void;
  appView: AppView;
  setAppView: (view: AppView) => void;
  authView: AuthView;
  setAuthView: (view: AuthView) => void;
  doctorView: DoctorView;
  setDoctorView: (view: DoctorView) => void;
  patientView: PatientView;
  setPatientView: (view: PatientView) => void;
  
  // Data
  patients: Patient[];
  selectedPatient: Patient;
  setSelectedPatient: (p: Patient) => void;
  selectPatientById: (id: string) => void;

  doctorAlerts: DoctorAlert[];
  selectedDoctorAlert: DoctorAlert;
  setSelectedDoctorAlert: (alert: DoctorAlert) => void;
  acknowledgeAlert: (alertId: string) => void;
  resolveAlert: (alertId: string) => void;

  patientAlerts: PatientAlert[];
  selectedPatientAlert: PatientAlert;
  setSelectedPatientAlert: (alert: PatientAlert) => void;

  aminaReadings: BPReading[];
  addAminaReading: (reading: Omit<BPReading, 'id'>) => void;
  marcDpuisReadings: BPReading[];

  settings: SettingsState;
  updateSettings: (newSettings: Partial<SettingsState>) => void;

  // Navigation helpers
  navigateToDoctorPatient: (patientId: string) => void;
  navigateToDoctorReview: (patientId: string) => void;
  navigateToPatientAlertDetail: (alertId: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRole] = useState<Role>('doctor');
  const [appView, setAppView] = useState<AppView>('doctor');
  const [authView, setAuthView] = useState<AuthView>('login');
  const [doctorView, setDoctorView] = useState<DoctorView>('home');
  const [patientView, setPatientView] = useState<PatientView>('home');

  const [patients] = useState<Patient[]>(initialPatients);
  const [selectedPatient, setSelectedPatient] = useState<Patient>(initialPatients[1]); // Marc Dupuis

  const [doctorAlerts, setDoctorAlerts] = useState<DoctorAlert[]>(initialDoctorAlerts);
  const [selectedDoctorAlert, setSelectedDoctorAlert] = useState<DoctorAlert>(initialDoctorAlerts[0]);

  const [patientAlerts] = useState<PatientAlert[]>(initialPatientAlerts);
  const [selectedPatientAlert, setSelectedPatientAlert] = useState<PatientAlert>(initialPatientAlerts[2]); // Device sync alert

  const [aminaReadings, setAminaReadings] = useState<BPReading[]>(initialAminaReadings);
  const [marcDpuisReadings] = useState<BPReading[]>(initialMarcDupuisReadings);

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

  const selectPatientById = (id: string) => {
    const found = patients.find(p => p.id === id || p.code === id);
    if (found) {
      setSelectedPatient(found);
    }
  };

  const acknowledgeAlert = (alertId: string) => {
    setDoctorAlerts(prev => prev.map(a => a.id === alertId ? { ...a, isAcknowledged: true } : a));
    if (selectedDoctorAlert.id === alertId) {
      setSelectedDoctorAlert(prev => ({ ...prev, isAcknowledged: true }));
    }
  };

  const resolveAlert = (alertId: string) => {
    setDoctorAlerts(prev => prev.filter(a => a.id !== alertId));
    if (doctorAlerts.length > 0) {
      setSelectedDoctorAlert(doctorAlerts.filter(a => a.id !== alertId)[0] || null);
    }
  };

  const addAminaReading = (reading: Omit<BPReading, 'id'>) => {
    const newReading: BPReading = {
      ...reading,
      id: `ar-${Date.now()}`
    };
    setAminaReadings(prev => [newReading, ...prev]);
  };

  const updateSettings = (newSettings: Partial<SettingsState>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
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
        doctorView,
        setDoctorView,
        patientView,
        setPatientView,
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
