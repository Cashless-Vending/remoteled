import { useState, useEffect, useCallback } from 'react'
import { devicesApi } from '../api'
import { Device, DeviceCreateRequest, DeviceUpdateRequest } from '../types'

export const useDevices = (autoRefresh = false, interval = 30000) => {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDevices = useCallback(async () => {
    try {
      const data = await devicesApi.getAll()
      setDevices(data)
      setError(null)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDevices()

    if (autoRefresh) {
      const intervalId = setInterval(fetchDevices, interval)
      return () => clearInterval(intervalId)
    }
  }, [fetchDevices, autoRefresh, interval])

  const createDevice = async (device: DeviceCreateRequest): Promise<Device> => {
    const newDevice = await devicesApi.create(device)
    await fetchDevices()
    return newDevice
  }

  const updateDevice = async (id: string, device: DeviceUpdateRequest): Promise<Device> => {
    const updated = await devicesApi.update(id, device)
    await fetchDevices()
    return updated
  }

  const deleteDevice = async (id: string): Promise<void> => {
    await devicesApi.delete(id)
    await fetchDevices()
  }

  return {
    devices,
    loading,
    error,
    fetchDevices,
    createDevice,
    updateDevice,
    deleteDevice
  }
}

