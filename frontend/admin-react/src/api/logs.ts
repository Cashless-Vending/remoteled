import { apiClient } from './client'
import type { SystemLog } from '../types'

export const logsApi = {
  async getRecent(limit: number = 50, errorOnly: boolean = false): Promise<SystemLog[]> {
    const query = new URLSearchParams({
      limit: String(limit)
    })

    if (errorOnly) {
      query.append('error_only', 'true')
    }

    return apiClient.get<SystemLog[]>(`/admin/logs/recent?${query.toString()}`)
  }
}


