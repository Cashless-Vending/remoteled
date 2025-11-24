import type { ReactNode } from 'react'

type DashboardNavItem = {
  id: string
  label: string
  icon?: string
}

interface DashboardLayoutProps {
  title?: string
  subtitle?: string
  navItems: DashboardNavItem[]
  activeItem: string
  onSelect: (id: string) => void
  headerSlot?: ReactNode
  children: ReactNode
}

export const DashboardLayout = ({
  title,
  subtitle,
  navItems,
  activeItem,
  onSelect,
  headerSlot,
  children
}: DashboardLayoutProps) => {
  const safeNavItems = navItems || []
  
  return (
    <div className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">⚡️</div>
          <div>
            <h1>{title ?? 'RemoteLED Admin'}</h1>
            {subtitle ? <p>{subtitle}</p> : <p>Operations Console</p>}
          </div>
        </div>
        <nav className="sidebar-nav">
          {safeNavItems.map(({ id, label, icon }) => {
            const isActive = id === activeItem
            return (
              <button
                key={id}
                type="button"
                className={`nav-link${isActive ? ' is-active' : ''}`}
                onClick={() => onSelect(id)}
              >
                {icon ? <span className="nav-icon" aria-hidden="true">{icon}</span> : null}
                <span>{label}</span>
              </button>
            )
          })}
        </nav>
      </aside>
      <section className="dashboard-main">
        <header className="dashboard-header">
          {headerSlot}
        </header>
        <div className="dashboard-content">
          {children}
        </div>
      </section>
    </div>
  )
}


