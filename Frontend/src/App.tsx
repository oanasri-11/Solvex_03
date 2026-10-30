import React from "react";
import { AppProvider, useApp } from "./context/AppContext";
import { DoctorLayout } from "./components/layout/DoctorLayout";
import { PatientLayout } from "./components/layout/PatientLayout";

// Doctor Views
import { DoctorDashboard } from "./components/doctor/DoctorDashboard";
import { DoctorPatients } from "./components/doctor/DoctorPatients";
import { DoctorAlerts } from "./components/doctor/DoctorAlerts";
import { DoctorPatientDetail } from "./components/doctor/DoctorPatientDetail";
import { DoctorPatientReview } from "./components/doctor/DoctorPatientReview";

// Patient Views
import { PatientHome } from "./components/patient/PatientHome";
import { PatientRecordReading } from "./components/patient/PatientRecordReading";
import { PatientHistoryTrends } from "./components/patient/PatientHistoryTrends";
import { PatientAlertsActions } from "./components/patient/PatientAlertsActions";
import { PatientAlertDetail } from "./components/patient/PatientAlertDetail";
import { PatientSettings } from "./components/patient/PatientSettings";

// Auth Views
import { SplashScreen } from "./components/auth/SplashScreen";
import { LoginScreen } from "./components/auth/LoginScreen";
import { SignUpDoctorScreen } from "./components/auth/SignUpDoctorScreen";
import { SignUpPatientScreen } from "./components/auth/SignUpPatientScreen";

const MainRouter: React.FC = () => {
  const { appView, authView, doctorView, patientView } = useApp();

  // Auth & Splash Mode
  if (appView === "auth") {
    switch (authView) {
      case "splash":
        return <SplashScreen />;
      case "login":
        return <LoginScreen />;
      case "signup_doctor":
        return <SignUpDoctorScreen />;
      case "signup_patient":
        return <SignUpPatientScreen />;
      default:
        return <LoginScreen />;
    }
  }

  // Doctor Workspace Portal
  if (appView === "doctor") {
    return (
      <DoctorLayout>
        {doctorView === "home" && <DoctorDashboard />}
        {doctorView === "patients" && <DoctorPatients />}
        {doctorView === "alerts" && <DoctorAlerts />}
        {doctorView === "patient_detail" && <DoctorPatientDetail />}
        {doctorView === "patient_review" && <DoctorPatientReview />}
      </DoctorLayout>
    );
  }

  // Patient Workspace Portal
  if (appView === "patient") {
    return (
      <PatientLayout>
        {patientView === "home" && <PatientHome />}
        {patientView === "tracking" && <PatientRecordReading />}
        {patientView === "history" && <PatientHistoryTrends />}
        {patientView === "alerts" && <PatientAlertsActions />}
        {patientView === "alert_detail" && <PatientAlertDetail />}
        {patientView === "settings" && <PatientSettings />}
      </PatientLayout>
    );
  }

  return <LoginScreen />;
};

export function App() {
  return (
    <AppProvider>
      <div className="min-h-screen flex flex-col font-sans antialiased text-slate-900 bg-[#f8fafc]">
        {/* App Main Body */}
        <div className="flex-1">
          <MainRouter />
        </div>
      </div>
    </AppProvider>
  );
}

export default App;
