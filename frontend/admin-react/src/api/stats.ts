import { apiClient } from './client'
import { Stats, Order } from '../types'

export const statsApi = {
  async getOverview(): Promise<Stats> {
    return apiClient.get<Stats>('/admin/stats/overview')
  },

  async getRecentOrders(limit: number = 20): Promise<Order[]> {
    return apiClient.get<Order[]>(`/admin/orders/recent?limit=${limit}`)
  }
}

