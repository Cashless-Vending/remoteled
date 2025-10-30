import { useState, useEffect, useCallback } from 'react'
import { statsApi } from '../api'
import { Stats, Order } from '../types'

export const useStats = (autoRefresh = false, interval = 30000) => {
  const [stats, setStats] = useState<Stats | null>(null)
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      const [statsData, ordersData] = await Promise.all([
        statsApi.getOverview(),
        statsApi.getRecentOrders(20)
      ])
      setStats(statsData)
      setOrders(ordersData)
      setError(null)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()

    if (autoRefresh) {
      const intervalId = setInterval(fetchData, interval)
      return () => clearInterval(intervalId)
    }
  }, [fetchData, autoRefresh, interval])

  return {
    stats,
    orders,
    loading,
    error,
    refetch: fetchData
  }
}

