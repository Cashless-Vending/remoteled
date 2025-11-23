import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { LoginForm } from '../components/forms'

export const Login = () => {
  const [showLoginForm, setShowLoginForm] = useState(false)
  const { login, signup } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (email: string, password: string) => {
    await login(email, password)
    navigate('/dashboard')
  }

  const handleSignup = async (email: string, password: string) => {
    await signup(email, password)
    navigate('/dashboard')
  }

  return (
    <>
      <div className="header">
        <div style={{ textAlign: 'center' }}>
          <h1>🚀 RemoteLED Admin Console</h1>
          <p>Real-time dashboard for device and order management</p>
          <button 
            className="btn btn-primary" 
            onClick={() => setShowLoginForm(true)}
            style={{ marginTop: '2rem' }}
          >
            Login to Continue
          </button>
        </div>
      </div>

      <LoginForm 
        isOpen={showLoginForm}
        onClose={() => setShowLoginForm(false)}
        onSubmit={handleLogin}
        onSignup={handleSignup}
      />
    </>
  )
}

