import { APP_SHORT_NAME } from '../app/config'
import { Icon } from '../app/icons'
import type { NavItem, View } from '../app/navigation'

interface SidebarProps {
  items: NavItem[]
  activeView: View
  roleLabel: string
  userId: string
  collapsed: boolean
  mobileOpen: boolean
  loggingOut: boolean
  onNavigate: (view: View) => void
  onToggleCollapsed: () => void
  onCloseMobile: () => void
  onLogout: () => void
}

export function Sidebar({
  items,
  activeView,
  roleLabel,
  userId,
  collapsed,
  mobileOpen,
  loggingOut,
  onNavigate,
  onToggleCollapsed,
  onCloseMobile,
  onLogout,
}: SidebarProps) {
  return (
    <aside
      className={`sidebar${collapsed ? ' collapsed' : ''}${mobileOpen ? ' mobile-open' : ''}`}
      aria-label="Navegación principal"
    >
      <div className="sidebar-brand">
        <span className="brand-mark">
          <Icon name="dispositivos" size={20} />
        </span>
        <div className="sidebar-brand-copy">
          <strong>{APP_SHORT_NAME}</strong>
          <small>IoT · Control educativo</small>
        </div>
        <button
          type="button"
          className="sidebar-control collapse-control"
          aria-label={collapsed ? 'Expandir menú lateral' : 'Contraer menú lateral'}
          title={collapsed ? 'Expandir menú' : 'Contraer menú'}
          onClick={onToggleCollapsed}
        >
          <Icon name="flecha" size={16} />
        </button>
        <button
          type="button"
          className="sidebar-control close-control"
          aria-label="Cerrar menú lateral"
          onClick={onCloseMobile}
        >
          <Icon name="cerrar" size={18} />
        </button>
      </div>

      <nav className="nav-list" aria-label="Módulos de la plataforma">
        {items.map((item) => {
          const active = activeView === item.view
          return (
            <button
              key={item.view}
              type="button"
              className={`nav-button${active ? ' active' : ''}`}
              aria-current={active ? 'page' : undefined}
              title={item.label}
              onClick={() => onNavigate(item.view)}
            >
              <Icon name={item.icon} size={19} />
              <span className="nav-label">{item.label}</span>
              {active && <span className="nav-active-mark" aria-hidden="true" />}
            </button>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <span className="avatar" aria-hidden="true">
            {userId.charAt(0).toUpperCase()}
          </span>
          <div className="sidebar-user-copy">
            <strong title={userId}>{userId}</strong>
            <small>{roleLabel}</small>
          </div>
        </div>
        <button
          type="button"
          className="sidebar-logout"
          disabled={loggingOut}
          onClick={onLogout}
        >
          <Icon name="salir" size={18} />
          <span>{loggingOut ? 'Cerrando sesión…' : 'Cerrar sesión'}</span>
        </button>
      </div>
    </aside>
  )
}
