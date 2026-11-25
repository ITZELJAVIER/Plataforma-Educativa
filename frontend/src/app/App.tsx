import { useCallback, useEffect, useState } from 'react'

import { ErrorState } from '../components/ErrorState'
import { Sidebar } from '../components/Sidebar'
import { ThemeToggle } from '../components/ThemeToggle'
import { Topbar } from '../components/Topbar'
import { LoginForm } from '../features/auth/LoginForm'
import { Dashboard } from '../features/dashboard/Dashboard'
import { DevicesView } from '../features/devices/DevicesView'
import { MonitoringView } from '../features/monitoring/MonitoringView'
import { PeripheralCatalog } from '../features/peripherals/PeripheralCatalog'
import { SettingsView } from '../features/settings/SettingsView'
import { UserAdmin } from '../features/users/UserAdmin'
import { UserProfile } from '../features/users/UserProfile'
import {
  ApiError,
  authApi,
  clearToken,
  errorMessage,
  readToken,
  saveToken,
} from '../services/api'
import type { User } from '../types/user'
import { APP_DESCRIPTION, APP_NAME } from './config'
import { Icon } from './icons'
import {
  VIEW_META,
  isViewAllowed,
  navItemsFor,
  roleLabel,
  type View,
} from './navigation'
import { useTheme } from './useTheme'

export default function App() {
  const [token, setToken] = useState<string | null>(() => readToken())
  const [user, setUser] = useState<User | null>(null)
  const [checkingSession, setCheckingSession] = useState(() => readToken() !== null)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<View>('inicio')
  const [loggingOut, setLoggingOut] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const themeController = useTheme()

  const applySession = useCallback((nextToken: string | null) => {
    if (nextToken) {
      saveToken(nextToken)
    } else {
      clearToken()
    }
    setToken(nextToken)
    setUser(null)
    setView('inicio')
    setMobileMenuOpen(false)
  }, [])

  useEffect(() => {
    if (!token) {
      setCheckingSession(false)
      return
    }

    let cancelled = false
    setCheckingSession(true)
    authApi
      .me(token)
      .then((current) => {
        if (!cancelled) {
          setUser(current)
        }
      })
      .catch(() => {
        if (!cancelled) {
          applySession(null)
          setError('La sesión no es válida. Inicie sesión de nuevo.')
        }
      })
      .finally(() => {
        if (!cancelled) {
          setCheckingSession(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [token, applySession])

  async function handleLogin(id: string, password: string) {
    setError(null)
    const response = await authApi.login(id, password)
    applySession(response.token)
  }

  async function handleLogout() {
    if (!token) return
    setError(null)
    setLoggingOut(true)
    try {
      await authApi.logout(token)
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) {
        applySession(null)
        return
      }
      setError(errorMessage(cause))
      return
    } finally {
      setLoggingOut(false)
    }
    applySession(null)
  }

  const esAdministrador = user?.role === 'administrador'
  const activeView: View = isViewAllowed(view, esAdministrador) ? view : 'inicio'
  const meta = VIEW_META[activeView]

  function navigate(nextView: View) {
    setView(nextView)
    setMobileMenuOpen(false)
  }

  if (!token || checkingSession || !user) {
    return (
      <div className="auth-layout">
        <section className="auth-brand" aria-labelledby="brand-title">
          <span className="brand-mark">
            <Icon name="dispositivos" size={26} />
          </span>
          <h1 id="brand-title">{APP_NAME}</h1>
          <p className="auth-subtitle">{APP_DESCRIPTION}</p>
          <ul className="brand-list">
            <li>
              <Icon name="inicio" size={18} />
              Panel principal con indicadores reales del catálogo y dispositivos
            </li>
            <li>
              <Icon name="catalogo" size={18} />
              Catálogo de periféricos dirigido por metadatos
            </li>
            <li>
              <Icon name="dispositivos" size={18} />
              Gestión de dispositivos, estados y eventos reales
            </li>
            <li>
              <Icon name="monitoreo" size={18} />
              Monitoreo IoT en preparación, sin datos simulados
            </li>
          </ul>
        </section>

        <div className="auth-panel">
          <div className="auth-panel-top">
            <span className="hint">Preferencia de tema</span>
            <ThemeToggle
              theme={themeController.theme}
              preference={themeController.preference}
              onChange={themeController.setPreference}
            />
          </div>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          {checkingSession ? (
            <div className="card auth-status">Verificando sesión…</div>
          ) : !token || !user ? (
            <LoginForm onLogin={(id, password) => handleLogin(id, password)} />
          ) : (
            <div className="card auth-status">No hay una sesión activa.</div>
          )}
        </div>
      </div>
    )
  }

  function contenido(activeToken: string, activeUser: User) {
    switch (activeView) {
      case 'inicio':
        return <Dashboard token={activeToken} user={activeUser} onNavigate={navigate} />
      case 'dispositivos':
        return (
          <DevicesView
            token={activeToken}
            esAdministrador={activeUser.role === 'administrador'}
          />
        )
      case 'catalogo':
        return (
          <PeripheralCatalog
            token={activeToken}
            esAdministrador={activeUser.role === 'administrador'}
          />
        )
      case 'usuarios':
        return activeUser.role === 'administrador' ? (
          <UserAdmin token={activeToken} />
        ) : null
      case 'perfil':
        return <UserProfile user={activeUser} onNavigate={navigate} />
      case 'configuracion':
        return (
          <SettingsView
            preference={themeController.preference}
            theme={themeController.theme}
            onPreferenceChange={themeController.setPreference}
          />
        )
      case 'monitoreo':
        return <MonitoringView />
    }
  }

  return (
    <div className={`layout${sidebarCollapsed ? ' sidebar-collapsed' : ''}`}>
      {mobileMenuOpen && (
        <button
          type="button"
          className="sidebar-overlay"
          aria-label="Cerrar menú lateral"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
      <Sidebar
        items={navItemsFor(esAdministrador)}
        activeView={activeView}
        roleLabel={roleLabel(user.role)}
        userId={user.id}
        collapsed={sidebarCollapsed}
        mobileOpen={mobileMenuOpen}
        loggingOut={loggingOut}
        onNavigate={navigate}
        onToggleCollapsed={() => setSidebarCollapsed((estado) => !estado)}
        onCloseMobile={() => setMobileMenuOpen(false)}
        onLogout={() => void handleLogout()}
      />

      <div className="workspace">
        <Topbar
          title={meta.title}
          description={meta.description}
          breadcrumb={meta.breadcrumb}
          userId={user.id}
          roleLabel={roleLabel(user.role)}
          theme={themeController.theme}
          themePreference={themeController.preference}
          loggingOut={loggingOut}
          onThemeChange={themeController.setPreference}
          onToggleMenu={() => setMobileMenuOpen((estado) => !estado)}
          onLogout={() => void handleLogout()}
        />

        <main className="content">
          {error && (
            <ErrorState
              compact
              message={error}
              title="Aviso de la sesión"
            />
          )}
          {contenido(token, user)}
        </main>
      </div>
    </div>
  )
}
