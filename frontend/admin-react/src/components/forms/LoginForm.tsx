import { useState, FormEvent } from 'react'
import { Modal } from '../common/Modal'
import { DEFAULT_CREDENTIALS } from '../../config/constants'

interface LoginFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (email: string, password: string) => Promise<void>
  onSignup?: (email: string, password: string) => Promise<void>
}

export const LoginForm = ({ isOpen, onClose, onSubmit, onSignup }: LoginFormProps) => {
  const [email, setEmail] = useState(DEFAULT_CREDENTIALS.email)
  const [password, setPassword] = useState(DEFAULT_CREDENTIALS.password)
  const [loading, setLoading] = useState(false)
  const [isSignupMode, setIsSignupMode] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (isSignupMode && onSignup) {
        await onSignup(email, password)
      } else {
        await onSubmit(email, password)
      }
      onClose()
    } catch (error: any) {
      alert(`${isSignupMode ? 'Signup' : 'Login'} failed:\n\n${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const toggleMode = () => {
    setIsSignupMode(!isSignupMode)
    setEmail('')
    setPassword('')
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isSignupMode ? 'Create Account' : 'Login'}>
      <form onSubmit={handleSubmit} style={{ padding: '1.5rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Email
          </label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your-email@example.com"
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Password
          </label>
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={isSignupMode ? 'At least 6 characters' : 'Your password'}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>
        
        {!isSignupMode && (
          <div style={{ fontSize: '0.875rem', color: '#718096', marginBottom: '1rem' }}>
            Default: {DEFAULT_CREDENTIALS.email} / {DEFAULT_CREDENTIALS.password}
          </div>
        )}

        {isSignupMode && (
          <div style={{ 
            fontSize: '0.875rem', 
            color: '#718096', 
            marginBottom: '1rem',
            padding: '0.75rem',
            background: '#f7fafc',
            borderRadius: '4px',
            border: '1px solid #e2e8f0'
          }}>
            <strong>Note:</strong> Your account will be created with Firebase Authentication and automatically granted admin access.
          </div>
        )}

        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'space-between', alignItems: 'center' }}>
          <button 
            type="button" 
            onClick={toggleMode}
            style={{
              background: 'none',
              border: 'none',
              color: '#4299e1',
              fontSize: '0.875rem',
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
            disabled={loading}
          >
            {isSignupMode ? '← Back to Login' : 'Create Account →'}
          </button>
          
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button type="button" className="btn" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (isSignupMode ? 'Creating...' : 'Logging in...') : (isSignupMode ? 'Create Account' : 'Login')}
            </button>
          </div>
        </div>
      </form>
    </Modal>
  )
}
