import { apiClient } from './client'
import type { Location, LocationCreate, LocationUpdate } from '../types/reference'

export const locationsApi = {
  /**
   * Get all locations
   */
  async getAll(): Promise<Location[]> {
    return apiClient.get<Location[]>('/admin/locations')
  },

  /**
   * Get a specific location by ID
   */
  async getById(id: string): Promise<Location> {
    return apiClient.get<Location>(`/admin/locations/${id}`)
  },

  /**
   * Create a new location
   */
  async create(data: LocationCreate): Promise<Location> {
    return apiClient.post<Location>('/admin/locations', data)
  },

  /**
   * Update an existing location
   */
  async update(id: string, data: LocationUpdate): Promise<Location> {
    return apiClient.put<Location>(`/admin/locations/${id}`, data)
  },

  /**
   * Delete a location
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/admin/locations/${id}`)
  }
}

