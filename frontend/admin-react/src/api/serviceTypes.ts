import { apiClient } from './client'
import type { ServiceType, ServiceTypeCreate, ServiceTypeUpdate } from '../types/reference'

export const serviceTypesApi = {
  /**
   * Get all service types
   */
  async getAll(): Promise<ServiceType[]> {
    return apiClient.get<ServiceType[]>('/admin/service-types')
  },

  /**
   * Get a specific service type by ID
   */
  async getById(id: string): Promise<ServiceType> {
    return apiClient.get<ServiceType>(`/admin/service-types/${id}`)
  },

  /**
   * Create a new service type
   */
  async create(data: ServiceTypeCreate): Promise<ServiceType> {
    return apiClient.post<ServiceType>('/admin/service-types', data)
  },

  /**
   * Update an existing service type
   */
  async update(id: string, data: ServiceTypeUpdate): Promise<ServiceType> {
    return apiClient.put<ServiceType>(`/admin/service-types/${id}`, data)
  },

  /**
   * Delete a service type
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/admin/service-types/${id}`)
  }
}

