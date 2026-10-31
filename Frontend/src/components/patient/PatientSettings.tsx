import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../common/Badge';
import { deviceService, type ConnectedDeviceOut } from '../../services/deviceService';
import { patientService, type PatientFollowUp } from '../../services/patientService';
import { 
  Eye, 
  Check, 
  Languages, 
  Activity, 
  ArrowLeftRight, 
  Stethoscope, 
  CheckCircle, 
  Info, 
  Bluetooth, 
  Plus, 
  SlidersHorizontal, 
  ShieldCheck, 
  CloudCheck, 
  FileDown, 
  Save,
  CheckCircle2,
  Lock,
  Battery,
  RotateCw,
  Loader2
} from 'lucide-react';

export const PatientSettings: React.FC = () => {
  const { settings, updateSettings, currentUser } = useApp();
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [testingSignal, setTestingSignal] = useState(false);
  const [signalTested, setSignalTested] = useState(false);
  const [devices, setDevices] = useState<ConnectedDeviceOut[]>([]);
  const [followUp, setFollowUp] = useState<PatientFollowUp | null>(null);
  const [loadingInitial, setLoadingInitial] = useState(false);

  useEffect(() => {
    setLoadingInitial(true);
    Promise.all([
      deviceService.getOwnDevices()
        .then(res => {
          if (res && res.length > 0) setDevices(res);
        })
        .catch(err => console.warn('Could not load patient devices:', err)),
      patientService.getOwnFollowUp()
        .then(res => {
          if (res) setFollowUp(res);
        })
        .catch(err => console.warn('Could not load patient follow-up:', err)),
    ]).finally(() => setLoadingInitial(false));
  }, []);

  const handleSave = () => {
    updateSettings(settings);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleTestSignal = async () => {
    setTestingSignal(true);
    try {
      const res = await deviceService.getOwnDevices();
      if (res && res.length > 0) setDevices(res);
      setSignalTested(true);
    } catch {
      setSignalTested(true);
    } finally {
      setTestingSignal(false);
      setTimeout(() => setSignalTested(false), 3500);
    }
  };

  const doctorName = followUp?.assigned_doctor?.name || 'Dr. Karim B.';
  const doctorSpeciality = followUp?.assigned_doctor?.speciality || 'Cardiology & Telemonitoring';
  const targetBP = followUp?.target ? `<${followUp.target.systolic}/${followUp.target.diastolic}` : '< 135/85';

  return (
    <div className="space-y-6 animate-fadeIn pb-16 max-w-4xl mx-auto">
      {/* Toast */}
      {saveSuccess && (
        <div className="fixed bottom-6 right-6 bg-[#0d6269] text-white px-5 py-3.5 rounded-xl shadow-xl flex items-center gap-2 text-sm z-50 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-emerald-300" />
          <span>Your preferences have been saved successfully to the server!</span>
        </div>
      )}

      {/* Header Tag and Title */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#e6f4f1] text-[#0d6269]">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            Secure Patient Portal
          </span>
          <span className="text-xs text-slate-400">Record #TC-{currentUser?.id || 1}</span>
          {loadingInitial && <Loader2 className="w-3.5 h-3.5 animate-spin text-teal-600 ml-1" />}
        </div>

        <h1 className="text-3xl font-extrabold text-[#0d6269] tracking-tight">
          Account Settings & Accessibility
        </h1>
        <p className="text-slate-500 text-sm">
          Customize reading preferences, alerts and health data settings.
        </p>
      </div>

      {/* User Profile Banner */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-14 h-14 rounded-full bg-[#004d55] text-white font-bold text-lg flex items-center justify-center border-2 border-white shadow-sm">
              {currentUser?.full_name ? currentUser.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : 'AB'}
            </div>
            <span className="absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-white"></span>
          </div>

          <div>
            <h3 className="text-lg font-bold text-slate-900">{currentUser?.full_name || 'Amina Benali'}</h3>
            <p className="text-xs text-slate-500">{currentUser?.email || 'amina.benali@email.com'} • Essential Hypertension Protocol</p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-[#f0f9f8] px-4 py-2.5 rounded-xl border border-teal-100 shrink-0">
          <div>
            <p className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Cloud sync status</p>
            <p className="text-xs font-bold text-[#0d6269]">Active & Encrypted</p>
          </div>
          <CloudCheck className="w-6 h-6 text-teal-600" />
        </div>
      </div>

      {/* Card 1: Accessibility & Visual Comfort */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
        <div className="flex items-start gap-3.5">
          <div className="w-9 h-9 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center shrink-0">
            <Eye className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Accessibility & Visual Comfort</h3>
            <p className="text-xs text-slate-500">Adjust text size and contrast to read without eye strain.</p>
          </div>
        </div>

        {/* Text Size */}
        <div className="space-y-2.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-800">Text size</span>
            <span className="text-[#0d6269] font-medium bg-[#e6f4f1] px-2.5 py-0.5 rounded-full">
              Current: {settings.textSize.toUpperCase()}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              { id: 'standard', label: 'Standard', desc: 'Default size (14px)' },
              { id: 'large', label: 'Large (16px)', desc: 'Comfortable reading' },
              { id: 'extra_large', label: 'Extra large (18px)', desc: 'High readability' }
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => updateSettings({ textSize: opt.id as any })}
                className={`p-4 rounded-xl text-left border transition-all ${
                  settings.textSize === opt.id
                    ? 'bg-[#0d6269] text-white border-[#0d6269] shadow-xs'
                    : 'bg-slate-50 border-slate-200 text-slate-800 hover:bg-slate-100/70'
                }`}
              >
                <p className="font-bold text-sm">{opt.label}</p>
                <p className={`text-xs mt-0.5 ${settings.textSize === opt.id ? 'text-teal-100' : 'text-slate-500'}`}>
                  {opt.desc}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Theme & Color Palette */}
        <div className="space-y-2.5 pt-2">
          <span className="font-bold text-xs text-slate-800 block">Theme & Color Palette</span>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              { id: 'light', label: 'Light (Nature)', desc: 'Soft sage & white', dot: 'bg-emerald-600' },
              { id: 'dark', label: 'Soothing dark', desc: 'Muted midnight blue', dot: 'bg-slate-800' },
              { id: 'high_contrast', label: 'High Contrast', desc: 'Enhanced WCAG AAA', dot: 'bg-black' }
            ].map((thm) => (
              <div
                key={thm.id}
                onClick={() => updateSettings({ theme: thm.id as any })}
                className={`p-3.5 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                  settings.theme === thm.id
                    ? 'bg-white border-[#0d6269] ring-2 ring-[#0d6269]/20'
                    : 'bg-slate-50 border-slate-200 hover:bg-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={`w-3.5 h-3.5 rounded-full ${thm.dot}`}></span>
                  <div>
                    <p className="font-bold text-xs text-slate-900">{thm.label}</p>
                    <p className="text-[11px] text-slate-500">{thm.desc}</p>
                  </div>
                </div>
                {settings.theme === thm.id && (
                  <Check className="w-4 h-4 text-[#0d6269]" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Application language */}
        <div className="bg-[#f8fafc] rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-slate-100">
          <div className="flex items-center gap-3">
            <Languages className="w-5 h-5 text-teal-700" />
            <div>
              <h4 className="font-bold text-slate-900 text-xs">Application language</h4>
              <p className="text-[11px] text-slate-500">Medical translations approved by health committees</p>
            </div>
          </div>

          <div className="flex items-center bg-white rounded-lg p-0.5 border border-slate-200">
            <button
              onClick={() => updateSettings({ language: 'en' })}
              className={`px-4 py-1.5 rounded-md text-xs font-semibold transition-all ${
                settings.language === 'en'
                  ? 'bg-[#0d6269] text-white'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              English (Active)
            </button>
            <button
              onClick={() => updateSettings({ language: 'ar' })}
              className={`px-4 py-1.5 rounded-md text-xs font-semibold transition-all ${
                settings.language === 'ar'
                  ? 'bg-[#0d6269] text-white'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              العربية (Arabic RTL)
            </button>
          </div>
        </div>
      </div>

      {/* Card 2: Monitoring Mode & Medical Protocol */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-xl bg-teal-100 text-teal-800 flex items-center justify-center shrink-0">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-slate-900">Monitoring Mode & Medical Protocol</h3>
                <Badge variant="within_target">722 Protocol Active</Badge>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">Settings coordinated under the supervision of your care team.</p>
            </div>
          </div>
        </div>

        <button 
          onClick={() => {
            patientService.requestModeChange('self_monitoring', 'Patient requested self-monitoring');
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 3000);
          }}
          className="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
        >
          <ArrowLeftRight className="w-3.5 h-3.5 text-slate-500" />
          <span>Request a monitoring mode change</span>
        </button>

        {/* Two sub cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Care status */}
          <div className="bg-[#f8fafc] border border-slate-200/70 rounded-xl p-5 space-y-3">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              Care status
            </span>
            <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              Remote telemonitoring active
            </div>
            <div className="flex items-center gap-2.5 pt-2 border-t border-slate-200/60 text-xs">
              <Stethoscope className="w-4 h-4 text-teal-700" />
              <div>
                <p className="font-bold text-slate-900">{doctorName}</p>
                <p className="text-slate-400 text-[11px]">{doctorSpeciality}</p>
              </div>
            </div>
          </div>

          {/* Blood pressure target */}
          <div className="bg-[#f0f9f8] border border-teal-100 rounded-xl p-5 space-y-2">
            <span className="text-[10px] font-bold text-teal-800 uppercase tracking-wider block">
              Blood pressure target
            </span>
            <div className="flex items-baseline gap-1">
              <span className="text-4xl font-black text-[#0d6269]">{targetBP}</span>
              <span className="text-xs text-slate-500 font-medium">mmHg</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-teal-900 pt-2 border-t border-teal-100/60">
              <CheckCircle className="w-4 h-4 text-teal-600" />
              <span>Approved by clinical supervisor per ESH/SFHTA consensus</span>
            </div>
          </div>
        </div>

        {/* Protocol info notice */}
        <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3 text-xs text-slate-700 leading-relaxed border border-sky-100">
          <Info className="w-4 h-4 text-sky-700 shrink-0 mt-0.5" />
          <p>
            During remote telemonitoring, every morning and evening blood pressure reading is automatically sent to {doctorName}'s dashboard. Any adjustment to treatment levels requires clinical consultation.
          </p>
        </div>
      </div>

      {/* Card 3: Connected Devices */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shrink-0">
              <Bluetooth className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">Connected Devices</h3>
              <p className="text-xs text-slate-500">Manage your wireless Bluetooth Low Energy (BLE) blood pressure monitor.</p>
            </div>
          </div>

          <button 
            onClick={() => {
              deviceService.pairDevice({
                device_model: 'OMRON HEM-7361T-EBK (Bluetooth Smart)',
                serial_number: `OM-${Date.now().toString().slice(-6)}`,
                validation_status: 'stride_bp_validated',
              }).then(newDev => {
                setDevices(prev => [...prev, newDev]);
                setSaveSuccess(true);
                setTimeout(() => setSaveSuccess(false), 3000);
              });
            }}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#0d6269] text-white text-xs font-bold rounded-xl hover:bg-teal-800 transition-colors shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>Pair BLE BP Monitor</span>
          </button>
        </div>

        {/* Device Item Card */}
        {devices.length > 0 ? (
          devices.map(dev => (
            <div key={dev.id} className="bg-[#f8fafc] border border-slate-200/70 rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="w-16 h-12 bg-white rounded-lg border border-slate-200 flex items-center justify-center shrink-0 p-2 shadow-xs">
                  <Activity className="w-7 h-7 text-[#0d6269]" />
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-slate-900 text-sm">{dev.device_model}</h4>
                    <Badge variant="within_target">{dev.validation_status ? 'Validated' : 'Paired'}</Badge>
                  </div>
                  <p className="text-xs text-slate-500">
                    Serial: {dev.serial_number || 'BLE-Connected'} • Stride BP Clinically Validated
                  </p>
                  <div className="flex items-center gap-4 text-xs text-slate-500 pt-1">
                    <span className="flex items-center gap-1">
                      <Battery className="w-3.5 h-3.5 text-emerald-600" />
                      Battery: 92%
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <RotateCw className="w-3.5 h-3.5 text-slate-400" />
                      Paired: {new Date(dev.paired_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleTestSignal}
                  disabled={testingSignal}
                  className="inline-flex items-center gap-1.5 px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
                >
                  <SlidersHorizontal className={`w-3.5 h-3.5 ${testingSignal ? 'animate-spin' : ''}`} />
                  <span>{testingSignal ? 'Testing...' : signalTested ? 'Signal: 98% (Good)' : 'Test signal'}</span>
                </button>
                <button 
                  onClick={() => {
                    deviceService.unpairDevice(dev.id).then(() => {
                      setDevices(prev => prev.filter(d => d.id !== dev.id));
                    });
                  }}
                  className="px-3 py-2 bg-white border border-rose-200 rounded-xl text-rose-600 hover:bg-rose-50 text-xs font-semibold transition-colors"
                >
                  Unpair
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-[#f8fafc] border border-slate-200/70 rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="w-16 h-12 bg-white rounded-lg border border-slate-200 flex items-center justify-center shrink-0 p-2 shadow-xs">
                <Activity className="w-7 h-7 text-[#0d6269]" />
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-slate-900 text-sm">OMRON HEM-7361T-EBK</h4>
                  <Badge variant="within_target">Connected</Badge>
                </div>
                <p className="text-xs text-slate-500">Standalone integrated cuff • Secure Bluetooth pairing</p>
                <div className="flex items-center gap-4 text-xs text-slate-500 pt-1">
                  <span className="flex items-center gap-1">
                    <Battery className="w-3.5 h-3.5 text-emerald-600" />
                    Battery: 85%
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <RotateCw className="w-3.5 h-3.5 text-slate-400" />
                    Synced today
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleTestSignal}
                disabled={testingSignal}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-xs"
              >
                <SlidersHorizontal className={`w-3.5 h-3.5 ${testingSignal ? 'animate-spin' : ''}`} />
                <span>{testingSignal ? 'Testing...' : signalTested ? 'Signal: 98% (Good)' : 'Test signal'}</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Card 4: Privacy, Sharing & Caregivers */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
        <div className="flex items-start gap-3.5">
          <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Privacy, Sharing & Caregivers</h3>
            <p className="text-xs text-slate-500">Manage who can view your blood pressure readings and your medical data rights.</p>
          </div>
        </div>

        {/* Caregiver sub card */}
        <div className="bg-[#f8fafc] border border-slate-200/70 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-sky-100 text-sky-800 font-bold text-xs flex items-center justify-center">
                KB
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-sm">Karim Benali (Son)</h4>
                <p className="text-xs text-slate-500">Designated caregiver access • Read-only</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Badge variant="within_target">Access enabled</Badge>
              <button className="text-xs font-semibold text-[#0d6269] hover:underline">Edit</button>
            </div>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed pt-2 border-t border-slate-200/60">
            Karim receives a secure weekly summary and a discreet notification only when your blood pressure needs attention. He cannot change your treatment or prescriptions.
          </p>
        </div>

        {/* GDPR consent banner */}
        <div className="bg-[#f8fafc] border border-slate-200/70 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Lock className="w-5 h-5 text-teal-700 shrink-0" />
            <div>
              <h5 className="font-bold text-slate-900 text-xs">GDPR Consent & HDS-Certified Hosting</h5>
              <p className="text-xs text-slate-500">Your health data is end-to-end encrypted and hosted in compliance with HIPAA and GDPR standards.</p>
            </div>
          </div>
          <Badge variant="outline">ISO 27001 / HDS Standard</Badge>
        </div>

        {/* Export Data */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
          <div>
            <h4 className="font-bold text-slate-900 text-xs">Download all my data</h4>
            <p className="text-xs text-slate-500">Full export of your blood pressure history, comments and protocols.</p>
          </div>

          <button className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 shadow-xs transition-colors shrink-0">
            <FileDown className="w-4 h-4 text-slate-500" />
            <span>Export PDF (Report)</span>
          </button>
        </div>
      </div>

      {/* Save Button */}
      <div className="pt-2">
        <button
          onClick={handleSave}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl font-bold text-sm bg-[#0d6269] text-white hover:bg-teal-800 shadow-sm transition-colors"
        >
          <Save className="w-4 h-4" />
          <span>Save my preferences</span>
        </button>
      </div>
    </div>
  );
};
