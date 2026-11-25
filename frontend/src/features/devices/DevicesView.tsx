import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'

import { Icon } from '../../app/icons'
import { VIEW_META, type View } from '../../app/navigation'
import { devicesApi, errorMessage } from '../../services/api'
import type { Device, DeviceInput, DeviceState, DeviceStateEvent } from '../../types/device'
import { ConfirmDialog } from '../../components/ConfirmDialog'
import { DataTable, type DataTableColumn } from '../../components/DataTable'
import { EmptyState } from '../../components/EmptyState'
import { ErrorState } from '../../components/ErrorState'
import { FormField } from '../../components/FormField'
import { LoadingState } from '../../components/LoadingState'
import { PageHeader } from '../../components/PageHeader'
import { StatusBadge } from '../../components/StatusBadge'
import { claseEstado, etiquetaEstado, resumirDispositivos } from './presentation'

interface DevicesViewProps {
  token: string
  esAdministrador: boolean
  compact?: boolean
  onNavigate?: (view: View) => void
}

interface FormState {
  id: string
  nombre: string
  tipo: string
  perfil_hardware: string
  ubicacion: string
  adaptador: string
}

type EstadoFiltro = 'todos' | DeviceState
type HabilitadoFiltro = 'todos' | 'habilitados' | 'desactivados'

const FORMULARIO_VACIO: FormState = {
  id: '',
  nombre: '',
  tipo: '',
  perfil_hardware: '',
  ubicacion: '',
  adaptador: '',
}

function datosFormulario(estado: FormState): Omit<DeviceInput, 'id'> & { id?: string } {
  return {
    id: estado.id.trim(),
    nombre: estado.nombre.trim(),
    tipo: estado.tipo.trim(),
    perfil_hardware: estado.perfil_hardware.trim(),
    ubicacion: estado.ubicacion.trim() || null,
    adaptador: estado.adaptador.trim() || null,
  }
}

function validarRegistro(estado: FormState): string | null {
  const datos = datosFormulario(estado)
  if (
    !datos.id ||
    !datos.nombre ||
    !datos.tipo ||
    !datos.perfil_hardware
  ) {
    return 'Complete el identificador, nombre, tipo y perfil de hardware.'
  }
  if (/\s/.test(datos.id)) {
    return 'El identificador no debe contener espacios en blanco.'
  }
  return null
}

function validarConfiguracion(estado: FormState): string | null {
  if (!estado.nombre.trim() || !estado.tipo.trim() || !estado.perfil_hardware.trim()) {
    return 'Nombre, tipo y perfil de hardware son obligatorios.'
  }
  return null
}

function tonoEstado(estado: DeviceState): 'success' | 'warning' | 'neutral' {
  if (estado === 'conectado') return 'success'
  if (estado === 'desconectado') return 'warning'
  return 'neutral'
}

