import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { BrandLogo } from '../common/BrandLogo';
import { authService } from '../../services/authService';
import { User, FileText, Eye, EyeOff, ChevronDown, HeartHandshake, AlertCircle, Loader2 } from 'lucide-react';

export const SignUpPatientScreen: React.FC = () => {
  const { setAuthView, login, setAuthRole } = useApp();
  const [fullName, setFullName] = useState('Amina Benali');
  const [email, setEmail] = useState('amina.benali@email.com');
  const [password, setPassword] = useState('Password123!');
  const [dob, setDob] = useState('1978-06-20');
  const [gender, setGender] = useState('female');
  const [phone, setPhone] = useState('+213660000001');
  const [emergencyContact, setEmergencyContact] = useState('Samir Benali (Son)');
  const [emergencyPhone, setEmergencyPhone] = useState('+213660998877');
  const [showPassword, setShowPassword] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agreed) {
      setError('Please agree to the Terms of Service and Privacy Policy.');
      return;
    }
    setIsLoading(true);
    setError(null);

    try {
      try {
        await authService.register({
          email: email.trim(),
          password: password.trim(),
          full_name: fullName.trim(),
          phone: phone.trim(),
          role: 'patient',
        });
      } catch (regErr: any) {
        if (!regErr.response?.data?.detail?.includes('already registered')) {
          throw regErr;
        }
      }

      await login(email.trim(), password.trim(), 'patient');
    } catch (err: any) {
      console.error('Patient registration error:', err);
      const detail = err.response?.data?.detail || err.message || 'Registration failed. Please check your information.';
      setError(detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col justify-between p-6 sm:p-10 animate-fadeIn">
      {/* Top Left Logo */}
      <div className="flex items-center justify-between max-w-6xl mx-auto w-full">
        <BrandLogo 
          size="sm" 
          showSubtitle={true} 
          subtitleText="Patient Portal Registration" 
          horizontal={true} 
        />
        <div className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-[#0d6269] bg-teal-50 px-3 py-1.5 rounded-full border border-teal-100">
          <HeartHandshake className="w-3.5 h-3.5" />
          <span>Patient Registration</span>
        </div>
      </div>

      {/* Main Container */}
      <div className="w-full max-w-xl mx-auto my-6 space-y-6">
        {/* Patient / Doctor Toggle Pill */}
        <div className="flex justify-center">
          <div className="inline-flex bg-slate-200/80 p-1 rounded-full text-xs font-semibold border border-slate-200">
            <button
              type="button"
              className="flex items-center gap-1.5 px-6 py-2 rounded-full bg-white text-slate-900 shadow-xs transition-all font-bold"
            >
              <User className="w-3.5 h-3.5 text-[#0d6269]" />
              <span>Patient</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setAuthRole('doctor');
                setAuthView('signup_doctor');
              }}
              className="flex items-center gap-1.5 px-6 py-2 rounded-full text-slate-600 hover:text-slate-900 transition-all"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Doctor</span>
            </button>
          </div>
        </div>

        {/* Heading */}
        <div className="text-center space-y-1.5">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Create your Patient account
          </h1>
          <p className="text-slate-500 text-xs sm:text-sm max-w-md mx-auto">
            Join روض telemonitoring to share readings with your care team.
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-sm p-8 sm:p-10">
          {error && (
            <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-2 text-xs font-medium text-rose-700 animate-fadeIn">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                Full name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Amina Benali"
                className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
              />
            </div>

            {/* Email Address */}
            <div>
              <label className="block text-xs font-bold text-slate-800 mb-1">
                Email address <span className="text-rose-500">*</span>
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="amina.benali@email.com"
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
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a password"
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

            {/* DOB & Gender */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">
                  Date of Birth
                </label>
                <div className="relative">
                  <input
                    type="date"
                    value={dob}
                    onChange={(e) => setDob(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">
                  Gender
                </label>
                <div className="relative">
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full appearance-none px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269] cursor-pointer"
                  >
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="other">Other</option>
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
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+213 660 000 001"
                className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
              />
            </div>

            {/* Emergency Contact Header */}
            <div className="pt-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                EMERGENCY CONTACT INFORMATION
              </span>
            </div>

            {/* Emergency Contact Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">
                  Contact Name
                </label>
                <input
                  type="text"
                  placeholder="Next of kin or contact"
                  value={emergencyContact}
                  onChange={(e) => setEmergencyContact(e.target.value)}
                  className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-800 mb-1">
                  Emergency Phone
                </label>
                <input
                  type="tel"
                  placeholder="+213 660 998 877"
                  value={emergencyPhone}
                  onChange={(e) => setEmergencyPhone(e.target.value)}
                  className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6269]/20 focus:border-[#0d6269]"
                />
              </div>
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-start gap-3 pt-2">
              <input
                type="checkbox"
                id="patientTerms"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="mt-1 w-4 h-4 rounded text-[#0d6269] focus:ring-teal-500 border-slate-300 cursor-pointer"
              />
              <label htmlFor="patientTerms" className="text-xs text-slate-600 leading-relaxed cursor-pointer">
                I agree to the <span className="text-slate-900 font-semibold underline">Terms of Service</span> and acknowledge the <span className="text-slate-900 font-semibold underline">Privacy Policy</span> governing health data telemonitoring on منصة روض.
              </label>
            </div>

            {/* Submit Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-[#004d55] text-white hover:bg-teal-900 shadow-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Creating account...</span>
                  </>
                ) : (
                  <span>Create patient account & Enter Portal</span>
                )}
              </button>
            </div>

            {/* Back to Login */}
            <div className="text-center pt-2">
              <p className="text-xs text-slate-600">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setAuthRole('patient');
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
