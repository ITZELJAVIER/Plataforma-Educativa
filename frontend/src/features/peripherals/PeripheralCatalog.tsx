import { useCallback, useEffect, useState, type FormEvent } from 'react'

import { Icon } from '../../app/icons'
import { VIEW_META } from '../../app/navigation'
import { catalogApi, errorMessage } from '../../services/api'
import type { PeripheralType, PeripheralTypeInput } from '../../types/peripheral'
import { EmptyState } from '../../components/EmptyState'
import { ErrorState } from '../../components/ErrorState'
import { FormField } from '../../components/FormField'
import { LoadingState } from '../../components/LoadingState'
import { PageHeader } from '../../components/PageHeader'
import { StatusBadge } from '../../components/StatusBadge'
import { esTipoBase } from './baseTypes'
import { describirCampos } from './metadata'

interface PeripheralCatalogProps {
  token: string
  esAdministrador: boolean
}

interface FormState {
  tipo: string
  canales: string
  sentido: string
  unidad: string
  rangoMinimo: string
  rangoMaximo: string
  resolucion: string
  frecuencia: string
}

const FORMULARIO_VACIO: FormState = {
  tipo: '',
  canales: '',
  sentido: '',
  unidad: '',
  rangoMinimo: '',
  rangoMaximo: '',
  resolucion: '',
  frecuencia: '',
}

function numero(texto: string): number | null {
  if (!texto.trim()) return null
  const valor = Number(texto)
  return Number.isFinite(valor) ? valor : null
}

function metadataDesdeFormulario(estado: FormState): PeripheralTypeInput {
  const minimo = numero(estado.rangoMinimo)
  const maximo = numero(estado.rangoMaximo)
  return {
    tipo: estado.tipo.trim(),
    canales: estado.canales
      .split(',')
      .map((canal) => canal.trim())
      .filter(Boolean),
    sentido: estado.sentido.trim() || null,
    unidad: estado.unidad.trim() || null,
    rango: minimo !== null && maximo !== null ? { minimo, maximo } : null,
    resolucion: numero(estado.resolucion),
    frecuencia: numero(estado.frecuencia),
  }
}

function formularioDesdeDefinicion(definicion: PeripheralType): FormState {
  return {
    tipo: definicion.tipo,
    canales: definicion.canales.join(', '),
    sentido: definicion.sentido ?? '',
    unidad: definicion.unidad ?? '',
    rangoMinimo: definicion.rango ? String(definicion.rango.minimo) : '',
    rangoMaximo: definicion.rango ? String(definicion.rango.maximo) : '',
    resolucion: definicion.resolucion === null ? '' : String(definicion.resolucion),
    frecuencia: definicion.frecuencia === null ? '' : String(definicion.frecuencia),
  }
}

function validarFormulario(estado: FormState): string | null {
  if (!estado.tipo.trim() || !estado.sentido.trim()) {
    return 'El tipo y el sentido de operación son obligatorios.'
  }
  const camposNumericos: [string, string][] = [
    ['mínimo del rango', estado.rangoMinimo],
    ['máximo del rango', estado.rangoMaximo],
    ['resolución', estado.resolucion],
    ['frecuencia', estado.frecuencia],
  ]
  for (const [etiqueta, valor] of camposNumericos) {
    if (valor.trim() && numero(valor) === null) {
      return `El ${etiqueta} debe ser un valor numérico.`
    }
  }
  const tieneMinimo = estado.rangoMinimo.trim() !== ''
  const tieneMaximo = estado.rangoMaximo.trim() !== ''
  if (tieneMinimo !== tieneMaximo) {
    return 'Indique ambos límites del rango o ninguno.'
  }
  const minimo = numero(estado.rangoMinimo)
  const maximo = numero(estado.rangoMaximo)
  if (minimo !== null && maximo !== null && minimo > maximo) {
    return 'El mínimo del rango no puede ser mayor que el máximo.'
  }
  return null
}

interface PeripheralCardProps {
  definicion: PeripheralType
  token: string
  deshabilitado: boolean
  onEditar: (definicion: PeripheralType) => void
  esAdministrador: boolean
}

