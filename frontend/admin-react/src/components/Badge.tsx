/**
 * Reusable Badge Component for status indicators
 */
import type { ReactNode } from 'react';
import { getStatusColor } from '../core/utils';

interface BadgeProps {
  children: ReactNode;
  variant?: string;
  className?: string;
}

export const Badge = ({ children, variant, className = '' }: BadgeProps) => {
  const colorClass = variant ? getStatusColor(variant) : 'bg-gray-100 text-gray-800';
  
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase ${colorClass} ${className}`}
    >
      {children}
    </span>
  );
};

