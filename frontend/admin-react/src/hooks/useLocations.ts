import { useState, useEffect, useCallback } from 'react'
import { locationsApi } from '../api/locations'
import type { Location, LocationCreate, LocationUpdate } from '../types/reference'

export const useLocations = () => {
  const [locations, setLocations] = useState<Location[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchLocations = useCallback(async () => {
    try {
      setLoading(true)
      const data = await locationsApi.getAll()
      setLocations(data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch locations')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchLocations()
  }, [fetchLocations])

  const createLocation = useCallback(async (data: LocationCreate) => {
    const newLocation = await locationsApi.create(data)
    setLocations(prev => [...prev, newLocation])
    return newLocation
  }, [])

  const updateLocation = useCallback(async (id: string, data: LocationUpdate) => {
    const updatedLocation = await locationsApi.update(id, data)
    setLocations(prev => prev.map(l => l.id === id ? updatedLocation : l))
    return updatedLocation
  }, [])

  const deleteLocation = useCallback(async (id: string) => {
    await locationsApi.delete(id)
    setLocations(prev => prev.filter(l => l.id !== id))
  }, [])

  return {
    locations,
    loading,
    error,
    fetchLocations,
    createLocation,
    updateLocation,
    deleteLocation
  }
}

