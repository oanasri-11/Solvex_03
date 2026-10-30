import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { BrandLogo } from '../common/BrandLogo';
import { Eye, EyeOff, Stethoscope, User, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const LoginScreen: React.FC = () => {
  const { authRole, setAuthRole, loginAsDoctor, loginAsPatient, setAuthView } = useApp();
  const [email, setEmail] = useState(authRole === 'doctor' ? 'dr.karim@clinic.com' : 'amina.benali@email.com');
  const [password, setPassword] = useState('••••••••••••');
  const [showPassword, setShowPassword] = useState(false);

  const handleRoleChange = (role: 'doctor' | 'patient') => {
    setAuthRole(role);
    setEmail(role === 'doctor' ? 'dr.karim@clinic.com' : 'amina.benali@email.com');
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (authRole === 'doctor' || email.toLowerCase().includes('doctor') || email.toLowerCase().includes('clinic') || email.toLowerCase().includes('karim')) {
      loginAsDoctor();
    } else {
      loginAsPatient();
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col justify-between p-6 sm:p-10 animate-fadeIn">
      {/* Top Header with Scaled Brand Logo */}
      <div className="flex items-center justify-between max-w-6xl mx-auto w-full">
        <BrandLogo 
          size="sm" 
          horizontal={true} 
        />
        <div className="hidden sm:flex items-center gap-2 text-xs font-semibold text-slate-500 bg-white px-3 py-1.5 rounded-full border border-slate-200 shadow-2xs">
          <ShieldCheck className="w-4 h-4 text-teal-600" />
          <span>Telemonitoring System • روض</span>
        </div>
      </div>

      {/* Center Auth Card Container */}
      <div className="w-full max-w-lg mx-auto my-auto py-6">
        {/* Portal Role Selector (Doctor vs Patient) */}
        <div className="mb-6 bg-slate-200/80 p-1.5 rounded-2xl flex items-center border border-slate-200">
          <button
            type="button"
            onClick={() => handleRoleChange('doctor')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-xs font-bold transition-all ${
              authRole === 'doctor'
                ? 'bg-[#004d55] text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Stethoscope className="w-4 h-4" />
            <span>بوابة الأطباء (Doctor)</span>
          </button>

          <button
            type="button"
            onClick={() => handleRoleChange('patient')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-xs font-bold transition-all ${
              authRole === 'patient'
                ? 'bg-[#004d55] text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <User className="w-4 h-4" />
            <span>بوابة المرضى (Patient)</span>
          </button>
        </div>

        {/* Card Content */}
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-sm p-8 sm:p-10">
          <div className="text-left mb-6">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold mb-3 tracking-wide uppercase bg-teal-50 text-[#0d6269] border border-teal-100">
              {authRole === 'doctor' ? 'Clinical Workspace' : 'Personal Health Workspace'}
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {authRole === 'doctor' ? 'Welcome Doctor' : 'Welcome back'}
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1.5 leading-relaxed">
              {authRole === 'doctor' 
                ? 'Access patient cohorts, critical alerts, and 14-day telemonitoring reviews.'
                : 'Log in to track your blood pressure readings and view physician guidance.'}
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email field */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1.5">
                {authRole === 'doctor' ? 'Clinical Email' : 'Email address'}
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={authRole === 'doctor' ? 'dr.karim@clinic.com' : 'you@example.com'}
                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] transition-all"
              />
            </div>

            {/* Password field */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] transition-all pr-10"
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

            {/* Forgot password */}
            <div className="text-left">
              <a 
                href="#forgot" 
                onClick={(e) => { e.preventDefault(); alert('Password reset link sent to your registered email.'); }}
                className="text-xs font-bold text-[#0d6269] hover:underline"
              >
                Forgot password?
              </a>
            </div>

            {/* Main Submit Button */}
            <button
              type="submit"
              className="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-[#004d55] text-white hover:bg-teal-900 shadow-sm transition-colors flex items-center justify-center gap-2"
            >
              <span>{authRole === 'doctor' ? 'Log in to Doctor Workspace' : 'Log in to Patient Portal'}</span>
              <ArrowRight className="w-4 h-4 rtl:rotate-180" />
            </button>

            {/* Dedicated Quick Demo Button */}
            <div className="pt-2">
              {authRole === 'doctor' ? (
                <button
                  type="button"
                  onClick={loginAsDoctor}
                  className="w-full flex items-center justify-center gap-2 py-2.5 px-4 border border-teal-200 bg-teal-50/70 hover:bg-teal-100/70 rounded-xl text-xs font-bold text-[#0d6269] transition-colors"
                >
                  <CheckCircle2 className="w-4 h-4 text-[#0d6269]" />
                  <span>One-Click Demo: Dr. Karim B. (Doctor)</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={loginAsPatient}
                  className="w-full flex items-center justify-center gap-2 py-2.5 px-4 border border-teal-200 bg-teal-50/70 hover:bg-teal-100/70 rounded-xl text-xs font-bold text-[#0d6269] transition-colors"
                >
                  <CheckCircle2 className="w-4 h-4 text-[#0d6269]" />
                  <span>One-Click Demo: Amina Benali (Patient)</span>
                </button>
              )}
            </div>

            {/* Registration link */}
            <div className="text-center pt-3 border-t border-slate-100">
              <p className="text-xs text-slate-600">
                New to روض?{' '}
                <button
                  type="button"
                  onClick={() => setAuthView(authRole === 'doctor' ? 'signup_doctor' : 'signup_patient')}
                  className="font-bold text-[#0d6269] hover:underline"
                >
                  {authRole === 'doctor' ? 'Register as Doctor' : 'Register as Patient'}
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
