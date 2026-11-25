import { APP_DESCRIPTION, APP_NAME, APP_VERSION } from '../../app/config'
import { Icon } from '../../app/icons'
import { VIEW_META } from '../../app/navigation'
import {
  themePreferenceLabel,
  type ResolvedTheme,
  type ThemePreference,
} from '../../app/theme'
import { PageHeader } from '../../components/PageHeader'
import { StatusBadge } from '../../components/StatusBadge'
import { ThemeToggle } from '../../components/ThemeToggle'

interface SettingsViewProps {
  preference: ThemePreference
  theme: ResolvedTheme
  onPreferenceChange: (preference: ThemePreference) => void
}

export function SettingsView({
  preference,
  theme,
  onPreferenceChange,
}: SettingsViewProps) {
  return (
    <div className="stack">
      <PageHeader
        eyebrow={VIEW_META.configuracion.eyebrow}
        title="Preferencias de interfaz"
        description="Ajuste la apariencia de la plataforma y consulte información general."
        meta={<StatusBadge tone="info">Preferencias locales</StatusBadge>}
      />

      <section className="card" aria-labelledby="settings-theme-title">
        <div className="section-heading">
          <div>
            <h3 id="settings-theme-title">Tema</h3>
            <p className="hint">
              La preferencia se guarda en localStorage y no afecta la sesión.
            </p>
          </div>
          <StatusBadge tone={theme === 'oscuro' ? 'info' : 'neutral'}>
            Tema aplicado: {theme === 'oscuro' ? 'Oscuro' : 'Claro'}
          </StatusBadge>
        </div>

        <div className="theme-settings">
          <div>
            <h4>Selección de tema</h4>
            <p className="hint">
              Si elige “Según el sistema”, la interfaz seguirá la preferencia del
              sistema operativo mientras no se guarde otra opción.
            </p>
          </div>
          <ThemeToggle
            theme={theme}
            preference={preference}
            onChange={onPreferenceChange}
            variant="full"
          />
        </div>

        <dl className="detail-grid compact-details">
          <div>
            <dt>Preferencia guardada</dt>
            <dd>{themePreferenceLabel(preference)}</dd>
          </div>
          <div>
            <dt>Mecanismo de persistencia</dt>
            <dd className="mono">localStorage</dd>
          </div>
        </dl>
      </section>

      <section className="card" aria-labelledby="settings-app-title">
        <div className="section-heading">
          <div>
            <h3 id="settings-app-title">Información general</h3>
            <p className="hint">Datos de la aplicación desplegada.</p>
          </div>
          <span className="section-icon" aria-hidden="true">
            <Icon name="informacion" size={19} />
          </span>
        </div>
        <dl className="detail-grid">
          <div>
            <dt>Aplicación</dt>
            <dd>{APP_NAME}</dd>
          </div>
          <div>
            <dt>Versión del frontend</dt>
            <dd className="mono">{APP_VERSION}</dd>
          </div>
          <div>
            <dt>Descripción</dt>
            <dd>{APP_DESCRIPTION}</dd>
          </div>
          <div>
            <dt>Arquitectura</dt>
            <dd>React, TypeScript y Vite con servicios REST existentes.</dd>
          </div>
          <div>
            <dt>Autenticación</dt>
            <dd>Token de sesión en sessionStorage, validado con la API.</dd>
          </div>
          <div>
            <dt>Configuración de infraestructura</dt>
            <dd className="hint">
              No disponible: la API no expone ajustes de broker, tópicos ni transporte.
            </dd>
          </div>
        </dl>
      </section>

      <section className="card" aria-labelledby="settings-privacy-title">
        <div className="section-heading">
          <div>
            <h3 id="settings-privacy-title">Sesión y privacidad</h3>
            <p className="hint">Mecanismos conservados sin modificaciones.</p>
          </div>
        </div>
        <ul className="info-list">
          <li>
            <Icon name="estado" size={16} />
            <span>La sesión se mantiene en sessionStorage y se valida al cargar.</span>
          </li>
          <li>
            <Icon name="configuracion" size={16} />
            <span>El tema se almacena por separado en localStorage.</span>
          </li>
          <li>
            <Icon name="salir" size={16} />
            <span>El cierre de sesión conserva el flujo original de autenticación.</span>
          </li>
        </ul>
      </section>
    </div>
  )
}
