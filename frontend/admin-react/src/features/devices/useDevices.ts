/**
 * Custom hook for device management
 */
import { useState, useCallback } from 'react';
import { devicesApi } from '../../core/api/client';
import type { Device, DeviceCreateRequest, DeviceUpdateRequest } from '../../core/types';

export const useDevices = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDevices = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await devicesApi.getAll();
      setDevices(data);
    } catch (err: any) {
      console.error('Error fetching devices:', err);
      setError(err.response?.data?.detail || 'Failed to load devices');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createDevice = useCallback(async (data: DeviceCreateRequest): Promise<Device> => {
    const device = await devicesApi.create(data);
    await fetchDevices();
    return device;
  }, [fetchDevices]);

  const updateDevice = useCallback(async (id: string, data: DeviceUpdateRequest): Promise<Device> => {
    const device = await devicesApi.update(id, data);
    await fetchDevices();
    return device;
  }, [fetchDevices]);

  const deleteDevice = useCallback(async (id: string): Promise<void> => {
    await devicesApi.delete(id);
    await fetchDevices();
  }, [fetchDevices]);

  return {
    devices,
    isLoading,
    error,
    fetchDevices,
    createDevice,
    updateDevice,
    deleteDevice,
  };
};


