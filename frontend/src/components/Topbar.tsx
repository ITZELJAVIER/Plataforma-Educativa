import { APP_NAME } from '../app/config'
import { Icon } from '../app/icons'
import type { ThemePreference, ResolvedTheme } from '../app/theme'
import { ThemeToggle } from './ThemeToggle'

interface TopbarProps {
  title: string
  description: string
  breadcrumb: string
  userId: string
  roleLabel: string
  theme: ResolvedTheme
  themePreference: ThemePreference
  loggingOut: boolean
  onThemeChange: (preference: ThemePreference) => void
  onToggleMenu: () => void
  onLogout: () => void
}

export function Topbar({
  title,
  description,
  breadcrumb,
  userId,
  roleLabel,
  theme,
  themePreference,
  loggingOut,
  onThemeChange,
  onToggleMenu,
  onLogout,
}: TopbarProps) {
  return (
    <header className="topbar">
      <div className="topbar-leading">
        <button
          type="button"
          className="icon-button menu-button"
          aria-label="Abrir menú de navegación"
          onClick={onToggleMenu}
        >
          <Icon name="menu" size={20} />
        </button>
        <div className="topbar-heading">
          <nav className="breadcrumb" aria-label="Ruta de navegación">
            <span>{APP_NAME}</span>
            <Icon name="flecha" size={12} />
            <strong>{breadcrumb}</strong>
          </nav>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
      </div>

      <div className="topbar-actions">
        <span className="session-indicator" title="La sesión fue validada por la API">
          <span className="session-dot" aria-hidden="true" />
          Sesión activa
        </span>
        <span className="notification-slot" title="Las notificaciones no están integradas">
          <Icon name="informacion" size={15} />
          Notificaciones sin integrar
        </span>
        <ThemeToggle
          theme={theme}
          preference={themePreference}
          onChange={onThemeChange}
        />
        <div className="user-chip">
          <span className="avatar" aria-hidden="true">
            {userId.charAt(0).toUpperCase()}
          </span>
          <span className="user-meta">
            <strong>{userId}</strong>
            <small>{roleLabel}</small>
          </span>
        </div>
        <button
          type="button"
          className="icon-button logout-button"
          aria-label="Cerrar sesión"
          title="Cerrar sesión"
          disabled={loggingOut}
          onClick={onLogout}
        >
          <Icon name="salir" size={18} />
        </button>
      </div>
    </header>
  )
}
