import { useState, useEffect, useCallback } from 'react'
import { serviceTypesApi } from '../api/serviceTypes'
import type { ServiceType, ServiceTypeCreate, ServiceTypeUpdate } from '../types/reference'

export const useServiceTypes = () => {
  const [serviceTypes, setServiceTypes] = useState<ServiceType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchServiceTypes = useCallback(async () => {
    try {
      setLoading(true)
      const data = await serviceTypesApi.getAll()
      setServiceTypes(data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch service types')
    } finally {
      setLoading(false)
    }
  }, [])

  const createServiceType = useCallback(async (data: ServiceTypeCreate): Promise<ServiceType> => {
    const newServiceType = await serviceTypesApi.create(data)
    setServiceTypes(prev => [...prev, newServiceType])
    return newServiceType
  }, [])

  const updateServiceType = useCallback(async (id: string, data: ServiceTypeUpdate): Promise<ServiceType> => {
    const updated = await serviceTypesApi.update(id, data)
    setServiceTypes(prev => prev.map(st => st.id === id ? updated : st))
    return updated
  }, [])

  const deleteServiceType = useCallback(async (id: string): Promise<void> => {
    await serviceTypesApi.delete(id)
    setServiceTypes(prev => prev.filter(st => st.id !== id))
  }, [])

  useEffect(() => {
    fetchServiceTypes()
  }, [fetchServiceTypes])

  return {
    serviceTypes,
    loading,
    error,
    fetchServiceTypes,
    createServiceType,
    updateServiceType,
    deleteServiceType
  }
}

