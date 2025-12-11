import { API_BASE_URL } from '../config/constants'

export interface ApiResponse<T> {
  data?: T
  error?: string
}

const TOKEN_KEY = 'remoteled_auth_token'

/**
 * Get JWT token from localStorage for authentication
 */
export const getAuthToken = (): string => {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export const apiClient = {
  async get<T>(endpoint: string): Promise<T> {
    const token = getAuthToken()
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return response.json()
  },

  async post<T>(endpoint: string, body: any, requireAuth = true): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    }
    
    if (requireAuth) {
      const token = getAuthToken()
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return response.json()
  },

  async put<T>(endpoint: string, body: any): Promise<T> {
    const token = getAuthToken()
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return response.json()
  },

  async delete(endpoint: string): Promise<{ success: boolean; message: string }> {
    const token = getAuthToken()
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return response.json()
  }
}
