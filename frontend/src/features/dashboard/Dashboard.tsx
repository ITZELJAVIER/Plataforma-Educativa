import { useCallback, useEffect, useMemo, useState } from 'react'

import { Icon } from '../../app/icons'
import { VIEW_META, roleLabel, type IconName, type View } from '../../app/navigation'
import { catalogApi, devicesApi, errorMessage } from '../../services/api'
import type { Device } from '../../types/device'
import type { PeripheralType } from '../../types/peripheral'
import type { User } from '../../types/user'
import { EmptyState } from '../../components/EmptyState'
import { ErrorState } from '../../components/ErrorState'
import { LoadingState } from '../../components/LoadingState'
import { PageHeader } from '../../components/PageHeader'
import { StatCard } from '../../components/StatCard'
import { StatusBadge } from '../../components/StatusBadge'
import {
  claseEstado,
  etiquetaEstado,
  resumirDispositivos,
} from '../devices/presentation'
import { resumirCatalogo } from './summary'

interface DashboardProps {
  token: string
  user: User
  onNavigate: (view: View) => void
}

interface QuickAccess {
  view: View
  label: string
  description: string
  icon: IconName
  adminOnly?: boolean
}

const ACCESOS: readonly QuickAccess[] = [
  {
    view: 'dispositivos',
    label: 'Dispositivos',
    description: 'Consultar registros, estados y eventos reales.',
    icon: 'dispositivos',
  },
  {
    view: 'catalogo',
    label: 'Catálogo de periféricos',
    description: 'Revisar tipos base, metadatos y validaciones.',
    icon: 'catalogo',
  },
  {
    view: 'monitoreo',
    label: 'Monitoreo',
    description: 'Conocer las capacidades previstas de supervisión.',
    icon: 'monitoreo',
  },
  {
    view: 'configuracion',
    label: 'Configuración',
    description: 'Ajustar el tema y consultar información general.',
    icon: 'configuracion',
  },
  {
    view: 'usuarios',
    label: 'Administración de usuarios',
    description: 'Gestionar cuentas, roles y estados de acceso.',
    icon: 'usuarios',
    adminOnly: true,
  },
  {
    view: 'perfil',
    label: 'Mi perfil',
    description: 'Consultar los datos de la cuenta autenticada.',
    icon: 'perfil',
  },
]

