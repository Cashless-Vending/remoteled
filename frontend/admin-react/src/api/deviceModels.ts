import { apiClient } from './client'
import type { DeviceModel, DeviceModelCreate, DeviceModelUpdate } from '../types/reference'

export const deviceModelsApi = {
  /**
   * Get all device models
   */
  async getAll(): Promise<DeviceModel[]> {
    return apiClient.get<DeviceModel[]>('/admin/device-models')
  },

  /**
   * Get a specific device model by ID
   */
  async getById(id: string): Promise<DeviceModel> {
    return apiClient.get<DeviceModel>(`/admin/device-models/${id}`)
  },

  /**
   * Create a new device model
   */
  async create(data: DeviceModelCreate): Promise<DeviceModel> {
    return apiClient.post<DeviceModel>('/admin/device-models', data)
  },

  /**
   * Update an existing device model
   */
  async update(id: string, data: DeviceModelUpdate): Promise<DeviceModel> {
    return apiClient.put<DeviceModel>(`/admin/device-models/${id}`, data)
  },

  /**
   * Delete a device model
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/admin/device-models/${id}`)
  }
}

