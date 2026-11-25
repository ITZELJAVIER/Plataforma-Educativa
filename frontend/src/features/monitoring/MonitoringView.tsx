import { Icon } from '../../app/icons'
import { VIEW_META, type IconName } from '../../app/navigation'
import { EmptyState } from '../../components/EmptyState'
import { PageHeader } from '../../components/PageHeader'
import { StatusBadge } from '../../components/StatusBadge'

interface Capacidad {
  title: string
  description: string
  icon: IconName
}

const CAPACIDADES: readonly Capacidad[] = [
  {
    title: 'Monitoreo de dispositivos',
    description: 'Supervisión visual del estado informado por cada dispositivo.',
    icon: 'dispositivos',
  },
  {
    title: 'Variables de sensores',
    description: 'Presentación de magnitudes y unidades declaradas en el catálogo.',
    icon: 'medida',
  },
  {
    title: 'Gráficas temporales',
    description: 'Visualización de series históricas cuando exista una fuente real.',
    icon: 'monitoreo',
  },
  {
    title: 'Historial de mediciones',
    description: 'Consulta de mediciones persistidas con trazabilidad.',
    icon: 'eventos',
  },
  {
    title: 'Estado de comunicación',
    description: 'Indicadores de conectividad y transporte de mensajes.',
    icon: 'estado',
  },
  {
    title: 'Supervisión de periféricos',
    description: 'Seguimiento de canales y adaptadores declarados.',
    icon: 'canales',
  },
]

export function MonitoringView() {
  return (
    <div className="stack">
      <PageHeader
        eyebrow={VIEW_META.monitoreo.eyebrow}
        title="Monitoreo IoT"
        description="Espacio reservado para la futura supervisión operativa de dispositivos y periféricos."
        meta={
          <StatusBadge tone="warning" dot>
            Pendiente de integración
          </StatusBadge>
        }
      />

      <section className="card integration-banner" aria-labelledby="monitoring-status-title">
        <div className="integration-icon" aria-hidden="true">
          <Icon name="monitoreo" size={26} />
        </div>
        <div>
          <h3 id="monitoring-status-title">Módulo en preparación</h3>
          <p>
            La interfaz está preparada para recibir telemetría real. La API actual no
            expone mediciones, WebSocket, MQTT ni indicadores de comunicación; por
            ese motivo no se muestran gráficas ni valores simulados.
          </p>
        </div>
      </section>

      <section className="card" aria-labelledby="monitoring-capabilities-title">
        <div className="section-heading">
          <div>
            <h3 id="monitoring-capabilities-title">Capacidades previstas</h3>
            <p className="hint">
              Descripción de las áreas que se integrarán cuando existan contratos reales.
            </p>
          </div>
        </div>
        <div className="capability-grid">
          {CAPACIDADES.map((capacidad) => (
            <article className="capability-card" key={capacidad.title}>
              <span className="capability-icon" aria-hidden="true">
                <Icon name={capacidad.icon} size={19} />
              </span>
              <div>
                <h4>{capacidad.title}</h4>
                <p>{capacidad.description}</p>
              </div>
              <StatusBadge tone="neutral">Sin integrar</StatusBadge>
            </article>
          ))}
        </div>
      </section>

      <section className="card" aria-labelledby="monitoring-placeholder-title">
        <div className="section-heading">
          <div>
            <h3 id="monitoring-placeholder-title">Panel de mediciones</h3>
            <p className="hint">No se genera información ficticia.</p>
          </div>
        </div>
        <EmptyState
          icon="informacion"
          title="Sin fuente de datos disponible"
          description="Cuando la plataforma incorpore endpoints de telemetría e historial, este panel mostrará únicamente datos reales."
        />
      </section>
    </div>
  )
}
