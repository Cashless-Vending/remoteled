import { apiClient } from './client'
import { LoginRequest, LoginResponse, User } from '../types'

export const authApi = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return apiClient.post<LoginResponse>('/auth/login', credentials, false)
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me')
  },

  async logout(): Promise<{ message: string }> {
    return apiClient.post('/auth/logout', {})
  }
}

