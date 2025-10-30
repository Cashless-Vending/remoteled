import { apiClient } from './client'
import { Service, ServiceCreateRequest, ServiceUpdateRequest } from '../types'

export const servicesApi = {
  async getAll(): Promise<Service[]> {
    return apiClient.get<Service[]>('/admin/services/all')
  },

  async create(service: ServiceCreateRequest): Promise<Service> {
    return apiClient.post<Service>('/admin/services', service)
  },

  async update(id: string, service: ServiceUpdateRequest): Promise<Service> {
    return apiClient.put<Service>(`/admin/services/${id}`, service)
  },

  async delete(id: string): Promise<{ success: boolean; message: string }> {
    return apiClient.delete(`/admin/services/${id}`)
  }
}

