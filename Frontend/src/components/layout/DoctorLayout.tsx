import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { BrandLogo } from '../common/BrandLogo';
import { Home, Bell, Users, ChevronRight, Menu, X, LogOut, ShieldCheck } from 'lucide-react';

interface DoctorLayoutProps {
  children: React.ReactNode;
}

export const DoctorLayout: React.FC<DoctorLayoutProps> = ({ children }) => {
  const { doctorView, setDoctorView, selectedPatient, logout, currentUser } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const getBreadcrumb = () => {
    switch (doctorView) {
      case 'home':
        return <span>Home</span>;
      case 'patients':
        return <span>Patients</span>;
      case 'alerts':
        return <span>Alerts</span>;
      case 'patient_detail':
        return (
          <div className="flex items-center gap-1.5 text-slate-600">
            <button 
              onClick={() => setDoctorView('patients')} 
              className="hover:text-teal-700 transition-colors"
            >
              Patients
            </button>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-900 font-medium">{selectedPatient.name}</span>
          </div>
        );
      case 'patient_review':
        return (
          <div className="flex items-center gap-1.5 text-slate-600">
            <button 
              onClick={() => setDoctorView('patients')} 
              className="hover:text-teal-700 transition-colors"
            >
              Patients
            </button>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
            <button 
              onClick={() => setDoctorView('patient_detail')} 
              className="hover:text-teal-700 transition-colors"
            >
              {selectedPatient.name}
            </button>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-900 font-medium">Patient review</span>
          </div>
        );
      default:
        return <span>Home</span>;
    }
  };

  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'patients', label: 'Patients', icon: Users },
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
            <BrandLogo 
              size="md" 
              showTitle={true} 
              showSubtitle={true} 
              subtitleText="Doctor workspace" 
            />
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
              const isActive = doctorView === item.id || 
                (item.id === 'patients' && (doctorView === 'patient_detail' || doctorView === 'patient_review'));

              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setDoctorView(item.id as any);
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

        {/* Doctor workspace footer & Logout */}
        <div className="p-5 border-t border-slate-100 space-y-3">
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <div className="text-[11px]">
                <p className="font-bold text-slate-800">روض Telemonitoring</p>
                <p className="text-slate-400">Clinical Mode Active</p>
              </div>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          </div>

          {/* User info card with logout button */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-full bg-[#e0f2f1] text-[#0d6269] font-bold text-xs flex items-center justify-center shrink-0">
                {currentUser?.full_name ? currentUser.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : 'DR'}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-bold text-slate-800 truncate">{currentUser?.full_name || 'Doctor'}</p>
                <p className="text-[10px] text-slate-400 truncate">Cardiologist</p>
              </div>
            </div>

            <button
              onClick={logout}
              title="Log out of Doctor Workspace"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
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
            <div className="text-sm font-medium text-slate-500">
              {getBreadcrumb()}
            </div>
          </div>

          {/* User profile & quick exit */}
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <h4 className="text-sm font-bold text-slate-900 leading-tight">{currentUser?.full_name || 'Doctor'}</h4>
              <p className="text-xs text-slate-500">Consultant Cardiologist</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-[#e0f2f1] text-[#0d6269] font-bold text-sm flex items-center justify-center border border-teal-100 shadow-sm">
              {currentUser?.full_name ? currentUser.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : 'DR'}
            </div>
            <button
              onClick={logout}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600 bg-rose-50/80 hover:bg-rose-100 rounded-lg border border-rose-100 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Log out</span>
            </button>
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
