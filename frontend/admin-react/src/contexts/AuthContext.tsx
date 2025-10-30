import { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import { authApi } from '../api'
import { User, LoginRequest } from '../types'
import { AUTH_TOKEN_KEY, USER_EMAIL_KEY } from '../config/constants'

interface AuthContextType {
  isAuthenticated: boolean
  user: User | null
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem(AUTH_TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem(AUTH_TOKEN_KEY)
    const email = localStorage.getItem(USER_EMAIL_KEY)
    
    if (token && email) {
      setIsAuthenticated(true)
      // You could fetch user details here if needed
      setUser({ id: '', email, role: 'admin' })
    }
    setLoading(false)
  }, [])

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await authApi.login(credentials)
      localStorage.setItem(AUTH_TOKEN_KEY, response.access_token)
      localStorage.setItem(USER_EMAIL_KEY, response.user.email)
      setIsAuthenticated(true)
      setUser(response.user)
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(USER_EMAIL_KEY)
    setIsAuthenticated(false)
    setUser(null)
    // Optionally call authApi.logout() if you want to log on server
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

