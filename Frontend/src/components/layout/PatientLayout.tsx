import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { BrandLogo } from '../common/BrandLogo';
import { 
  Calendar, 
  PlusCircle, 
  Clock, 
  Settings, 
  Bell, 
  User, 
  Menu, 
  X
} from 'lucide-react';

interface PatientLayoutProps {
  children: React.ReactNode;
}

export const PatientLayout: React.FC<PatientLayoutProps> = ({ children }) => {
  const { patientView, setPatientView, settings, updateSettings } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'home', label: 'Home', icon: Calendar },
    { id: 'tracking', label: 'Blood Pressure Tracking', icon: PlusCircle },
    { id: 'alerts', label: 'Alerts & Actions', icon: Clock },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen flex bg-[#f8fafc]">
      {/* Mobile Backdrop */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/40 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`fixed lg:sticky top-0 h-screen w-64 bg-white border-r border-slate-200/80 z-40 flex flex-col justify-between transition-transform duration-200 ease-in-out ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-6">
          <div className="flex justify-between items-center lg:justify-center mb-8">
            <BrandLogo size="md" showSubtitle={false} />
            <button 
              onClick={() => setMobileMenuOpen(false)}
              className="lg:hidden p-1 rounded-md text-slate-400 hover:text-slate-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <nav className="space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = patientView === item.id || 
                (item.id === 'tracking' && patientView === 'history') ||
                (item.id === 'alerts' && patientView === 'alert_detail');

              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setPatientView(item.id as any);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl font-medium text-sm transition-all text-left ${
                    isActive
                      ? 'bg-[#0d6269] text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Patient portal footer */}
        <div className="p-6 border-t border-slate-100">
          <div className="bg-[#e6f4f1] text-[#0d6269] p-3 rounded-xl text-xs">
            <p className="font-semibold">Telemonitoring Active</p>
            <p className="text-[11px] text-teal-800/80 mt-0.5">Synced with Dr. Philippe Laurent</p>
          </div>
        </div>
      </aside>

      {/* Main Container */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-6 sm:px-8 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h2 className="text-base font-semibold text-slate-800">Hello, Amina</h2>
          </div>

          {/* Controls: Language toggle + Bell + User */}
          <div className="flex items-center gap-4 sm:gap-6">
            {/* Language toggle pill */}
            <div className="flex items-center bg-slate-100 p-0.5 rounded-full border border-slate-200">
              <button
                onClick={() => updateSettings({ language: 'en' })}
                className={`px-3 py-1 text-xs font-semibold rounded-full transition-all ${
                  settings.language === 'en' 
                    ? 'bg-[#0d6269] text-white shadow-xs' 
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                EN
              </button>
              <button
                onClick={() => updateSettings({ language: 'ar' })}
                className={`px-3 py-1 text-xs font-semibold rounded-full transition-all ${
                  settings.language === 'ar' 
                    ? 'bg-[#0d6269] text-white shadow-xs' 
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Arabic
              </button>
            </div>

            {/* Notification bell */}
            <div className="relative cursor-pointer p-1.5 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-teal-600"></span>
            </div>

            {/* Patient profile */}
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <h4 className="text-sm font-bold text-slate-900 leading-tight">Amina Benali</h4>
                <p className="text-xs text-slate-500">Patient ID: #TC-4819</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-[#004d55] text-white flex items-center justify-center shadow-xs">
                <User className="w-5 h-5" />
              </div>
            </div>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 p-6 sm:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
};
