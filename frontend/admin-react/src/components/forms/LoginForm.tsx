import { useState, FormEvent } from 'react'
import { Modal } from '../common/Modal'
import { DEFAULT_CREDENTIALS } from '../../config/constants'

interface LoginFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (email: string, password: string) => Promise<void>
}

export const LoginForm = ({ isOpen, onClose, onSubmit }: LoginFormProps) => {
  const [email, setEmail] = useState(DEFAULT_CREDENTIALS.email)
  const [password, setPassword] = useState(DEFAULT_CREDENTIALS.password)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onSubmit(email, password)
      onClose()
    } catch (error: any) {
      alert(`Login failed:\n\n${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Login">
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
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}
          />
        </div>
        <div style={{ fontSize: '0.875rem', color: '#718096', marginBottom: '1rem' }}>
          Default: {DEFAULT_CREDENTIALS.email} / {DEFAULT_CREDENTIALS.password}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
          <button type="button" className="btn" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

