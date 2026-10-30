import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { BrandLogo } from '../common/BrandLogo';
import { User, FileText, Eye, EyeOff, ChevronDown, Stethoscope } from 'lucide-react';

export const SignUpDoctorScreen: React.FC = () => {
  const { setAuthView, loginAsDoctor, setAuthRole } = useApp();
  const [showPassword, setShowPassword] = useState(false);
  const [agreed, setAgreed] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!agreed) {
      alert('Please agree to the Terms of Service and Medical Protocols.');
      return;
    }
    loginAsDoctor();
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col justify-between p-6 sm:p-10 animate-fadeIn">
      {/* Top Left Logo */}
      <div className="flex items-center justify-between max-w-6xl mx-auto w-full">
        <BrandLogo 
          size="sm" 
          showSubtitle={true} 
          subtitleText="Doctor Workspace Registration" 
          horizontal={true} 
        />
        <div className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-[#0d6269] bg-teal-50 px-3 py-1.5 rounded-full border border-teal-100">
          <Stethoscope className="w-3.5 h-3.5" />
          <span>Clinical Registration</span>
        </div>
      </div>

      {/* Main Container */}
      <div className="w-full max-w-xl mx-auto my-6 space-y-6">
        {/* Patient / Doctor Toggle Pill */}
        <div className="flex justify-center">
          <div className="inline-flex bg-slate-200/80 p-1 rounded-full text-xs font-semibold border border-slate-200">
            <button
              type="button"
              onClick={() => {
                setAuthRole('patient');
                setAuthView('signup_patient');
              }}
              className="flex items-center gap-1.5 px-6 py-2 rounded-full text-slate-600 hover:text-slate-900 transition-all"
            >
              <User className="w-3.5 h-3.5" />
              <span>Patient</span>
            </button>

            <button
              type="button"
              className="flex items-center gap-1.5 px-6 py-2 rounded-full bg-white text-slate-900 shadow-xs transition-all font-bold"
            >
              <FileText className="w-3.5 h-3.5 text-[#0d6269]" />
              <span>Doctor</span>
            </button>
          </div>
        </div>

        {/* Heading */}
        <div className="text-center space-y-1.5">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Create your Doctor account
          </h1>
          <p className="text-slate-500 text-xs sm:text-sm max-w-md mx-auto">
            Join روض telemonitoring to monitor your patients and clinical alerts.
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-sm p-8 sm:p-10">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                Full name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                required
                defaultValue="Dr. Karim B."
                placeholder="Dr. Karim B."
                className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
              />
            </div>

            {/* Professional Email */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                Professional email <span className="text-rose-500">*</span>
              </label>
              <input
                type="email"
                required
                defaultValue="dr.karim@clinic.com"
                placeholder="doctor@clinic.com"
                className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                Password <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  defaultValue="SecurePass123!"
                  placeholder="Create a strong password"
                  className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* RPPS & Specialization Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">
                  RPPS / License # <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  defaultValue="10101234567"
                  placeholder="10101234567"
                  className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">
                  Specialization <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <select
                    required
                    defaultValue="cardiology"
                    className="w-full appearance-none px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] cursor-pointer"
                  >
                    <option value="" disabled>Select specialty</option>
                    <option value="cardiology">Cardiology</option>
                    <option value="internal_medicine">Internal Medicine</option>
                    <option value="general_practice">General Practice</option>
                    <option value="nephrology">Nephrology</option>
                  </select>
                  <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                </div>
              </div>
            </div>

            {/* Phone Number */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                placeholder="+33 6 12 34 56 78"
                className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
              />
            </div>

            {/* Checkbox */}
            <div className="flex items-start gap-3 pt-2">
              <input
                type="checkbox"
                id="doctorTerms"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="mt-1 w-4 h-4 rounded text-[#0d6269] focus:ring-teal-500 border-slate-300 cursor-pointer"
              />
              <label htmlFor="doctorTerms" className="text-xs text-slate-600 leading-relaxed cursor-pointer">
                I agree to the <span className="text-slate-900 font-semibold underline">Terms of Service</span> and acknowledge the <span className="text-slate-900 font-semibold underline">Medical Telemonitoring Protocols</span> governing clinical patient care on منصة روض.
              </label>
            </div>

            {/* Submit Button */}
            <div className="pt-2">
              <button
                type="submit"
                className="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-[#004d55] text-white hover:bg-teal-900 shadow-sm transition-colors"
              >
                Create doctor account & Enter Workspace
              </button>
            </div>

            {/* Back to Login */}
            <div className="text-center pt-2">
              <p className="text-xs text-slate-600">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setAuthRole('doctor');
                    setAuthView('login');
                  }}
                  className="font-bold text-[#0d6269] hover:underline"
                >
                  Log in
                </button>
              </p>
            </div>
          </form>
        </div>
      </div>

      {/* Footer */}
      <footer className="w-full max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2 border-t border-slate-100 pt-6">
        <div>© 2026 روض. All rights reserved.</div>
        <div className="flex items-center gap-6">
          <a href="#privacy" className="hover:text-slate-600">Privacy policy</a>
          <a href="#terms" className="hover:text-slate-600">Terms of service</a>
        </div>
      </footer>
    </div>
  );
};
