import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'

import { Icon } from '../../app/icons'
import { VIEW_META } from '../../app/navigation'
import { errorMessage, usersApi } from '../../services/api'
import { ROLES, type Role, type User } from '../../types/user'
import { ConfirmDialog } from '../../components/ConfirmDialog'
import { DataTable, type DataTableColumn } from '../../components/DataTable'
import { EmptyState } from '../../components/EmptyState'
import { ErrorState } from '../../components/ErrorState'
import { FormField } from '../../components/FormField'
import { PageHeader } from '../../components/PageHeader'
import { StatusBadge } from '../../components/StatusBadge'

interface UserAdminProps {
  token: string
}

export function UserAdmin({ token }: UserAdminProps) {
  const [users, setUsers] = useState<User[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [id, setId] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<Role>('estudiante')
  const [termino, setTermino] = useState('')
  const [pendiente, setPendiente] = useState<User | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setUsers(await usersApi.list(token))
    } catch (cause) {
      setUsers(null)
      setError(errorMessage(cause))
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    void load()
  }, [load])

  const filtrados = useMemo(() => {
    const texto = termino.trim().toLocaleLowerCase('es')
    if (!texto) return users ?? []
    return (users ?? []).filter((item) =>
      item.id.toLocaleLowerCase('es').includes(texto),
    )
  }, [users, termino])

  async function run(
    action: () => Promise<unknown>,
    mensaje: string,
    resetForm = false,
  ) {
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      await action()
      setNotice(mensaje)
      if (resetForm) {
        setId('')
        setPassword('')
        setFormError(null)
      }
      await load()
      return true
    } catch (cause) {
      setError(errorMessage(cause))
      return false
    } finally {
      setBusy(false)
    }
  }

  function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!id.trim() || !password) {
      setFormError('El identificador y la contraseña son obligatorios.')
      return
    }
    void run(
      () => usersApi.create(token, id.trim(), password, role),
      'Usuario creado correctamente.',
      true,
    )
  }

  async function confirmarCambioEstado() {
    if (!pendiente) return
    const usuario = pendiente
    const correcto = await run(
      () =>
        usuario.active
          ? usersApi.deactivate(token, usuario.id)
          : usersApi.reactivate(token, usuario.id),
      usuario.active
        ? 'Usuario desactivado correctamente.'
        : 'Usuario reactivado correctamente.',
    )
    if (correcto) setPendiente(null)
  }

  const columnas: DataTableColumn<User>[] = [
    {
      key: 'id',
      header: 'Identificador',
      render: (item) => <span className="mono">{item.id}</span>,
    },
    {
      key: 'correo',
      header: 'Correo electrónico',
      render: () => <span className="hint">No disponible en la API</span>,
    },
    {
      key: 'rol',
      header: 'Rol',
      render: (item) => (
        <select
          aria-label={`Rol de ${item.id}`}
          value={item.role}
          disabled={busy}
          onChange={(event) => {
            const nextRole = event.target.value as Role
            void run(
              () => usersApi.changeRole(token, item.id, nextRole),
              'Rol actualizado correctamente.',
            )
          }}
        >
          {ROLES.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      ),
    },
    {
      key: 'estado',
      header: 'Estado',
      render: (item) => (
        <StatusBadge tone={item.active ? 'success' : 'neutral'} dot>
          {item.active ? 'Activo' : 'Inactivo'}
        </StatusBadge>
      ),
    },
    {
      key: 'accion',
      header: 'Acción',
      render: (item) => (
        <button
          type="button"
          className={item.active ? 'button danger small' : 'button ghost small'}
          disabled={busy}
          onClick={() => setPendiente(item)}
        >
          {item.active ? 'Desactivar' : 'Reactivar'}
        </button>
      ),
    },
  ]

  return (
    <div className="stack">
      <PageHeader
        eyebrow={VIEW_META.usuarios.eyebrow}
        title="Usuarios registrados"
        description="Cree cuentas, consulte roles y gestione el estado de acceso."
        actions={
          <button
            type="button"
            className="button ghost"
            disabled={loading || busy}
            onClick={() => void load()}
          >
            <Icon name="actualizar" size={16} />
            {loading ? 'Cargando…' : 'Actualizar'}
          </button>
        }
        meta={<StatusBadge tone="info">Acceso de administrador</StatusBadge>}
      />

      <section className="card" aria-labelledby="user-create-title">
        <div className="section-heading">
          <div>
            <h3 id="user-create-title">Crear usuario</h3>
            <p className="hint">El backend valida las credenciales y el rol asignado.</p>
          </div>
        </div>
        <form className="form-grid" onSubmit={handleCreate} noValidate>
          <FormField id="new-user-id" label="Identificador" required>
            <input
              id="new-user-id"
              value={id}
              disabled={busy}
              autoComplete="off"
              onChange={(event) => {
                setId(event.target.value)
                setFormError(null)
              }}
            />
          </FormField>
          <FormField id="new-user-password" label="Contraseña" required>
            <input
              id="new-user-password"
              type="password"
              autoComplete="new-password"
              value={password}
              disabled={busy}
              onChange={(event) => {
                setPassword(event.target.value)
                setFormError(null)
              }}
            />
          </FormField>
          <FormField id="new-user-role" label="Rol" required>
            <select
              id="new-user-role"
              value={role}
              disabled={busy}
              onChange={(event) => setRole(event.target.value as Role)}
            >
              {ROLES.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </FormField>
          {formError && (
            <p className="field-error span-all" role="alert">
              {formError}
            </p>
          )}
          <div className="form-actions span-all">
            <button type="submit" className="button primary" disabled={busy}>
              <Icon name="check" size={16} />
              {busy ? 'Procesando…' : 'Crear usuario'}
            </button>
          </div>
        </form>
      </section>

      {notice && (
        <div className="notice" role="status">
          <Icon name="check" size={17} />
          {notice}
        </div>
      )}
      {error && (
        <ErrorState
          message={error}
          title="La operación no pudo completarse"
          onRetry={() => void load()}
          retrying={loading}
        />
      )}

      <section className="card" aria-labelledby="user-list-title">
        <div className="section-heading">
          <div>
            <h3 id="user-list-title">Cuentas registradas</h3>
            <p className="hint">
              Los correos electrónicos no forman parte del contrato actual de la API.
            </p>
          </div>
          <div className="search-field">
            <Icon name="buscar" size={16} />
            <input
              type="search"
              aria-label="Buscar usuario por identificador"
              placeholder="Buscar por identificador"
              value={termino}
              onChange={(event) => setTermino(event.target.value)}
            />
          </div>
        </div>

        <DataTable
          columns={columnas}
          rows={filtrados}
          rowKey={(item) => item.id}
          caption="Usuarios registrados en la plataforma"
          loading={loading}
          loadingLabel="Cargando usuarios…"
          empty={
            <EmptyState
              icon="usuarios"
              title={users?.length === 0 ? 'No hay usuarios registrados' : 'Sin resultados'}
              description={
                users?.length === 0
                  ? 'La API no devolvió cuentas registradas.'
                  : 'Ajuste el término de búsqueda para ver otros usuarios.'
              }
            />
          }
        />
      </section>

      <ConfirmDialog
        open={pendiente !== null}
        title={pendiente?.active ? 'Desactivar usuario' : 'Reactivar usuario'}
        description={
          pendiente?.active
            ? `Se desactivará la cuenta "${pendiente.id}". El usuario no podrá autenticarse mientras esté inactiva.`
            : `Se reactivará la cuenta "${pendiente?.id ?? ''}". Podrá volver a autenticarse.`
        }
        confirmLabel={pendiente?.active ? 'Desactivar' : 'Reactivar'}
        destructive={pendiente?.active ?? false}
        busy={busy}
        onConfirm={() => void confirmarCambioEstado()}
        onCancel={() => setPendiente(null)}
      />
    </div>
  )
}
