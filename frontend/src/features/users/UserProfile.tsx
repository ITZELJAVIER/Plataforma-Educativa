import { Icon } from '../../app/icons'
import { VIEW_META, roleLabel, type View } from '../../app/navigation'
import { PageHeader } from '../../components/PageHeader'
import { StatusBadge } from '../../components/StatusBadge'
import type { User } from '../../types/user'

interface UserProfileProps {
  user: User
  onNavigate: (view: View) => void
}

export function UserProfile({ user, onNavigate }: UserProfileProps) {
  return (
    <div className="stack">
      <PageHeader
        eyebrow={VIEW_META.perfil.eyebrow}
        title="Mi perfil"
        description="Datos de la cuenta validados por el servicio de autenticación."
        meta={<StatusBadge tone="success" dot>Sesión activa</StatusBadge>}
      />

      <section className="card" aria-labelledby="profile-data-title">
        <div className="section-heading">
          <div>
            <h3 id="profile-data-title">Datos de la cuenta</h3>
            <p className="hint">La API no expone nombre completo ni correo electrónico.</p>
          </div>
          <span className="section-icon" aria-hidden="true">
            <Icon name="perfil" size={19} />
          </span>
        </div>
        <dl className="detail-grid">
          <div>
            <dt>Identificador</dt>
            <dd className="mono">{user.id}</dd>
          </div>
          <div>
            <dt>Rol</dt>
            <dd>
              <StatusBadge tone="info">{roleLabel(user.role)}</StatusBadge>
            </dd>
          </div>
          <div>
            <dt>Estado de la cuenta</dt>
            <dd>
              <StatusBadge tone={user.active ? 'success' : 'warning'} dot>
                {user.active ? 'Activo' : 'Inactivo'}
              </StatusBadge>
            </dd>
          </div>
          <div>
            <dt>Correo electrónico</dt>
            <dd className="hint">Pendiente de integración</dd>
          </div>
          <div>
            <dt>Fecha de registro</dt>
            <dd className="hint">Pendiente de integración</dd>
          </div>
        </dl>
      </section>

      <section className="card" aria-labelledby="session-info-title">
        <div className="section-heading">
          <div>
            <h3 id="session-info-title">Información de sesión</h3>
            <p className="hint">Detalles seguros sin exponer credenciales ni tokens.</p>
          </div>
          <span className="section-icon" aria-hidden="true">
            <Icon name="estado" size={19} />
          </span>
        </div>
        <ul className="info-list">
          <li>
            <Icon name="check" size={16} />
            <span>Identidad verificada mediante authApi.me.</span>
          </li>
          <li>
            <Icon name="estado" size={16} />
            <span>
              El token de sesión se conserva en sessionStorage; su valor no se muestra.
            </span>
          </li>
          <li>
            <Icon name="configuracion" size={16} />
            <span>La preferencia de tema se guarda por separado en localStorage.</span>
          </li>
          <li>
            <Icon name="informacion" size={16} />
            <span>El cierre de sesión se realiza desde la barra lateral.</span>
          </li>
        </ul>
      </section>

      <section className="card" aria-labelledby="profile-links-title">
        <div className="section-heading">
          <div>
            <h3 id="profile-links-title">Enlaces útiles</h3>
            <p className="hint">Accesos relacionados con su cuenta.</p>
          </div>
        </div>
        <div className="quick-grid">
          <button
            type="button"
            className="quick-card"
            onClick={() => onNavigate('configuracion')}
          >
            <span className="icon-tile">
              <Icon name="configuracion" size={19} />
            </span>
            <span className="quick-copy">
              <strong>Configuración</strong>
              <small>Preferencias de tema e información general.</small>
            </span>
            <Icon name="flecha" size={16} className="quick-arrow" />
          </button>
          <button
            type="button"
            className="quick-card"
            onClick={() => onNavigate('monitoreo')}
          >
            <span className="icon-tile">
              <Icon name="monitoreo" size={19} />
            </span>
            <span className="quick-copy">
              <strong>Monitoreo</strong>
              <small>Capacidades previstas de supervisión IoT.</small>
            </span>
            <Icon name="flecha" size={16} className="quick-arrow" />
          </button>
        </div>
      </section>
    </div>
  )
}
