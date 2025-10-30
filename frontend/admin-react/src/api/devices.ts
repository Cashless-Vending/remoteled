import { apiClient } from './client'
import { Device, DeviceCreateRequest, DeviceUpdateRequest } from '../types'

export const devicesApi = {
  async getAll(): Promise<Device[]> {
    return apiClient.get<Device[]>('/admin/devices/all')
  },

  async create(device: DeviceCreateRequest): Promise<Device> {
    return apiClient.post<Device>('/admin/devices', device)
  },

  async update(id: string, device: DeviceUpdateRequest): Promise<Device> {
    return apiClient.put<Device>(`/admin/devices/${id}`, device)
  },

  async delete(id: string): Promise<{ success: boolean; message: string }> {
    return apiClient.delete(`/admin/devices/${id}`)
  }
}

