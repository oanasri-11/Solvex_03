import React from 'react';
import logoPng from '../../assets/logo/Logo.png';

interface BrandLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showTitle?: boolean;
  showSubtitle?: boolean;
  subtitleText?: string;
  horizontal?: boolean;
  className?: string;
  imgClassName?: string;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  size = 'md',
  showTitle = true,
  showSubtitle = false,
  subtitleText = '',
  horizontal = false,
  className = '',
  imgClassName = ''
}) => {
  // Appropriately scaled-up dimensions so the emblem calligraphy is large and distinct
  const sizeConfig = {
    sm: {
      box: 'w-12 h-12',
      img: 'w-12 h-12 scale-125',
      title: 'text-xl',
      sub: 'text-[11px]'
    },
    md: {
      box: 'w-20 h-20',
      img: 'w-20 h-20 scale-125',
      title: 'text-2xl',
      sub: 'text-xs'
    },
    lg: {
      box: 'w-28 h-28',
      img: 'w-28 h-28 scale-125',
      title: 'text-3xl',
      sub: 'text-sm'
    },
    xl: {
      box: 'w-48 h-48 sm:w-60 sm:h-60',
      img: 'w-full h-full scale-135',
      title: 'text-4xl sm:text-5xl',
      sub: 'text-base'
    }
  };

  const config = sizeConfig[size];

  if (horizontal) {
    return (
      <div className={`flex items-center gap-3.5 ${className}`}>
        <div className={`relative flex items-center justify-center shrink-0 ${config.box}`}>
          <img 
            src={logoPng} 
            alt="روض" 
            className={`object-contain mix-blend-multiply drop-shadow-xs transition-transform ${config.img} ${imgClassName}`}
          />
        </div>
        <div>
          {showTitle && (
            <div className="flex items-center gap-1.5">
              <span className={`font-black text-[#004d55] ${config.title} tracking-tight font-['Cairo',sans-serif] leading-tight`}>
                روض
              </span>
            </div>
          )}
          {showSubtitle && subtitleText && (
            <p className={`${config.sub} text-slate-500 font-medium tracking-tight mt-0.5`}>
              {subtitleText}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center justify-center text-center ${className}`}>
      <div className={`relative ${config.box} mb-1 flex items-center justify-center`}>
        <img 
          src={logoPng} 
          alt="روض" 
          className={`object-contain mix-blend-multiply drop-shadow-xs transition-transform ${config.img} ${imgClassName}`}
        />
      </div>
      {showTitle && (
        <span className={`font-black text-[#004d55] ${config.title} tracking-tight font-['Cairo',sans-serif] leading-tight`}>
          {/* روض */}
        </span>
      )}
      {showSubtitle && subtitleText && (
        <span className={`${config.sub} text-slate-500 font-medium tracking-tight mt-0.5`}>
          {subtitleText}
        </span>
      )}
    </div>
  );
};
