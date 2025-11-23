import { apiClient } from './client'
import type { DeviceModel, DeviceModelCreate, DeviceModelUpdate } from '../types/reference'

export const deviceModelsApi = {
  /**
   * Get all device models
   */
  async getAll(): Promise<DeviceModel[]> {
    const response = await apiClient.get('/admin/device-models')
    return response.data
  },

  /**
   * Get a specific device model by ID
   */
  async getById(id: string): Promise<DeviceModel> {
    const response = await apiClient.get(`/admin/device-models/${id}`)
    return response.data
  },

  /**
   * Create a new device model
   */
  async create(data: DeviceModelCreate): Promise<DeviceModel> {
    const response = await apiClient.post('/admin/device-models', data)
    return response.data
  },

  /**
   * Update an existing device model
   */
  async update(id: string, data: DeviceModelUpdate): Promise<DeviceModel> {
    const response = await apiClient.put(`/admin/device-models/${id}`, data)
    return response.data
  },

  /**
   * Delete a device model
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/admin/device-models/${id}`)
  }
}

