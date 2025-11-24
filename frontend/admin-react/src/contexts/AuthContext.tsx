import { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import { onAuthStateChanged, User as FirebaseUser } from 'firebase/auth'
import { auth } from '../config/firebase'
import { firebaseAuthService } from '../services/firebaseAuth'

export interface User {
  id: string
  email: string
  displayName?: string | null
  emailVerified: boolean
}

interface AuthContextType {
  isAuthenticated: boolean
  user: User | null
  firebaseUser: FirebaseUser | null
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, displayName?: string) => Promise<void>
  logout: () => Promise<void>
  resetPassword: (email: string) => Promise<void>
  getIdToken: () => Promise<string | null>
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Listen to Firebase auth state changes
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        // User is signed in
        setFirebaseUser(firebaseUser)
        setUser({
          id: firebaseUser.uid,
          email: firebaseUser.email || '',
          displayName: firebaseUser.displayName,
          emailVerified: firebaseUser.emailVerified
        })
      } else {
        // User is signed out
        setFirebaseUser(null)
        setUser(null)
      }
      setLoading(false)
    })

    // Cleanup subscription on unmount
    return () => unsubscribe()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      await firebaseAuthService.signIn(email, password)
      // onAuthStateChanged will handle setting the user
    } catch (error: any) {
      console.error('Login error:', error)
      throw error
    }
  }

  const signup = async (email: string, password: string, displayName?: string) => {
    try {
      await firebaseAuthService.signUp(email, password, displayName)
      // onAuthStateChanged will handle setting the user
    } catch (error: any) {
      console.error('Signup error:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      await firebaseAuthService.signOut()
      // onAuthStateChanged will handle clearing the user
    } catch (error: any) {
      console.error('Logout error:', error)
      throw error
    }
  }

  const resetPassword = async (email: string) => {
    try {
      await firebaseAuthService.resetPassword(email)
    } catch (error: any) {
      console.error('Reset password error:', error)
      throw error
    }
  }

  const getIdToken = async (): Promise<string | null> => {
    return await firebaseAuthService.getIdToken()
  }

  const isAuthenticated = !!firebaseUser

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      user, 
      firebaseUser,
      login, 
      signup,
      logout, 
      resetPassword,
      getIdToken,
      loading 
    }}>
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