function PeripheralCard({
  definicion,
  token,
  deshabilitado,
  onEditar,
  esAdministrador,
}: PeripheralCardProps) {
  const [valor, setValor] = useState('')
  const [resultado, setResultado] = useState<string | null>(null)
  const [valido, setValido] = useState(false)
  const [validando, setValidando] = useState(false)
  const campos = describirCampos(definicion)
  const base = esTipoBase(definicion.tipo)
  const idCampo = `valor-${definicion.tipo.replace(/\s+/g, '-').toLowerCase()}`

  async function handleValidar() {
    const numeroValor = numero(valor)
    if (numeroValor === null) {
      setResultado('Introduzca un valor numérico válido.')
      setValido(false)
      return
    }
    setResultado(null)
    setValidando(true)
    try {
      const respuesta = await catalogApi.validateValue(token, definicion.tipo, numeroValor)
      setValido(respuesta.valido)
      setResultado(
        respuesta.valido
          ? 'El valor cumple los metadatos declarados.'
          : 'El valor no cumple los metadatos declarados.',
      )
    } catch (cause) {
      setValido(false)
      setResultado(errorMessage(cause))
    } finally {
      setValidando(false)
    }
  }

  return (
    <article className="catalog-card">
      <div className="catalog-card-header">
        <div>
          <h4>{definicion.tipo}</h4>
          <StatusBadge tone={base ? 'info' : 'neutral'}>
            {base ? 'Tipo base' : 'Personalizado'}
          </StatusBadge>
        </div>
        {esAdministrador && (
          <button
            type="button"
            className="button ghost small"
            disabled={deshabilitado}
            onClick={() => onEditar(definicion)}
          >
            <Icon name="editar" size={15} />
            Editar
          </button>
        )}
      </div>

      <dl className="metadata-list">
        {campos.map((campo) => (
          <div key={campo.etiqueta}>
            <dt>{campo.etiqueta}</dt>
            <dd>{campo.valor}</dd>
          </div>
        ))}
      </dl>

      <div className="validate-row">
        <label htmlFor={idCampo}>Validar valor</label>
        <input
          id={idCampo}
          inputMode="decimal"
          value={valor}
          disabled={validando}
          placeholder="0"
          onChange={(event) => {
            setValor(event.target.value)
            setResultado(null)
          }}
        />
        <button
          type="button"
          className="button primary small"
          disabled={validando || !valor.trim()}
          onClick={() => void handleValidar()}
        >
          {validando ? 'Validando…' : 'Validar'}
        </button>
      </div>
      {resultado && (
        <p className={valido ? 'validation-result valid' : 'validation-result'} role="status">
          <Icon name={valido ? 'check' : 'informacion'} size={15} />
          {resultado}
        </p>
      )}
    </article>
  )
}

