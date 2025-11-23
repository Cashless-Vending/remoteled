import { apiClient } from './client'
import type { ServiceType, ServiceTypeCreate, ServiceTypeUpdate } from '../types/reference'

export const serviceTypesApi = {
  /**
   * Get all service types
   */
  async getAll(): Promise<ServiceType[]> {
    const response = await apiClient.get('/admin/service-types')
    return response.data
  },

  /**
   * Get a specific service type by ID
   */
  async getById(id: string): Promise<ServiceType> {
    const response = await apiClient.get(`/admin/service-types/${id}`)
    return response.data
  },

  /**
   * Create a new service type
   */
  async create(data: ServiceTypeCreate): Promise<ServiceType> {
    const response = await apiClient.post('/admin/service-types', data)
    return response.data
  },

  /**
   * Update an existing service type
   */
  async update(id: string, data: ServiceTypeUpdate): Promise<ServiceType> {
    const response = await apiClient.put(`/admin/service-types/${id}`, data)
    return response.data
  },

  /**
   * Delete a service type
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/admin/service-types/${id}`)
  }
}

