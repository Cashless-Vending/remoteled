import { useState, useEffect, useCallback } from 'react'
import { deviceModelsApi } from '../api/deviceModels'
import type { DeviceModel, DeviceModelCreate, DeviceModelUpdate } from '../types/reference'

export const useDeviceModels = () => {
  const [models, setModels] = useState<DeviceModel[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchModels = useCallback(async () => {
    try {
      setLoading(true)
      const data = await deviceModelsApi.getAll()
      setModels(data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch device models')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchModels()
  }, [fetchModels])

  const createModel = useCallback(async (data: DeviceModelCreate) => {
    const newModel = await deviceModelsApi.create(data)
    setModels(prev => [...prev, newModel])
    return newModel
  }, [])

  const updateModel = useCallback(async (id: string, data: DeviceModelUpdate) => {
    const updatedModel = await deviceModelsApi.update(id, data)
    setModels(prev => prev.map(m => m.id === id ? updatedModel : m))
    return updatedModel
  }, [])

  const deleteModel = useCallback(async (id: string) => {
    await deviceModelsApi.delete(id)
    setModels(prev => prev.filter(m => m.id !== id))
  }, [])

  return {
    models,
    loading,
    error,
    fetchModels,
    createModel,
    updateModel,
    deleteModel
  }
}