export function Dashboard({ token, user, onNavigate }: DashboardProps) {
  const [catalogo, setCatalogo] = useState<PeripheralType[] | null>(null)
  const [dispositivos, setDispositivos] = useState<Device[] | null>(null)
  const [cargandoCatalogo, setCargandoCatalogo] = useState(true)
  const [cargandoDispositivos, setCargandoDispositivos] = useState(true)
  const [errorCatalogo, setErrorCatalogo] = useState<string | null>(null)
  const [errorDispositivos, setErrorDispositivos] = useState<string | null>(null)

  const cargarCatalogo = useCallback(async () => {
    setCargandoCatalogo(true)
    setErrorCatalogo(null)
    try {
      setCatalogo(await catalogApi.list(token))
    } catch (cause) {
      setCatalogo(null)
      setErrorCatalogo(errorMessage(cause))
    } finally {
      setCargandoCatalogo(false)
    }
  }, [token])

  const cargarDispositivos = useCallback(async () => {
    setCargandoDispositivos(true)
    setErrorDispositivos(null)
    try {
      setDispositivos(await devicesApi.list(token))
    } catch (cause) {
      setDispositivos(null)
      setErrorDispositivos(errorMessage(cause))
    } finally {
      setCargandoDispositivos(false)
    }
  }, [token])

  useEffect(() => {
    void cargarCatalogo()
    void cargarDispositivos()
  }, [cargarCatalogo, cargarDispositivos])

  const fecha = useMemo(
    () =>
      new Intl.DateTimeFormat('es-ES', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      }).format(new Date()),
    [],
  )

  const resumenPerifericos = resumirCatalogo(catalogo ?? [])
  const resumenDevices = resumirDispositivos(dispositivos ?? [])
  const valorCatalogo = (numero: number) => (catalogo === null ? '—' : String(numero))
  const valorDevices = (numero: number) => (dispositivos === null ? '—' : String(numero))
  const actualizando = cargandoCatalogo || cargandoDispositivos

  return (
    <div className="stack">
      <section className="welcome-panel">
        <PageHeader
          eyebrow={VIEW_META.inicio.eyebrow}
          title={`Bienvenido, ${user.id}`}
          description="Consulte el estado real del catálogo y de los dispositivos registrados en la plataforma."
          meta={
            <>
              <StatusBadge tone="info" dot>
                {roleLabel(user.role)}
              </StatusBadge>
              <span className="welcome-date">
                <Icon name="calendario" size={16} />
                {fecha}
              </span>
              <span className="hint">La API validó su sesión correctamente.</span>
            </>
          }
        />
        <span className="welcome-mark" aria-hidden="true">
          <Icon name="inicio" size={34} />
        </span>
      </section>

      <section className="card" aria-labelledby="dashboard-indicators">
        <div className="section-heading">
          <div>
            <h3 id="dashboard-indicators">Resumen general</h3>
            <p className="hint">
              Indicadores calculados únicamente con respuestas de catalogApi y
              devicesApi.
            </p>
          </div>
          <button
            type="button"
            className="button ghost"
            disabled={actualizando}
            onClick={() => {
              void cargarCatalogo()
              void cargarDispositivos()
            }}
          >
            <Icon name="actualizar" size={16} />
            {actualizando ? 'Actualizando…' : 'Actualizar'}
          </button>
        </div>

        {errorCatalogo && (
          <ErrorState
            compact
            title="No se pudo cargar el catálogo"
            message={errorCatalogo}
            onRetry={() => void cargarCatalogo()}
            retrying={cargandoCatalogo}
          />
        )}
        {errorDispositivos && (
          <ErrorState
            compact
            title="No se pudieron cargar los dispositivos"
            message={errorDispositivos}
            onRetry={() => void cargarDispositivos()}
            retrying={cargandoDispositivos}
          />
        )}

        <div className="stat-grid">
          <StatCard
            label="Tipos de periféricos"
            value={valorCatalogo(resumenPerifericos.total)}
            hint={catalogo === null ? 'Sin datos disponibles' : 'catalogApi'}
            icon="catalogo"
          />
          <StatCard
            label="Tipos con canales"
            value={valorCatalogo(resumenPerifericos.conCanales)}
            hint={catalogo === null ? 'Sin datos disponibles' : 'Metadatos reales'}
            icon="canales"
          />
          <StatCard
            label="Tipos con unidad"
            value={valorCatalogo(resumenPerifericos.conUnidad)}
            hint={catalogo === null ? 'Sin datos disponibles' : 'Metadatos reales'}
            icon="medida"
          />
          <StatCard
            label="Tipos con rango"
            value={valorCatalogo(resumenPerifericos.conRango)}
            hint={catalogo === null ? 'Sin datos disponibles' : 'Metadatos reales'}
            icon="rango"
          />
          <StatCard
            label="Dispositivos registrados"
            value={valorDevices(resumenDevices.total)}
            hint={dispositivos === null ? 'Sin datos disponibles' : 'devicesApi'}
            icon="dispositivos"
            tone="success"
          />
          <StatCard
            label="Dispositivos habilitados"
            value={valorDevices(resumenDevices.habilitados)}
            hint={dispositivos === null ? 'Sin datos disponibles' : 'Estado lógico real'}
            icon="estado"
            tone="success"
          />
          <StatCard
            label="Dispositivos conectados"
            value={valorDevices(resumenDevices.conectados)}
            hint={dispositivos === null ? 'Sin datos disponibles' : 'Estado informado por la API'}
            icon="monitoreo"
            tone="success"
          />
        </div>
      </section>

      <div className="dashboard-columns">
        <section className="card" aria-labelledby="dashboard-devices">
          <div className="section-heading">
            <div>
              <h3 id="dashboard-devices">Estado de dispositivos</h3>
              <p className="hint">Solo se muestran estados devueltos por la API.</p>
            </div>
            <button
              type="button"
              className="button link"
              onClick={() => onNavigate('dispositivos')}
            >
              Ver dispositivos
              <Icon name="flecha" size={15} />
            </button>
          </div>

          {cargandoDispositivos ? (
            <LoadingState label="Consultando dispositivos…" compact />
          ) : dispositivos === null ? (
            <p className="hint">La información no está disponible en este momento.</p>
          ) : dispositivos.length === 0 ? (
            <EmptyState
              compact
              icon="dispositivos"
              title="Sin dispositivos registrados"
              description="Cuando se registren instancias, su estado real aparecerá aquí."
            />
          ) : (
            <>
              <div className="status-summary">
                <StatusBadge tone="success" dot>
                  {resumenDevices.conectados} conectados
                </StatusBadge>
                <StatusBadge tone="warning" dot>
                  {resumenDevices.desconectados} desconectados
                </StatusBadge>
                <StatusBadge tone="neutral" dot>
                  {resumenDevices.desconocidos} desconocidos
                </StatusBadge>
              </div>
              <ul className="mini-device-list">
                {dispositivos.slice(0, 5).map((device) => (
                  <li key={device.id}>
                    <span className="mini-device-name">
                      <strong>{device.nombre}</strong>
                      <small>{device.id}</small>
                    </span>
                    <span className={`badge ${claseEstado(device.estado)}`}>
                      {etiquetaEstado(device.estado)}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>

        <section className="card" aria-labelledby="dashboard-activity">
          <div className="section-heading">
            <div>
              <h3 id="dashboard-activity">Actividad reciente</h3>
              <p className="hint">Integración pendiente.</p>
            </div>
            <span className="section-icon" aria-hidden="true">
              <Icon name="eventos" size={18} />
            </span>
          </div>
          <EmptyState
            compact
            icon="informacion"
            title="Pendiente de integración"
            description="La API actual no expone un endpoint de actividad reciente. No se muestran eventos simulados."
          />
        </section>
      </div>

      <section className="card" aria-labelledby="dashboard-shortcuts">
        <div className="section-heading">
          <div>
            <h3 id="dashboard-shortcuts">Accesos rápidos</h3>
            <p className="hint">Entradas directas a los módulos disponibles para su rol.</p>
          </div>
        </div>
        <div className="quick-grid">
          {ACCESOS.filter((acceso) => !acceso.adminOnly || user.role === 'administrador').map(
            (acceso) => (
              <button
                key={acceso.view}
                type="button"
                className="quick-card"
                onClick={() => onNavigate(acceso.view)}
              >
                <span className="icon-tile">
                  <Icon name={acceso.icon} size={19} />
                </span>
                <span className="quick-copy">
                  <strong>{acceso.label}</strong>
                  <small>{acceso.description}</small>
                </span>
                <Icon name="flecha" size={16} className="quick-arrow" />
              </button>
            ),
          )}
        </div>
      </section>
    </div>
  )
}
