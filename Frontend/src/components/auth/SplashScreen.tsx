import React from 'react';
import { useApp } from '../../context/AppContext';
import { BrandLogo } from '../common/BrandLogo';

export const SplashScreen: React.FC = () => {
  const { setAuthView } = useApp();

  return (
    <div 
      onClick={() => setAuthView('login')}
      className="min-h-screen bg-[#f8fafc] flex flex-col items-center justify-center p-6 cursor-pointer select-none animate-fadeIn"
    >
      <div className="flex flex-col items-center justify-center space-y-12 max-w-sm w-full text-center">
        {/* Brand Logo with Arabic */}
        <div className="transform scale-125">
          <BrandLogo size="xl" showSubtitle={false} />
        </div>

        {/* Loading Spinner & Status */}
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="w-6 h-6 border-2 border-teal-600/30 border-t-teal-700 rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400 font-medium tracking-wide">
            Getting things ready
          </p>
        </div>
      </div>

      <div className="absolute bottom-8 text-[11px] text-slate-400">
        Click anywhere to continue to TensioCare portal
      </div>
    </div>
  );
};
