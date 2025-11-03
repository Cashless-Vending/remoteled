import { useCallback, useEffect, useState } from 'react'
import { logsApi } from '../api'
import type { SystemLog } from '../types'

export const useLogs = (autoRefresh = false, interval = 60000) => {
  const [logs, setLogs] = useState<SystemLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchLogs = useCallback(async () => {
    try {
      setLoading(true)
      const data = await logsApi.getRecent(100)
      setLogs(data)
      setError(null)
    } catch (err: any) {
      setError(err?.message || 'Unable to load logs')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchLogs()

    if (autoRefresh) {
      const timer = setInterval(fetchLogs, interval)
      return () => clearInterval(timer)
    }
  }, [fetchLogs, autoRefresh, interval])

  return {
    logs,
    loading,
    error,
    refetch: fetchLogs
  }
}


