import { useState, useEffect, useCallback } from 'react'
import { servicesApi } from '../api'
import { Service, ServiceCreateRequest, ServiceUpdateRequest } from '../types'

export const useServices = (autoRefresh = false, interval = 30000) => {
  const [services, setServices] = useState<Service[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchServices = useCallback(async () => {
    try {
      const data = await servicesApi.getAll()
      setServices(data)
      setError(null)
    } catch (err: any) {
      setError(err.message)
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
    const newService = await servicesApi.create(service)
    await fetchServices()
    return newService
  }

  const updateService = async (id: string, service: ServiceUpdateRequest): Promise<Service> => {
    const updated = await servicesApi.update(id, service)
    await fetchServices()
    return updated
  }

  const deleteService = async (id: string): Promise<void> => {
    await servicesApi.delete(id)
    await fetchServices()
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

