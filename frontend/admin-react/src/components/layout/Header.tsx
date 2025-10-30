import { useAuth } from '../../contexts/AuthContext'

export const Header = () => {
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <div className="header">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>🚀 RemoteLED Admin Console</h1>
          <p>Real-time dashboard for device and order management</p>
        </div>
        <div>
          {isAuthenticated && user ? (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                👤 {user.email}
              </div>
              <button 
                className="btn btn-sm" 
                onClick={logout} 
                style={{ background: 'rgba(255,255,255,0.2)' }}
              >
                Logout
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}

