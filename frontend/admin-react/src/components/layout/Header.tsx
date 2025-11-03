import { useAuth } from '../../contexts/AuthContext'

export const Header = () => {
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <div className="header">
      <div className="header-copy">
        <h1>RemoteLED Console</h1>
        <p>Real-time oversight for devices, products, and orders</p>
      </div>
      {isAuthenticated && user ? (
        <div className="header-user">
          <span className="header-user-email">{user.email}</span>
          <button className="btn btn-sm header-logout" onClick={logout}>
            Logout
          </button>
        </div>
      ) : null}
    </div>
  )
}

