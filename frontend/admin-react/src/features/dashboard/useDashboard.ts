/**
 * Custom hook for dashboard data fetching
 */
import { useState, useEffect, useCallback } from 'react';
import { statsApi } from '../../core/api/client';
import type { DashboardStats, OrdersChartData, DeviceStatusData } from '../../core/types';

export const useDashboard = (autoRefresh = true) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [ordersChart, setOrdersChart] = useState<OrdersChartData[]>([]);
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatusData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const [statsData, ordersData, deviceData] = await Promise.all([
        statsApi.getOverview(),
        statsApi.getOrdersLast7Days(),
        statsApi.getDeviceStatus(),
      ]);

      setStats(statsData);
      setOrdersChart(ordersData);
      setDeviceStatus(deviceData);
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    // Auto-refresh every 30 seconds
    if (autoRefresh) {
      const interval = setInterval(fetchData, 30000);
      return () => clearInterval(interval);
    }
  }, [fetchData, autoRefresh]);

  return {
    stats,
    ordersChart,
    deviceStatus,
    isLoading,
    error,
    refetch: fetchData,
  };
};


