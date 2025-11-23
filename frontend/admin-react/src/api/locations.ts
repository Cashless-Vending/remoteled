import { apiClient } from './client'
import type { Location, LocationCreate, LocationUpdate } from '../types/reference'

export const locationsApi = {
  /**
   * Get all locations
   */
  async getAll(): Promise<Location[]> {
    const response = await apiClient.get('/admin/locations')
    return response.data
  },

  /**
   * Get a specific location by ID
   */
  async getById(id: string): Promise<Location> {
    const response = await apiClient.get(`/admin/locations/${id}`)
    return response.data
  },

  /**
   * Create a new location
   */
  async create(data: LocationCreate): Promise<Location> {
    const response = await apiClient.post('/admin/locations', data)
    return response.data
  },

  /**
   * Update an existing location
   */
  async update(id: string, data: LocationUpdate): Promise<Location> {
    const response = await apiClient.put(`/admin/locations/${id}`, data)
    return response.data
  },

  /**
   * Delete a location
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/admin/locations/${id}`)
  }
}

