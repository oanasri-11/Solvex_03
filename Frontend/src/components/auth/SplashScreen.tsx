import React, { useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { BrandLogo } from '../common/BrandLogo';
import { ArrowRight, Sparkles } from 'lucide-react';

export const SplashScreen: React.FC = () => {
  const { setAuthView } = useApp();

  // Auto transition after 2.5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      setAuthView('login');
    }, 2500);
    return () => clearTimeout(timer);
  }, [setAuthView]);

  return (
    <div 
      onClick={() => setAuthView('login')}
      className="min-h-screen bg-gradient-to-b from-[#f0f9f8] via-[#f8fafc] to-[#e6f4f1] flex flex-col items-center justify-between p-8 cursor-pointer select-none transition-all duration-500 relative overflow-hidden"
    >
      {/* Background ambient decorative glow circles */}
      <div className="absolute -top-32 -right-32 w-96 h-96 bg-teal-200/40 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-emerald-200/40 rounded-full blur-3xl pointer-events-none"></div>

      {/* Top indicator */}
      <div className="pt-4 flex items-center gap-2 text-xs font-semibold text-[#0d6269] bg-white/70 backdrop-blur-xs px-4 py-1.5 rounded-full border border-teal-100 shadow-2xs">
        <Sparkles className="w-3.5 h-3.5 text-teal-600" />
      </div>

      {/* Center Brand Hero */}
      <div className="flex flex-col items-center justify-center max-w-md w-full text-center my-auto py-8 space-y-6">
        {/* Scaled-up Logo */}
        <div className="p-4 bg-white/60 backdrop-blur-xs rounded-3xl border border-teal-100/60 shadow-lg shadow-teal-900/5 transition-transform hover:scale-105 duration-300">
          <BrandLogo 
            size="xl" 
            showTitle={true} 
            showSubtitle={true}
            subtitleText="Clinical Telemonitoring Platform"
          />
        </div>

        {/* Tagline */}
        <p className="text-sm text-slate-600 font-medium max-w-xs leading-relaxed">
          متابعة دقيقة لضغط الدم والمؤشرات الحيوية برعاية فريقك الطبي
        </p>

        {/* Loading Spinner & Progress */}
        <div className="flex flex-col items-center justify-center space-y-3 pt-2">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#0d6269] animate-bounce"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#0d6269] animate-bounce [animation-delay:0.15s]"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#0d6269] animate-bounce [animation-delay:0.3s]"></span>
          </div>
          <p className="text-xs text-slate-400 font-medium tracking-wide">
            جاري تحضير المنصة • Getting ready...
          </p>
        </div>

        {/* Instant Continue Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            setAuthView('login');
          }}
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-[#004d55] hover:bg-teal-900 text-white font-bold text-xs shadow-md shadow-teal-900/10 transition-all hover:scale-102"
        >
          <span>الدخول إلى منصة روض</span>
          <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
        </button>
      </div>

      {/* Bottom hint */}
      <div className="pb-4 text-xs text-slate-400 font-medium">
        انقر في أي مكان للمتابعة • Click anywhere to continue to روض
      </div>
    </div>
  );
};
