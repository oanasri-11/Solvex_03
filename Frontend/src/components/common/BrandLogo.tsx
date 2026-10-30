import React from 'react';
import logoSvg from '../../assets/logo/Logo.svg';

interface BrandLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showSubtitle?: boolean;
  subtitleText?: string;
  horizontal?: boolean;
  className?: string;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  size = 'md',
  showSubtitle = false,
  subtitleText = 'Doctor workspace',
  horizontal = false,
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  };

  if (horizontal) {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <div className="relative flex items-center justify-center">
          <img 
            src={logoSvg} 
            alt="TensioCare Logo" 
            className="w-10 h-10 object-contain rounded-full"
          />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-slate-900 text-xl tracking-tight">TensioCare</span>
          </div>
          {showSubtitle && (
            <p className="text-xs text-slate-500 font-medium">{subtitleText}</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center justify-center text-center ${className}`}>
      <div className={`relative ${sizeClasses[size]} mb-1.5 flex items-center justify-center`}>
        <img 
          src={logoSvg} 
          alt="TensioCare Logo" 
          className="w-full h-full object-contain"
        />
      </div>
      {showSubtitle && (
        <span className="text-xs text-slate-500 font-medium tracking-tight mt-0.5">
          {subtitleText}
        </span>
      )}
    </div>
  );
};
