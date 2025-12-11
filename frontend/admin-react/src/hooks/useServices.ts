import { useState, useEffect, useCallback } from 'react'
import { servicesApi } from '../api'
import { Service, ServiceCreateRequest, ServiceUpdateRequest } from '../types'

export const useServices = (autoRefresh = false, interval = 30000) => {
  const [services, setServices] = useState<Service[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const parseError = (err: any) => {
    if (err?.message) {
      return err.message
    }
    return 'Unexpected service error'
  }

  const fetchServices = useCallback(async () => {
    setLoading(true)
    try {
      const data = await servicesApi.getAll()
      setServices(data)
      setError(null)
    } catch (err: any) {
      setError(parseError(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchServices()

    if (autoRefresh) {
      const intervalId = setInterval(fetchServices, interval)
      return () => clearInterval(intervalId)
    }
  }, [fetchServices, autoRefresh, interval])

  const createService = async (service: ServiceCreateRequest): Promise<Service> => {
    try {
      const newService = await servicesApi.create(service)
      await fetchServices()
      return newService
    } catch (err: any) {
      const message = parseError(err)
      setError(message)
      throw new Error(message)
    }
  }

  const updateService = async (id: string, service: ServiceUpdateRequest): Promise<Service> => {
    try {
      const updated = await servicesApi.update(id, service)
      await fetchServices()
      return updated
    } catch (err: any) {
      const message = parseError(err)
      setError(message)
      throw new Error(message)
    }
  }

  const deleteService = async (id: string): Promise<void> => {
    try {
      await servicesApi.delete(id)
      await fetchServices()
    } catch (err: any) {
      const message = parseError(err)
      setError(message)
      throw new Error(message)
    }
  }

  return {
    services,
    loading,
    error,
    fetchServices,
    createService,
    updateService,
    deleteService
  }
}

