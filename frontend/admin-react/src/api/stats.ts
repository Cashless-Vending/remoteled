import { apiClient } from './client'
import { Stats, Order } from '../types'

export interface LiveOrdersResponse {
  orders: Order[]
  summary: {
    active: number
    completed: number
    failed: number
    total: number
  }
  timestamp: string
}

export interface RealtimeStats {
  pending: number
  paid: number
  running: number
  completed: number
  failed: number
  revenue_24h_cents: number
  total_orders_24h: number
  orders_last_hour: number
  revenue_last_hour_cents: number
  timestamp: string
}

export const statsApi = {
  async getOverview(): Promise<Stats> {
    return apiClient.get<Stats>('/admin/stats/overview')
  },

  async getRecentOrders(limit: number = 20): Promise<Order[]> {
    return apiClient.get<Order[]>(`/admin/orders/recent?limit=${limit}`)
  },

  async getLiveOrders(): Promise<LiveOrdersResponse> {
    return apiClient.get<LiveOrdersResponse>('/admin/orders/live')
  },

  async getRealtimeStats(): Promise<RealtimeStats> {
    return apiClient.get<RealtimeStats>('/admin/orders/stats/realtime')
  }
}
