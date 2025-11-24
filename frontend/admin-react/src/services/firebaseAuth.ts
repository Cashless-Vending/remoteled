import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  sendPasswordResetEmail,
  sendEmailVerification,
  updateProfile,
  User,
  UserCredential
} from 'firebase/auth'
import { auth } from '../config/firebase'

export interface FirebaseAuthService {
  signUp: (email: string, password: string, displayName?: string) => Promise<UserCredential>
  signIn: (email: string, password: string) => Promise<UserCredential>
  signOut: () => Promise<void>
  resetPassword: (email: string) => Promise<void>
  sendVerificationEmail: (user: User) => Promise<void>
  getCurrentUser: () => User | null
  getIdToken: () => Promise<string | null>
}

class FirebaseAuth implements FirebaseAuthService {
  /**
   * Sign up a new user with email and password
   */
  async signUp(email: string, password: string, displayName?: string): Promise<UserCredential> {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password)
      
      // Update display name if provided
      if (displayName && userCredential.user) {
        await updateProfile(userCredential.user, { displayName })
      }
      
      // Send verification email
      if (userCredential.user) {
        await this.sendVerificationEmail(userCredential.user)
      }
      
      return userCredential
    } catch (error: any) {
      throw this.handleAuthError(error)
    }
  }

  /**
   * Sign in an existing user
   */
  async signIn(email: string, password: string): Promise<UserCredential> {
    try {
      return await signInWithEmailAndPassword(auth, email, password)
    } catch (error: any) {
      throw this.handleAuthError(error)
    }
  }

  /**
   * Sign out the current user
   */
  async signOut(): Promise<void> {
    try {
      await signOut(auth)
    } catch (error: any) {
      throw this.handleAuthError(error)
    }
  }

  /**
   * Send password reset email
   */
  async resetPassword(email: string): Promise<void> {
    try {
      await sendPasswordResetEmail(auth, email)
    } catch (error: any) {
      throw this.handleAuthError(error)
    }
  }

  /**
   * Send email verification
   */
  async sendVerificationEmail(user: User): Promise<void> {
    try {
      await sendEmailVerification(user)
    } catch (error: any) {
      throw this.handleAuthError(error)
    }
  }

  /**
   * Get the currently signed-in user
   */
  getCurrentUser(): User | null {
    return auth.currentUser
  }

  /**
   * Get the Firebase ID token for the current user
   */
  async getIdToken(): Promise<string | null> {
    const user = this.getCurrentUser()
    if (!user) return null
    
    try {
      return await user.getIdToken()
    } catch (error) {
      console.error('Failed to get ID token:', error)
      return null
    }
  }

  /**
   * Handle Firebase Auth errors and return user-friendly messages
   */
  private handleAuthError(error: any): Error {
    let message = 'An authentication error occurred'
    
    switch (error.code) {
      case 'auth/email-already-in-use':
        message = 'This email is already registered'
        break
      case 'auth/invalid-email':
        message = 'Invalid email address'
        break
      case 'auth/operation-not-allowed':
        message = 'Email/password accounts are not enabled'
        break
      case 'auth/weak-password':
        message = 'Password is too weak. Use at least 6 characters'
        break
      case 'auth/user-disabled':
        message = 'This account has been disabled'
        break
      case 'auth/user-not-found':
      case 'auth/wrong-password':
        message = 'Invalid email or password'
        break
      case 'auth/invalid-credential':
        message = 'Invalid credentials. Please check your email and password'
        break
      case 'auth/too-many-requests':
        message = 'Too many failed attempts. Please try again later'
        break
      case 'auth/network-request-failed':
        message = 'Network error. Please check your connection'
        break
      default:
        message = error.message || 'Authentication failed'
    }
    
    return new Error(message)
  }
}

export const firebaseAuthService = new FirebaseAuth()

