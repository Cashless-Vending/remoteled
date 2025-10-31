/**
 * Utility functions for RemoteLED Admin Console
 */
import { format, formatDistanceToNow } from 'date-fns';
import type { ServiceType } from '../types';

/**
 * Format cents to currency string
 */
export const formatCurrency = (cents: number): string => {
  return `$${(cents / 100).toFixed(2)}`;
};

/**
 * Format date to locale string
 */
export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return format(date, 'MM/dd/yyyy HH:mm:ss');
};

/**
 * Format time only
 */
export const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return format(date, 'HH:mm:ss');
};

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  return formatDistanceToNow(date, { addSuffix: true });
};

/**
 * Truncate UUID or long string
 */
export const truncateId = (id: string, length = 12): string => {
  return id.substring(0, length);
};

/**
 * Get LED color description from service type
 */
export const getLedColor = (type: ServiceType): string => {
  const colorMap: Record<ServiceType, string> = {
    TRIGGER: '🔵 Blue Blink',
    FIXED: '🟢 Green Solid',
    VARIABLE: '🟠 Amber Solid',
  };
  return colorMap[type] || '⚪ Default';
};

/**
 * Get duration text based on service type
 */
export const getDurationText = (
  type: ServiceType,
  fixedMinutes?: number,
  _minutesPer25c?: number
): string => {
  if (type === 'TRIGGER') {
    return '2 seconds';
  } else if (type === 'FIXED' && fixedMinutes) {
    return `${fixedMinutes} minutes`;
  } else if (type === 'VARIABLE') {
    return 'Variable duration';
  }
  return 'N/A';
};

/**
 * Get change indicator (up/down arrow)
 */
export const getChangeSymbol = (value: number): string => {
  return value >= 0 ? '↑' : '↓';
};

/**
 * Export data to CSV
 */
export const exportToCSV = (data: any[], filename: string): void => {
  if (data.length === 0) return;

  // Get headers from first object
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map((row) =>
      headers
        .map((header) => {
          const value = row[header]?.toString() || '';
          // Escape commas and quotes
          if (value.includes(',') || value.includes('"')) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        })
        .join(',')
    ),
  ].join('\n');

  // Create download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}_${format(new Date(), 'yyyy-MM-dd')}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  return emailRegex.test(email);
};

/**
 * Get status badge color class
 */
export const getStatusColor = (status: string): string => {
  const statusColors: Record<string, string> = {
    ACTIVE: 'bg-green-100 text-green-800',
    OFFLINE: 'bg-red-100 text-red-800',
    MAINTENANCE: 'bg-orange-100 text-orange-800',
    DEACTIVATED: 'bg-gray-100 text-gray-800',
    CREATED: 'bg-blue-100 text-blue-800',
    PAID: 'bg-green-100 text-green-800',
    RUNNING: 'bg-orange-100 text-orange-800',
    DONE: 'bg-purple-100 text-purple-800',
    FAILED: 'bg-red-100 text-red-800',
  };
  return statusColors[status] || 'bg-gray-100 text-gray-800';
};

/**
 * Calculate percentage
 */
export const calculatePercentage = (value: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
};

/**
 * Debounce function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

