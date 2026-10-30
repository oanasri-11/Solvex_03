import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Stethoscope, User, Lock, Sparkles, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react';

export const DevNavBar: React.FC = () => {
  const {
    appView,
    setAppView,
    setRole,
    doctorView,
    setDoctorView,
    patientView,
    setPatientView,
    authView,
    setAuthView,
    resetToSplash
  } = useApp();

  const [collapsed, setCollapsed] = useState(false);

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="fixed top-2 right-2 z-50 bg-slate-900/90 text-teal-400 hover:text-white px-2.5 py-1 rounded-full text-[11px] font-bold shadow-lg border border-slate-700 flex items-center gap-1.5 backdrop-blur-xs"
      >
        <Sparkles className="w-3 h-3 text-teal-400" />
        <span>روض Navigator</span>
        <ChevronDown className="w-3 h-3" />
      </button>
    );
  }

  return (
    <div className="bg-slate-900 text-white text-xs py-1.5 px-4 sticky top-0 z-50 shadow-md border-b border-slate-800 flex items-center justify-between flex-wrap gap-2">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 font-bold text-teal-400">
          <Sparkles className="w-3.5 h-3.5" />
          <span>روض Flow Navigator</span>
        </div>
        
        {/* Reset / Replay Flow from Splash Screen */}
        <button
          onClick={resetToSplash}
          title="Replay full app flow starting from Splash Screen"
          className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-teal-600/30 hover:bg-teal-600/50 text-teal-300 font-semibold text-[11px] border border-teal-500/40 transition-colors"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Test Flow (Splash)</span>
        </button>

        {/* Portal switcher */}
        <div className="flex items-center bg-slate-800 rounded-lg p-0.5 border border-slate-700">
          <button
            onClick={() => {
              setAppView('doctor');
              setRole('doctor');
            }}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-all font-medium ${
              appView === 'doctor' ? 'bg-teal-700 text-white shadow-sm' : 'text-slate-300 hover:text-white'
            }`}
          >
            <Stethoscope className="w-3 h-3" />
            Doctor Portal
          </button>
          
          <button
            onClick={() => {
              setAppView('patient');
              setRole('patient');
            }}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-all font-medium ${
              appView === 'patient' ? 'bg-teal-700 text-white shadow-sm' : 'text-slate-300 hover:text-white'
            }`}
          >
            <User className="w-3 h-3" />
            Patient Portal
          </button>

          <button
            onClick={() => {
              setAppView('auth');
            }}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-all font-medium ${
              appView === 'auth' ? 'bg-teal-700 text-white shadow-sm' : 'text-slate-300 hover:text-white'
            }`}
          >
            <Lock className="w-3 h-3" />
            Auth & Splash
          </button>
        </div>
      </div>

      {/* Screen selector pills */}
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="text-slate-400 mr-1 hidden sm:inline">Active Screen:</span>
        
        {appView === 'doctor' && (
          <>
            <button
              onClick={() => setDoctorView('home')}
              className={`px-2 py-0.5 rounded text-[11px] ${doctorView === 'home' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Doctor Home
            </button>
            <button
              onClick={() => setDoctorView('patients')}
              className={`px-2 py-0.5 rounded text-[11px] ${doctorView === 'patients' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Patients List
            </button>
            <button
              onClick={() => setDoctorView('alerts')}
              className={`px-2 py-0.5 rounded text-[11px] ${doctorView === 'alerts' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Doctor Alerts
            </button>
            <button
              onClick={() => setDoctorView('patient_detail')}
              className={`px-2 py-0.5 rounded text-[11px] ${doctorView === 'patient_detail' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Marc Dupuis (Detail)
            </button>
            <button
              onClick={() => setDoctorView('patient_review')}
              className={`px-2 py-0.5 rounded text-[11px] ${doctorView === 'patient_review' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              14-Day Review
            </button>
          </>
        )}

        {appView === 'patient' && (
          <>
            <button
              onClick={() => setPatientView('home')}
              className={`px-2 py-0.5 rounded text-[11px] ${patientView === 'home' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Patient Home
            </button>
            <button
              onClick={() => setPatientView('tracking')}
              className={`px-2 py-0.5 rounded text-[11px] ${patientView === 'tracking' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Record Reading
            </button>
            <button
              onClick={() => setPatientView('history')}
              className={`px-2 py-0.5 rounded text-[11px] ${patientView === 'history' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              History & Trends
            </button>
            <button
              onClick={() => setPatientView('alerts')}
              className={`px-2 py-0.5 rounded text-[11px] ${patientView === 'alerts' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Alerts & Actions
            </button>
            <button
              onClick={() => setPatientView('alert_detail')}
              className={`px-2 py-0.5 rounded text-[11px] ${patientView === 'alert_detail' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Device Alert Detail
            </button>
            <button
              onClick={() => setPatientView('settings')}
              className={`px-2 py-0.5 rounded text-[11px] ${patientView === 'settings' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Settings
            </button>
          </>
        )}

        {appView === 'auth' && (
          <>
            <button
              onClick={() => setAuthView('splash')}
              className={`px-2 py-0.5 rounded text-[11px] ${authView === 'splash' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Splash
            </button>
            <button
              onClick={() => setAuthView('login')}
              className={`px-2 py-0.5 rounded text-[11px] ${authView === 'login' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Log in
            </button>
            <button
              onClick={() => setAuthView('signup_doctor')}
              className={`px-2 py-0.5 rounded text-[11px] ${authView === 'signup_doctor' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Sign Up Doctor
            </button>
            <button
              onClick={() => setAuthView('signup_patient')}
              className={`px-2 py-0.5 rounded text-[11px] ${authView === 'signup_patient' ? 'bg-teal-600 text-white font-semibold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Sign Up Patient
            </button>
          </>
        )}

        {/* Minimize button */}
        <button
          onClick={() => setCollapsed(true)}
          title="Minimize navigator"
          className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 ml-1"
        >
          <ChevronUp className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
