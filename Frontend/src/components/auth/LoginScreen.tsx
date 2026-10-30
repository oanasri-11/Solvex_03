import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { BrandLogo } from '../common/BrandLogo';
import { Eye, EyeOff, Stethoscope, User } from 'lucide-react';

export const LoginScreen: React.FC = () => {
  const { setAppView, setRole, setAuthView } = useApp();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.toLowerCase().includes('doctor') || email.toLowerCase().includes('clinic') || email.toLowerCase().includes('karim')) {
      setRole('doctor');
      setAppView('doctor');
    } else {
      setRole('patient');
      setAppView('patient');
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col justify-between p-6 sm:p-12 animate-fadeIn">
      {/* Top Left Logo */}
      <div className="flex items-center">
        <BrandLogo size="sm" showSubtitle={false} />
      </div>

      {/* Center Form Container */}
      <div className="w-full max-w-md mx-auto my-auto py-8">
        <div className="text-left mb-8">
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Welcome back
          </h1>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          {/* Email address */}
          <div>
            <label className="block text-xs font-bold text-slate-900 mb-1.5">
              Email address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] transition-all"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-bold text-slate-900 mb-1.5">
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

          {/* Forgot Password Link */}
          <div className="text-left">
            <a 
              href="#forgot" 
              onClick={(e) => { e.preventDefault(); alert('Password reset link sent to your registered email.'); }}
              className="text-xs font-bold text-[#0d6269] hover:underline"
            >
              Forgot password?
            </a>
          </div>

          {/* Log In Button */}
          <button
            type="submit"
            className="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-[#004d55] text-white hover:bg-teal-900 shadow-sm transition-colors"
          >
            Log in
          </button>

          {/* Quick presets for demo testing */}
          <div className="pt-2 grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => {
                setRole('doctor');
                setAppView('doctor');
              }}
              className="flex items-center justify-center gap-1.5 py-2 px-3 border border-teal-200 bg-teal-50/50 hover:bg-teal-50 rounded-lg text-xs font-semibold text-[#0d6269] transition-colors"
            >
              <Stethoscope className="w-3.5 h-3.5" />
              <span>Demo Doctor</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setRole('patient');
                setAppView('patient');
              }}
              className="flex items-center justify-center gap-1.5 py-2 px-3 border border-teal-200 bg-teal-50/50 hover:bg-teal-50 rounded-lg text-xs font-semibold text-[#0d6269] transition-colors"
            >
              <User className="w-3.5 h-3.5" />
              <span>Demo Patient</span>
            </button>
          </div>

          {/* New to TensioCare Link */}
          <div className="text-center pt-3">
            <p className="text-xs text-slate-600">
              New to TensioCare?{' '}
              <button
                type="button"
                onClick={() => setAuthView('signup_doctor')}
                className="font-bold text-[#0d6269] hover:underline"
              >
                Create an account
              </button>
            </p>
          </div>
        </form>
      </div>

      {/* Footer */}
      <footer className="w-full flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2 border-t border-slate-100 pt-6">
        <div>© 2026 TensioCare. All rights reserved.</div>
        <div className="flex items-center gap-6">
          <a href="#privacy" className="hover:text-slate-600">Privacy policy</a>
          <a href="#terms" className="hover:text-slate-600">Terms of service</a>
        </div>
      </footer>
    </div>
  );
};