export function DevicesView({
  token,
  esAdministrador,
  compact = false,
  onNavigate,
}: DevicesViewProps) {
  const [dispositivos, setDispositivos] = useState<Device[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [accionError, setAccionError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const [formulario, setFormulario] = useState<FormState>(FORMULARIO_VACIO)
  const [formError, setFormError] = useState<string | null>(null)

  const [termino, setTermino] = useState('')
  const [filtroEstado, setFiltroEstado] = useState<EstadoFiltro>('todos')
  const [filtroHabilitado, setFiltroHabilitado] =
    useState<HabilitadoFiltro>('todos')

  const [detalleId, setDetalleId] = useState<string | null>(null)
  const [detalle, setDetalle] = useState<Device | null>(null)
  const [cargandoDetalle, setCargandoDetalle] = useState(false)
  const [editando, setEditando] = useState(false)
  const [edicion, setEdicion] = useState<FormState>(FORMULARIO_VACIO)
  const [edicionError, setEdicionError] = useState<string | null>(null)

  const [eventos, setEventos] = useState<DeviceStateEvent[] | null>(null)
  const [cargandoEventos, setCargandoEventos] = useState(false)
  const [eventosVisibles, setEventosVisibles] = useState(false)

  const [pendienteDesactivar, setPendienteDesactivar] = useState<Device | null>(null)

  const cargar = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setDispositivos(await devicesApi.list(token))
    } catch (cause) {
      setDispositivos(null)
      setError(errorMessage(cause))
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    void cargar()
  }, [cargar])

  const cargarDetalle = useCallback(
    async (id: string) => {
      setCargandoDetalle(true)
      setAccionError(null)
      try {
        setDetalle(await devicesApi.get(token, id))
      } catch (cause) {
        setDetalle(null)
        setAccionError(errorMessage(cause))
      } finally {
        setCargandoDetalle(false)
      }
    },
    [token],
  )

  const resumen = resumirDispositivos(dispositivos ?? [])

  const filtrados = useMemo(() => {
    const texto = termino.trim().toLocaleLowerCase('es')
    return (dispositivos ?? []).filter((device) => {
      const coincideTexto =
        !texto ||
        device.id.toLocaleLowerCase('es').includes(texto) ||
        device.nombre.toLocaleLowerCase('es').includes(texto)
      const coincideEstado =
        filtroEstado === 'todos' || device.estado === filtroEstado
      const coincideHabilitacion =
        filtroHabilitado === 'todos' ||
        (filtroHabilitado === 'habilitados' && device.habilitado) ||
        (filtroHabilitado === 'desactivados' && !device.habilitado)
      return coincideTexto && coincideEstado && coincideHabilitacion
    })
  }, [dispositivos, termino, filtroEstado, filtroHabilitado])

  async function ejecutar(accion: () => Promise<unknown>, mensaje: string) {
    setBusy(true)
    setAccionError(null)
    setNotice(null)
    try {
      await accion()
      setNotice(mensaje)
      await cargar()
      return true
    } catch (cause) {
      setAccionError(errorMessage(cause))
      return false
    } finally {
      setBusy(false)
    }
  }

  function abrirDetalle(device: Device) {
    setDetalleId(device.id)
    setDetalle(null)
    setEventos(null)
    setEventosVisibles(false)
    setEditando(false)
    setEdicionError(null)
    void cargarDetalle(device.id)
  }

  function cerrarDetalle() {
    setDetalleId(null)
    setDetalle(null)
    setEventos(null)
    setEventosVisibles(false)
    setEditando(false)
  }

  function iniciarEdicion(device: Device) {
    setEditando(true)
    setEdicionError(null)
    setEdicion({
      id: device.id,
      nombre: device.nombre,
      tipo: device.tipo,
      perfil_hardware: device.perfil_hardware,
      ubicacion: device.ubicacion ?? '',
      adaptador: device.adaptador,
    })
  }

  async function handleCrear(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const validacion = validarRegistro(formulario)
    if (validacion) {
      setFormError(validacion)
      return
    }
    const datos = datosFormulario(formulario)
    const correcto = await ejecutar(
      () => devicesApi.create(token, datos as DeviceInput),
      'Dispositivo registrado correctamente.',
    )
    if (correcto) {
      setFormulario(FORMULARIO_VACIO)
      setFormError(null)
    }
  }

  async function handleActualizar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!detalle) return
    const validacion = validarConfiguracion(edicion)
    if (validacion) {
      setEdicionError(validacion)
      return
    }
    const correcto = await ejecutar(
      () =>
        devicesApi.update(token, detalle.id, {
          nombre: edicion.nombre.trim(),
          tipo: edicion.tipo.trim(),
          perfil_hardware: edicion.perfil_hardware.trim(),
          ubicacion: edicion.ubicacion.trim() || null,
          adaptador: edicion.adaptador.trim() || null,
        }),
      'Configuración actualizada correctamente.',
    )
    if (correcto) {
      setEdicionError(null)
      setEditando(false)
      void cargarDetalle(detalle.id)
    }
  }

  async function confirmarDesactivacion() {
    if (!pendienteDesactivar) return
    const dispositivo = pendienteDesactivar
    const correcto = await ejecutar(
      () => devicesApi.deactivate(token, dispositivo.id),
      'Dispositivo desactivado correctamente.',
    )
    if (correcto) {
      setPendienteDesactivar(null)
      if (detalleId === dispositivo.id) void cargarDetalle(dispositivo.id)
    }
  }

  async function handleEventos() {
    if (!detalleId) return
    if (eventosVisibles) {
      setEventosVisibles(false)
      return
    }
    setCargandoEventos(true)
    setAccionError(null)
    try {
      setEventos(await devicesApi.events(token, detalleId))
      setEventosVisibles(true)
    } catch (cause) {
      setAccionError(errorMessage(cause))
    } finally {
      setCargandoEventos(false)
    }
  }

  if (compact) {
    return (
      <section className="card" aria-labelledby="devices-compact-title">
        <div className="section-heading">
          <div>
            <h3 id="devices-compact-title">Dispositivos</h3>
            <p className="hint">Estado real del registro.</p>
          </div>
          <StatusBadge tone="info">{resumen.total} registrados</StatusBadge>
        </div>
        {error ? (
          <ErrorState compact message={error} onRetry={() => void cargar()} />
        ) : loading ? (
          <LoadingState compact label="Consultando dispositivos…" />
        ) : dispositivos === null ? (
          <p className="hint">Información no disponible.</p>
        ) : dispositivos.length === 0 ? (
          <EmptyState
            compact
            icon="dispositivos"
            title="Sin dispositivos registrados"
            description="El registro está disponible; solo se muestran datos reales."
          />
        ) : (
          <>
            <ul className="mini-device-list">
              {dispositivos.slice(0, 5).map((device) => (
                <li key={device.id}>
                  <span className="mini-device-name">
                    <strong>{device.nombre}</strong>
                    <small>{device.id}</small>
                  </span>
                  <StatusBadge tone={tonoEstado(device.estado)} dot>
                    {etiquetaEstado(device.estado)}
                  </StatusBadge>
                </li>
              ))}
            </ul>
            {onNavigate && (
              <button
                type="button"
                className="button ghost"
                onClick={() => onNavigate('dispositivos')}
              >
                Ver todos los dispositivos
                <Icon name="flecha" size={15} />
              </button>
            )}
          </>
        )}
      </section>
    )
  }

  const columnas: DataTableColumn<Device>[] = [
    {
      key: 'id',
      header: 'Identificador',
      render: (device) => <span className="mono">{device.id}</span>,
    },
    { key: 'nombre', header: 'Nombre', render: (device) => device.nombre },
    { key: 'tipo', header: 'Tipo', render: (device) => device.tipo },
    {
      key: 'ubicacion',
      header: 'Ubicación',
      render: (device) => device.ubicacion ?? '—',
    },
    { key: 'adaptador', header: 'Adaptador', render: (device) => device.adaptador },
    {
      key: 'estado',
      header: 'Estado',
      render: (device) => (
        <div className="cell-stack">
          <StatusBadge tone={tonoEstado(device.estado)} dot>
            {etiquetaEstado(device.estado)}
          </StatusBadge>
          <small className="hint">
            {device.habilitado ? 'Habilitado' : 'Desactivado'}
          </small>
        </div>
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (device) => (
        <div className="row-actions">
          <button
            type="button"
            className="button ghost small"
            onClick={() => abrirDetalle(device)}
          >
            <Icon name="detalle" size={15} />
            Detalle
          </button>
          {esAdministrador && (
            <>
              <button
                type="button"
                className="button ghost small"
                disabled={busy}
                onClick={() => {
                  setPendienteDesactivar(device)
                  setAccionError(null)
                }}
              >
                Desactivar
              </button>
            </>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="stack">
      <PageHeader
        eyebrow={VIEW_META.dispositivos.eyebrow}
        title="Dispositivos registrados"
        description="Consulte la información real de cada instancia y acceda a su detalle."
        actions={
          <button
            type="button"
            className="button ghost"
            disabled={loading || busy}
            onClick={() => void cargar()}
          >
            <Icon name="actualizar" size={16} />
            {loading ? 'Cargando…' : 'Actualizar'}
          </button>
        }
        meta={
          <StatusBadge tone={esAdministrador ? 'info' : 'neutral'}>
            {esAdministrador ? 'Administración' : 'Solo lectura'}
          </StatusBadge>
        }
      />

      {esAdministrador && (
        <section className="card" aria-labelledby="device-create-title">
          <div className="section-heading">
            <div>
              <h3 id="device-create-title">Registrar dispositivo</h3>
              <p className="hint">
                La API valida los datos; los campos marcados son obligatorios.
              </p>
            </div>
          </div>
          <form className="form-grid" onSubmit={(event) => void handleCrear(event)} noValidate>
            <FormField id="device-id" label="Identificador" required error={formError}>
              <input
                id="device-id"
                value={formulario.id}
                disabled={busy}
                aria-invalid={Boolean(formError)}
                aria-describedby={formError ? 'device-id-error' : undefined}
                onChange={(event) => {
                  setFormulario({ ...formulario, id: event.target.value })
                  setFormError(null)
                }}
              />
            </FormField>
            <FormField id="device-nombre" label="Nombre" required>
              <input
                id="device-nombre"
                value={formulario.nombre}
                disabled={busy}
                onChange={(event) =>
                  setFormulario({ ...formulario, nombre: event.target.value })
                }
              />
            </FormField>
            <FormField id="device-tipo" label="Tipo" required>
              <input
                id="device-tipo"
                value={formulario.tipo}
                disabled={busy}
                onChange={(event) =>
                  setFormulario({ ...formulario, tipo: event.target.value })
                }
              />
            </FormField>
            <FormField id="device-perfil" label="Perfil de hardware" required>
              <input
                id="device-perfil"
                value={formulario.perfil_hardware}
                disabled={busy}
                onChange={(event) =>
                  setFormulario({
                    ...formulario,
                    perfil_hardware: event.target.value,
                  })
                }
              />
            </FormField>
            <FormField id="device-ubicacion" label="Ubicación">
              <input
                id="device-ubicacion"
                value={formulario.ubicacion}
                disabled={busy}
                onChange={(event) =>
                  setFormulario({ ...formulario, ubicacion: event.target.value })
                }
              />
            </FormField>
            <FormField
              id="device-adaptador"
              label="Adaptador"
              hint="Valor declarado; la API no comprueba hardware físico."
            >
              <input
                id="device-adaptador"
                value={formulario.adaptador}
                disabled={busy}
                onChange={(event) =>
                  setFormulario({ ...formulario, adaptador: event.target.value })
                }
              />
            </FormField>
            <div className="form-actions span-all">
              <button type="submit" className="button primary" disabled={busy}>
                <Icon name="check" size={16} />
                {busy ? 'Procesando…' : 'Registrar dispositivo'}
              </button>
            </div>
          </form>
        </section>
      )}

      {notice && (
        <div className="notice" role="status">
          <Icon name="check" size={17} />
          {notice}
        </div>
      )}
      {accionError && (
        <ErrorState
          message={accionError}
          title="La operación no pudo completarse"
          compact
        />
      )}

      <section className="card" aria-labelledby="device-list-title">
        <div className="section-heading">
          <div>
            <h3 id="device-list-title">Registro de dispositivos</h3>
            <p className="hint">
              {resumen.total} registros · {resumen.habilitados} habilitados
            </p>
          </div>
          <div className="device-summary">
            <StatusBadge tone="success" dot>{resumen.conectados} conectados</StatusBadge>
            <StatusBadge tone="warning" dot>{resumen.desconectados} desconectados</StatusBadge>
          </div>
        </div>

        <div className="filter-bar">
          <div className="search-field">
            <Icon name="buscar" size={16} />
            <input
              type="search"
              aria-label="Buscar por identificador o nombre"
              placeholder="Buscar por identificador o nombre"
              value={termino}
              onChange={(event) => setTermino(event.target.value)}
            />
          </div>
          <label className="select-field">
            <span>Estado</span>
            <select
              value={filtroEstado}
              onChange={(event) => setFiltroEstado(event.target.value as EstadoFiltro)}
            >
              <option value="todos">Todos</option>
              <option value="conectado">Conectado</option>
              <option value="desconectado">Desconectado</option>
              <option value="desconocido">Desconocido</option>
            </select>
          </label>
          <label className="select-field">
            <span>Habilitación</span>
            <select
              value={filtroHabilitado}
              onChange={(event) =>
                setFiltroHabilitado(event.target.value as HabilitadoFiltro)
              }
            >
              <option value="todos">Todas</option>
              <option value="habilitados">Habilitados</option>
              <option value="desactivados">Desactivados</option>
            </select>
          </label>
        </div>

        {error ? (
          <ErrorState
            message={error}
            title="No se pudo cargar el registro"
            onRetry={() => void cargar()}
            retrying={loading}
          />
        ) : (
          <DataTable
            columns={columnas}
            rows={filtrados}
            rowKey={(device) => device.id}
            caption="Dispositivos registrados en la plataforma"
            loading={loading}
            loadingLabel="Consultando dispositivos…"
            empty={
              <EmptyState
                icon="dispositivos"
                title={
                  dispositivos?.length === 0
                    ? 'No hay dispositivos registrados'
                    : 'Sin resultados para los filtros aplicados'
                }
                description={
                  dispositivos?.length === 0
                    ? esAdministrador
                      ? 'Use el formulario de registro para crear el primer dispositivo.'
                      : 'Cuando el administrador registre dispositivos, aparecerán aquí.'
                    : 'Ajuste la búsqueda o los filtros para ver otros registros.'
                }
              />
            }
          />
        )}
      </section>

      {detalleId && (
        <section className="card detail-panel" aria-labelledby="device-detail-title">
          <div className="section-heading">
            <div>
              <h3 id="device-detail-title">Detalle del dispositivo</h3>
              <p className="hint">Información obtenida con devicesApi.get.</p>
            </div>
            <button type="button" className="button ghost" onClick={cerrarDetalle}>
              <Icon name="cerrar" size={16} />
              Cerrar
            </button>
          </div>

          {cargandoDetalle ? (
            <LoadingState label="Cargando detalle…" compact />
          ) : detalle ? (
            <>
              <dl className="detail-grid">
                <div>
                  <dt>Identificador</dt>
                  <dd className="mono">{detalle.id}</dd>
                </div>
                <div>
                  <dt>Nombre</dt>
                  <dd>{detalle.nombre}</dd>
                </div>
                <div>
                  <dt>Tipo de periférico</dt>
                  <dd>{detalle.tipo}</dd>
                </div>
                <div>
                  <dt>Perfil de hardware</dt>
                  <dd>{detalle.perfil_hardware}</dd>
                </div>
                <div>
                  <dt>Ubicación</dt>
                  <dd>{detalle.ubicacion ?? 'No declarada'}</dd>
                </div>
                <div>
                  <dt>Adaptador</dt>
                  <dd>{detalle.adaptador}</dd>
                </div>
                <div>
                  <dt>Estado de conexión</dt>
                  <dd className={`badge ${claseEstado(detalle.estado)}`}>
                    {etiquetaEstado(detalle.estado)}
                  </dd>
                </div>
                <div>
                  <dt>Habilitación</dt>
                  <dd>
                    <StatusBadge tone={detalle.habilitado ? 'success' : 'neutral'} dot>
                      {detalle.habilitado ? 'Habilitado' : 'Desactivado'}
                    </StatusBadge>
                  </dd>
                </div>
              </dl>
              <p className="hint">Fecha de registro: no disponible en la API actual.</p>

              {esAdministrador && (
                <div className="detail-config">
                  <div className="section-heading">
                    <h4>{editando ? 'Editar configuración' : 'Configuración lógica'}</h4>
                    {!editando && (
                      <button
                        type="button"
                        className="button ghost small"
                        onClick={() => iniciarEdicion(detalle)}
                      >
                        <Icon name="editar" size={15} />
                        Configurar
                      </button>
                    )}
                  </div>
                  {editando ? (
                    <form
                      className="form-grid"
                      onSubmit={(event) => void handleActualizar(event)}
                      noValidate
                    >
                      <FormField id="edit-nombre" label="Nombre" required>
                        <input
                          id="edit-nombre"
                          value={edicion.nombre}
                          disabled={busy}
                          onChange={(event) => {
                            setEdicion({ ...edicion, nombre: event.target.value })
                            setEdicionError(null)
                          }}
                        />
                      </FormField>
                      <FormField id="edit-tipo" label="Tipo" required>
                        <input
                          id="edit-tipo"
                          value={edicion.tipo}
                          disabled={busy}
                          onChange={(event) =>
                            setEdicion({ ...edicion, tipo: event.target.value })
                          }
                        />
                      </FormField>
                      <FormField id="edit-perfil" label="Perfil de hardware" required>
                        <input
                          id="edit-perfil"
                          value={edicion.perfil_hardware}
                          disabled={busy}
                          onChange={(event) =>
                            setEdicion({
                              ...edicion,
                              perfil_hardware: event.target.value,
                            })
                          }
                        />
                      </FormField>
                      <FormField id="edit-ubicacion" label="Ubicación">
                        <input
                          id="edit-ubicacion"
                          value={edicion.ubicacion}
                          disabled={busy}
                          onChange={(event) =>
                            setEdicion({ ...edicion, ubicacion: event.target.value })
                          }
                        />
                      </FormField>
                      <FormField id="edit-adaptador" label="Adaptador">
                        <input
                          id="edit-adaptador"
                          value={edicion.adaptador}
                          disabled={busy}
                          onChange={(event) =>
                            setEdicion({ ...edicion, adaptador: event.target.value })
                          }
                        />
                      </FormField>
                      {edicionError && (
                        <p className="field-error span-all" role="alert">
                          {edicionError}
                        </p>
                      )}
                      <div className="form-actions span-all">
                        <button type="submit" className="button primary" disabled={busy}>
                          {busy ? 'Guardando…' : 'Guardar cambios'}
                        </button>
                        <button
                          type="button"
                          className="button ghost"
                          disabled={busy}
                          onClick={() => {
                            setEditando(false)
                            setEdicionError(null)
                          }}
                        >
                          Cancelar
                        </button>
                      </div>
                    </form>
                  ) : (
                    <p className="hint">
                      Solo el administrador puede modificar la configuración lógica.
                    </p>
                  )}
                </div>
              )}

              <div className="detail-events">
                <div className="section-heading">
                  <h4>Eventos de cambio de estado</h4>
                  <button
                    type="button"
                    className="button ghost small"
                    disabled={cargandoEventos}
                    onClick={() => void handleEventos()}
                  >
                    <Icon name="eventos" size={15} />
                    {cargandoEventos
                      ? 'Consultando…'
                      : eventosVisibles
                        ? 'Ocultar eventos'
                        : 'Consultar eventos'}
                  </button>
                </div>
                {cargandoEventos ? (
                  <LoadingState compact label="Consultando eventos…" />
                ) : eventosVisibles ? (
                  eventos === null || eventos.length === 0 ? (
                    <EmptyState
                      compact
                      icon="eventos"
                      title="Sin transiciones registradas"
                      description="La API no devolvió eventos de cambio de estado para este dispositivo."
                    />
                  ) : (
                    <ul className="event-list">
                      {eventos.map((evento, indice) => (
                        <li key={`${evento.ocurrido_en}-${indice}`}>
                          <StatusBadge tone={tonoEstado(evento.estado_anterior)}>
                            {etiquetaEstado(evento.estado_anterior)}
                          </StatusBadge>
                          <Icon name="flecha" size={14} />
                          <StatusBadge tone={tonoEstado(evento.estado_nuevo)}>
                            {etiquetaEstado(evento.estado_nuevo)}
                          </StatusBadge>
                          <time dateTime={evento.ocurrido_en}>
                            {new Date(evento.ocurrido_en).toLocaleString('es-ES')}
                          </time>
                        </li>
                      ))}
                    </ul>
                  )
                ) : (
                  <p className="hint">
                    Los eventos se consultan únicamente cuando se solicitan.
                  </p>
                )}
              </div>
            </>
          ) : (
            <p className="hint">No fue posible cargar el detalle.</p>
          )}
        </section>
      )}

      <ConfirmDialog
        open={pendienteDesactivar !== null}
        title="Desactivar dispositivo"
        description={`Se desactivará "${pendienteDesactivar?.nombre ?? ''}". Esta operación se registra en la API y el dispositivo dejará de estar habilitado.`}
        confirmLabel="Desactivar"
        destructive
        busy={busy}
        onConfirm={() => void confirmarDesactivacion()}
        onCancel={() => setPendienteDesactivar(null)}
      />
    </div>
  )
}
