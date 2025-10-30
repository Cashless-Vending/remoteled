import { API_BASE_URL, AUTH_TOKEN_KEY } from '../config/constants'

export interface ApiResponse<T> {
  data?: T
  error?: string
}

export const getAuthToken = (): string => {
  return localStorage.getItem(AUTH_TOKEN_KEY) || ''
}

export const apiClient = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
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
      headers['Authorization'] = `Bearer ${getAuthToken()}`
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
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
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
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return response.json()
  }
}

