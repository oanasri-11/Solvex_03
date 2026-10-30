import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { 
  Clock, 
  Pill, 
  Check, 
  Save, 
  Radio, 
  Sparkles, 
  Cpu, 
  CheckCircle2
} from 'lucide-react';

export const PatientRecordReading: React.FC = () => {
  const { addAminaReading, setPatientView } = useApp();

  const [mode, setMode] = useState<'manual' | 'continuous'>('manual');
  const [systolic, setSystolic] = useState<number>(124);
  const [diastolic, setDiastolic] = useState<number>(82);
  const [pulse, setPulse] = useState<number>(70);
  const [selectedSymptom, setSelectedSymptom] = useState<number>(1);
  const [medicationTaken, setMedicationTaken] = useState<boolean>(true);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [monitoringRunning, setMonitoringRunning] = useState(false);
  const [aiPrediction, setAiPrediction] = useState<string | null>(null);

  const symptomsList = [
    { id: 1, label: 'No symptoms' },
    { id: 2, label: 'Headache' },
    { id: 3, label: 'Dizziness' },
    { id: 4, label: 'Palpitations' },
    { id: 5, label: 'Unusual fatigue' },
    { id: 6, label: 'Nausea' },
    { id: 7, label: 'Other symptom' }
  ];

  const handleSimulateHigh = () => {
    setSystolic(165);
    setDiastolic(102);
    setPulse(84);
    setSelectedSymptom(2); // Headache
  };

  const handleSave = () => {
    const isHigh = systolic >= 140 || diastolic >= 90;
    const isCrisis = systolic >= 180 || diastolic >= 120;
    
    addAminaReading({
      date: 'Today',
      time: '08:30',
      period: 'Morning',
      systolic,
      diastolic,
      pulse,
      context: symptomsList.find(s => s.id === selectedSymptom)?.label || 'No symptoms',
      classification: isCrisis ? 'crisis' : isHigh ? 'high' : 'normal',
      classificationLabel: isCrisis ? 'Crisis' : isHigh ? 'High' : 'Normal',
      isManual: mode === 'manual'
    });

    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      setPatientView('history');
    }, 1500);
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Toast */}
      {savedSuccess && (
        <div className="fixed bottom-6 right-6 bg-[#0d6269] text-white px-5 py-3.5 rounded-xl shadow-xl flex items-center gap-2 text-sm z-50 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-emerald-300" />
          <span className="font-semibold">Reading saved to your health record!</span>
        </div>
      )}

      {/* Top Mode Switcher Pill */}
      <div className="flex items-center gap-2">
        <div className="inline-flex bg-slate-200/80 p-1 rounded-full text-xs font-semibold">
          <button
            onClick={() => setMode('continuous')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full transition-all ${
              mode === 'continuous'
                ? 'bg-[#0d6269] text-white shadow-xs'
                : 'text-slate-700 hover:text-slate-900'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${mode === 'continuous' ? 'bg-emerald-400' : 'bg-slate-400'}`}></span>
            Continuous Tracking
          </button>

          <button
            onClick={() => setMode('manual')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full transition-all ${
              mode === 'manual'
                ? 'bg-[#0d6269] text-white shadow-xs'
                : 'text-slate-700 hover:text-slate-900'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${mode === 'manual' ? 'bg-emerald-400' : 'bg-slate-400'}`}></span>
            Manual
          </button>
        </div>
      </div>

      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-extrabold text-[#0d6269] tracking-tight">
          Record a reading
        </h1>
        <p className="text-slate-500 mt-1 text-sm">
          Enter manually or sync automatically with your connected blood pressure monitor.
        </p>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Form / Controls (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {mode === 'manual' ? (
            <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
              {/* Reading Time */}
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Reading time
                </p>
                <div className="flex items-center gap-2 text-slate-900 font-bold text-base mt-1">
                  <Clock className="w-4 h-4 text-slate-500" />
                  <span>Today, 08:30</span>
                </div>
              </div>

              {/* Recommended optimal range card */}
              <div className="bg-[#eaf4f7] border border-teal-100 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                    <Check className="w-3.5 h-3.5 stroke-[3]" />
                  </div>
                  <div>
                    <h5 className="font-bold text-slate-900 text-xs">
                      Recommended optimal range
                    </h5>
                    <p className="text-xs text-slate-600 mt-0.5">
                      {systolic} / {diastolic} mmHg: Consistent with your weekly average (F06 validated).
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleSimulateHigh}
                  className="shrink-0 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50 shadow-xs transition-colors"
                >
                  Simulate 165/102
                </button>
              </div>

              {/* Manual numeric inputs for customization */}
              <div className="grid grid-cols-3 gap-4 pt-1">
                <div>
                  <label className="text-xs font-semibold text-slate-600">Systolic (SYS)</label>
                  <input
                    type="number"
                    value={systolic}
                    onChange={(e) => setSystolic(Number(e.target.value))}
                    className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-xl text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-600"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600">Diastolic (DIA)</label>
                  <input
                    type="number"
                    value={diastolic}
                    onChange={(e) => setDiastolic(Number(e.target.value))}
                    className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-xl text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-600"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600">Pulse (BPM)</label>
                  <input
                    type="number"
                    value={pulse}
                    onChange={(e) => setPulse(Number(e.target.value))}
                    className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-xl text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-600"
                  />
                </div>
              </div>

              {/* Context & Medication */}
              <div className="space-y-4 pt-2">
                <h4 className="text-sm font-bold text-slate-900">
                  Context & Medication
                </h4>

                <div className="bg-[#f0f7f9] rounded-xl p-4 space-y-3 border border-slate-100">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-800 flex items-center gap-1.5">
                      <span className="w-4 h-4 rounded-full border border-teal-600 flex items-center justify-center text-[10px] text-teal-800 font-bold">+</span>
                      Do you have any symptoms today?
                    </span>
                    <span className="text-slate-400">Optional</span>
                  </div>

                  {/* List of 7 symptoms */}
                  <div className="space-y-1.5">
                    {symptomsList.map((item) => (
                      <div
                        key={item.id}
                        onClick={() => setSelectedSymptom(item.id)}
                        className={`p-2.5 px-4 rounded-xl text-xs font-medium cursor-pointer transition-all flex items-center gap-3 ${
                          selectedSymptom === item.id
                            ? 'bg-white text-slate-900 shadow-xs border border-teal-500 font-semibold'
                            : 'bg-white/70 text-slate-700 hover:bg-white border border-transparent'
                        }`}
                      >
                        <span className="w-5 text-slate-400 font-bold">{item.id}</span>
                        <span>{item.label}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Medication taken item */}
                <div className="bg-[#f0f7f9] rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-sky-200 text-sky-800 flex items-center justify-center shrink-0">
                      <Pill className="w-4 h-4" />
                    </div>
                    <div>
                      <h5 className="font-bold text-slate-900 text-xs">
                        Amlodipine 5mg (Morning dose)
                      </h5>
                      <p className="text-[11px] text-slate-500">
                        Dr. Bensalem • 1 tablet with breakfast
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center bg-white rounded-lg p-0.5 border border-slate-200 shrink-0">
                    <button
                      type="button"
                      onClick={() => setMedicationTaken(true)}
                      className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                        medicationTaken
                          ? 'bg-[#40d2a8] text-slate-900'
                          : 'text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      <Check className="w-3.5 h-3.5 stroke-[3]" />
                      <span>Taken</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setMedicationTaken(false)}
                      className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                        !medicationTaken
                          ? 'bg-slate-200 text-slate-900'
                          : 'text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      Not taken
                    </button>
                  </div>
                </div>
              </div>

              {/* Save Button */}
              <button
                type="button"
                onClick={handleSave}
                className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-bold text-sm bg-[#0d6269] text-white hover:bg-teal-800 shadow-sm transition-colors"
              >
                <Save className="w-4 h-4" />
                <span>Save reading</span>
              </button>
            </div>
          ) : (
            /* Continuous Monitoring Card */
            <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-8 space-y-6">
              <div>
                <h3 className="text-xl font-bold text-slate-900">Continuous monitoring</h3>
                <p className="text-sm text-slate-500 mt-1">
                  Start automatic monitoring or run a simulation to assess the trend over recent days.
                </p>
              </div>

              <div className="space-y-3 pt-2">
                <button
                  type="button"
                  onClick={() => setMonitoringRunning(!monitoringRunning)}
                  className={`w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-bold text-sm transition-all shadow-xs ${
                    monitoringRunning
                      ? 'bg-emerald-600 text-white animate-pulse'
                      : 'bg-[#0d6269] text-white hover:bg-teal-800'
                  }`}
                >
                  <Radio className="w-4 h-4" />
                  <span>{monitoringRunning ? 'Monitoring Active (Streaming telemetry...)' : 'Start continuous monitoring'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleSimulateHigh()}
                  className="w-full py-3.5 rounded-xl font-semibold text-sm bg-white border border-slate-200 text-slate-800 hover:bg-slate-50 transition-colors shadow-xs"
                >
                  Simulation
                </button>

                <button
                  type="button"
                  onClick={() => setAiPrediction('Predictive Risk: Low (94% target adherence projected over next 7 days based on current circadian profile).')}
                  className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-sm bg-white border border-slate-200 text-slate-800 hover:bg-slate-50 transition-colors shadow-xs"
                >
                  <Sparkles className="w-4 h-4 text-teal-600" />
                  <span>AI Prediction</span>
                </button>
              </div>

              {aiPrediction && (
                <div className="bg-[#f0f9f8] border border-teal-200 rounded-xl p-4 text-xs text-teal-900 leading-relaxed animate-fadeIn">
                  <p className="font-bold flex items-center gap-1.5 mb-1">
                    <Cpu className="w-4 h-4 text-teal-700" />
                    Clinical AI Assessment
                  </p>
                  {aiPrediction}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: HAS Protocol "Measure BP Correctly" (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs p-7 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900">Measure BP correctly</h3>
            <span className="text-xs text-slate-400 font-medium">HAS protocol</span>
          </div>

          <div className="space-y-3.5">
            {/* Step 1 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                1
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Rest for 5 minutes</h5>
                <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                  Sit comfortably without your phone or television.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                2
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Cuff at heart level</h5>
                <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                  Rest your bent arm on the table, with your palm facing up.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                3
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Do not talk or move</h5>
                <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                  Breathe naturally while the cuff inflates.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="bg-[#e9f4f9] rounded-xl p-4 flex items-start gap-3.5">
              <div className="w-8 h-8 rounded-lg bg-[#b4e0ee] text-[#0d6269] font-bold text-sm flex items-center justify-center shrink-0">
                4
              </div>
              <div>
                <h5 className="font-bold text-slate-900 text-sm">Keep feet flat</h5>
                <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                  Keep legs uncrossed and your back supported.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
