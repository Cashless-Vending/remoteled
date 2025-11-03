import { useState, useEffect, useCallback } from 'react'
import { devicesApi } from '../api'
import { Device, DeviceCreateRequest, DeviceUpdateRequest } from '../types'

export const useDevices = (autoRefresh = false, interval = 30000) => {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const parseError = (err: any) => {
    if (err?.message) {
      return err.message
    }
    return 'Unexpected device error'
  }

  const fetchDevices = useCallback(async () => {
    setLoading(true)
    try {
      const data = await devicesApi.getAll()
      setDevices(data)
      setError(null)
    } catch (err: any) {
      setError(parseError(err))
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
    try {
      const newDevice = await devicesApi.create(device)
      await fetchDevices()
      return newDevice
    } catch (err: any) {
      const message = parseError(err)
      setError(message)
      throw new Error(message)
    }
  }

  const updateDevice = async (id: string, device: DeviceUpdateRequest): Promise<Device> => {
    try {
      const updated = await devicesApi.update(id, device)
      await fetchDevices()
      return updated
    } catch (err: any) {
      const message = parseError(err)
      setError(message)
      throw new Error(message)
    }
  }

  const deleteDevice = async (id: string): Promise<void> => {
    try {
      await devicesApi.delete(id)
      await fetchDevices()
    } catch (err: any) {
      const message = parseError(err)
      setError(message)
      throw new Error(message)
    }
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

