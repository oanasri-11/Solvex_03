import React from 'react';

export type BadgeVariant = 
  | 'crisis' 
  | 'high_priority' 
  | 'urgent' 
  | 'within_target' 
  | 'under_follow_up' 
  | 'emergency' 
  | 'caution' 
  | 'information' 
  | 'action_needed' 
  | 'review_needed' 
  | 'check_needed'
  | 'normal'
  | 'moderately_high'
  | 'outline'
  | 'protocol';

interface BadgeProps {
  variant: BadgeVariant;
  children: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant,
  children,
  icon,
  className = ''
}) => {
  const styles: Record<BadgeVariant, string> = {
    crisis: 'bg-rose-50 text-rose-700 border border-rose-100 font-medium',
    emergency: 'bg-rose-50 text-rose-700 border border-rose-200 font-medium',
    high_priority: 'bg-orange-50 text-orange-800 border border-orange-100 font-medium',
    urgent: 'bg-rose-50 text-rose-600 border border-rose-100 font-medium',
    within_target: 'bg-[#e6f4f1] text-[#0d6269] border border-teal-100 font-medium',
    normal: 'bg-[#e6f4f1] text-[#0d6269] border border-teal-100 font-medium',
    under_follow_up: 'bg-amber-50 text-amber-800 border border-amber-100 font-medium',
    caution: 'bg-amber-50 text-amber-800 border border-amber-200 font-medium',
    information: 'bg-sky-50 text-sky-700 border border-sky-200 font-medium',
    action_needed: 'bg-slate-100 text-slate-700 font-medium',
    review_needed: 'bg-slate-100 text-slate-700 font-medium',
    check_needed: 'bg-slate-100 text-slate-700 font-medium',
    moderately_high: 'bg-amber-50 text-amber-700 border border-amber-100 font-medium',
    outline: 'border border-slate-200 text-slate-600 bg-white font-medium',
    protocol: 'bg-[#e6f4f1] text-[#0d6269] font-medium'
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs transition-colors ${styles[variant]} ${className}`}
    >
      {icon}
      <span>{children}</span>
    </span>
  );
};