export function PeripheralCatalog({
  token,
  esAdministrador,
}: PeripheralCatalogProps) {
  const [definiciones, setDefiniciones] = useState<PeripheralType[] | null>(null)
  const [formulario, setFormulario] = useState<FormState>(FORMULARIO_VACIO)
  const [editando, setEditando] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  const cargar = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setDefiniciones(await catalogApi.list(token))
    } catch (cause) {
      setDefiniciones(null)
      setError(errorMessage(cause))
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    void cargar()
  }, [cargar])

  function actualizarCampo(clave: keyof FormState, valor: string) {
    setFormulario((estado) => ({ ...estado, [clave]: valor }))
    setFormError(null)
  }

  function editar(definicion: PeripheralType) {
    setEditando(definicion.tipo)
    setFormulario(formularioDesdeDefinicion(definicion))
    setFormError(null)
    setNotice(null)
  }

  function cancelarEdicion() {
    setEditando(null)
    setFormulario(FORMULARIO_VACIO)
    setFormError(null)
  }

  async function ejecutar(accion: () => Promise<unknown>, mensaje: string) {
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      await accion()
      setNotice(mensaje)
      cancelarEdicion()
      await cargar()
      return true
    } catch (cause) {
      setError(errorMessage(cause))
      return false
    } finally {
      setBusy(false)
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const validacion = validarFormulario(formulario)
    if (validacion) {
      setFormError(validacion)
      return
    }
    const metadata = metadataDesdeFormulario(formulario)
    void ejecutar(
      () =>
        editando
          ? catalogApi.update(token, editando, metadata)
          : catalogApi.create(token, metadata),
      editando
        ? 'Tipo de periférico actualizado correctamente.'
        : 'Tipo de periférico registrado correctamente.',
    )
  }

  return (
    <div className="stack">
      <PageHeader
        eyebrow={VIEW_META.catalogo.eyebrow}
        title="Tipos de periféricos"
        description="Metadatos reales empleados por la plataforma para describir y validar periféricos."
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
        <section className="card" aria-labelledby="catalog-form-title">
          <div className="section-heading">
            <div>
              <h3 id="catalog-form-title">
                {editando ? `Editar ${editando}` : 'Registrar tipo'}
              </h3>
              <p className="hint">
                El catálogo admite tipos nuevos; no se limita a los siete tipos base.
              </p>
            </div>
          </div>
          <form className="form-grid" onSubmit={handleSubmit} noValidate>
            <FormField id="peripheral-tipo" label="Tipo" required>
              <input
                id="peripheral-tipo"
                value={formulario.tipo}
                disabled={busy || editando !== null}
                onChange={(event) => actualizarCampo('tipo', event.target.value)}
              />
            </FormField>
            <FormField
              id="peripheral-canales"
              label="Canales"
              hint="Separados por coma. Ejemplo: D0, D1."
            >
              <input
                id="peripheral-canales"
                value={formulario.canales}
                disabled={busy}
                onChange={(event) => actualizarCampo('canales', event.target.value)}
              />
            </FormField>
            <FormField id="peripheral-sentido" label="Sentido de operación" required>
              <input
                id="peripheral-sentido"
                value={formulario.sentido}
                disabled={busy}
                onChange={(event) => actualizarCampo('sentido', event.target.value)}
              />
            </FormField>
            <FormField id="peripheral-unidad" label="Unidad">
              <input
                id="peripheral-unidad"
                value={formulario.unidad}
                disabled={busy}
                onChange={(event) => actualizarCampo('unidad', event.target.value)}
              />
            </FormField>
            <div className="range-fields">
              <span className="field-legend">Rango (opcional)</span>
              <div className="range-inputs">
                <FormField id="peripheral-minimo" label="Mínimo">
                  <input
                    id="peripheral-minimo"
                    inputMode="decimal"
                    value={formulario.rangoMinimo}
                    disabled={busy}
                    onChange={(event) =>
                      actualizarCampo('rangoMinimo', event.target.value)
                    }
                  />
                </FormField>
                <FormField id="peripheral-maximo" label="Máximo">
                  <input
                    id="peripheral-maximo"
                    inputMode="decimal"
                    value={formulario.rangoMaximo}
                    disabled={busy}
                    onChange={(event) =>
                      actualizarCampo('rangoMaximo', event.target.value)
                    }
                  />
                </FormField>
              </div>
            </div>
            <FormField id="peripheral-resolucion" label="Resolución">
              <input
                id="peripheral-resolucion"
                inputMode="decimal"
                value={formulario.resolucion}
                disabled={busy}
                onChange={(event) => actualizarCampo('resolucion', event.target.value)}
              />
            </FormField>
            <FormField id="peripheral-frecuencia" label="Frecuencia">
              <input
                id="peripheral-frecuencia"
                inputMode="decimal"
                value={formulario.frecuencia}
                disabled={busy}
                onChange={(event) => actualizarCampo('frecuencia', event.target.value)}
              />
            </FormField>
            {formError && (
              <p className="field-error span-all" role="alert">
                {formError}
              </p>
            )}
            <div className="form-actions span-all">
              <button type="submit" className="button primary" disabled={busy}>
                <Icon name="check" size={16} />
                {busy
                  ? 'Procesando…'
                  : editando
                    ? 'Guardar cambios'
                    : 'Registrar tipo'}
              </button>
              {editando && (
                <button
                  type="button"
                  className="button ghost"
                  disabled={busy}
                  onClick={cancelarEdicion}
                >
                  Cancelar
                </button>
              )}
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
      {error && (
        <ErrorState
          message={error}
          title="No se pudo completar la operación"
          onRetry={() => void cargar()}
          retrying={loading}
        />
      )}

      <section className="card" aria-labelledby="catalog-list-title">
        <div className="section-heading">
          <div>
            <h3 id="catalog-list-title">Tipos disponibles</h3>
            <p className="hint">
              {definiciones === null
                ? 'Consultando el catálogo…'
                : `${definiciones.length} definiciones devueltas por la API.`}
            </p>
          </div>
          <span className="legend-inline">
            <StatusBadge tone="info">Tipo base</StatusBadge>
            <StatusBadge tone="neutral">Personalizado</StatusBadge>
          </span>
        </div>

        {loading ? (
          <LoadingState label="Cargando catálogo…" />
        ) : definiciones === null ? (
          <p className="hint">El catálogo no está disponible en este momento.</p>
        ) : definiciones.length === 0 ? (
          <EmptyState
            icon="catalogo"
            title="El catálogo está vacío"
            description="La API no devolvió definiciones de periféricos."
          />
        ) : (
          <div className="catalog-grid">
            {definiciones.map((definicion) => (
              <PeripheralCard
                key={definicion.tipo}
                definicion={definicion}
                token={token}
                esAdministrador={esAdministrador}
                deshabilitado={busy}
                onEditar={editar}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
