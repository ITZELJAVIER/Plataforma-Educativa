import type {
  Device,
  DeviceConfigInput,
  DeviceInput,
  DeviceStateEvent,
} from '../types/device'
import type {
  PeripheralType,
  PeripheralTypeInput,
} from '../types/peripheral'
import type { Role, TokenResponse, User } from '../types/user'

const DEFAULT_BASE_URL = 'http://localhost:8000/api/v1'
const TOKEN_KEY = 'plataforma-educativa-token'

type Method = 'GET' | 'POST' | 'PATCH'

interface RequestOptions {
  method?: Method
  body?: unknown
  token?: string | null
}

function baseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL?.trim()
  return (configured || DEFAULT_BASE_URL).replace(/\/+$/, '')
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Error inesperado.'
}

export function readToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function saveToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY)
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {}

  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`
  }

  let response: Response
  try {
    response = await fetch(`${baseUrl()}${path}`, {
      method: options.method ?? 'GET',
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    })
  } catch {
    throw new ApiError(0, 'No fue posible conectar con la API.')
  }

  if (!response.ok) {
    let detail = 'La solicitud no pudo completarse.'
    try {
      const payload = (await response.json()) as { detail?: unknown }
      if (typeof payload.detail === 'string') {
        detail = payload.detail
      }
    } catch {
      // La respuesta de error no incluye un cuerpo JSON.
    }
    throw new ApiError(response.status, detail)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

export const authApi = {
  login: (id: string, password: string): Promise<TokenResponse> =>
    request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: { id, password },
    }),
  logout: (token: string): Promise<void> =>
    request<void>('/auth/logout', { method: 'POST', token }),
  me: (token: string): Promise<User> => request<User>('/users/me', { token }),
}

export const usersApi = {
  list: (token: string): Promise<User[]> => request<User[]>('/users', { token }),
  create: (
    token: string,
    id: string,
    password: string,
    role: Role,
  ): Promise<User> =>
    request<User>('/users', {
      method: 'POST',
      body: { id, password, roles: [role] },
      token,
    }),
  changeRole: (token: string, id: string, role: Role): Promise<User> =>
    request<User>(`/users/${encodeURIComponent(id)}/role`, {
      method: 'PATCH',
      body: { roles: [role] },
      token,
    }),
  deactivate: (token: string, id: string): Promise<User> =>
    request<User>(`/users/${encodeURIComponent(id)}/deactivate`, {
      method: 'POST',
      token,
    }),
  reactivate: (token: string, id: string): Promise<User> =>
    request<User>(`/users/${encodeURIComponent(id)}/reactivate`, {
      method: 'POST',
      token,
    }),
}

export const devicesApi = {
  list: (token: string): Promise<Device[]> => request<Device[]>('/devices', { token }),
  get: (token: string, id: string): Promise<Device> =>
    request<Device>(`/devices/${encodeURIComponent(id)}`, { token }),
  create: (token: string, data: DeviceInput): Promise<Device> =>
    request<Device>('/devices', { method: 'POST', body: data, token }),
  update: (token: string, id: string, data: DeviceConfigInput): Promise<Device> =>
    request<Device>(`/devices/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: data,
      token,
    }),
  deactivate: (token: string, id: string): Promise<Device> =>
    request<Device>(`/devices/${encodeURIComponent(id)}/deactivate`, {
      method: 'POST',
      token,
    }),
  events: (token: string, id: string): Promise<DeviceStateEvent[]> =>
    request<DeviceStateEvent[]>(`/devices/${encodeURIComponent(id)}/events`, { token }),
}

export const catalogApi = {
  list: (token: string): Promise<PeripheralType[]> =>
    request<PeripheralType[]>('/peripherals/types', { token }),
  create: (token: string, metadata: PeripheralTypeInput): Promise<PeripheralType> =>
    request<PeripheralType>('/peripherals/types', {
      method: 'POST',
      body: metadata,
      token,
    }),
  update: (
    token: string,
    tipo: string,
    metadata: PeripheralTypeInput,
  ): Promise<PeripheralType> =>
    request<PeripheralType>(`/peripherals/types/${encodeURIComponent(tipo)}`, {
      method: 'PATCH',
      body: metadata,
      token,
    }),
  validateValue: (
    token: string,
    tipo: string,
    valor: number,
  ): Promise<{ valido: boolean; tipo: string }> =>
    request<{ valido: boolean; tipo: string }>(
      `/peripherals/types/${encodeURIComponent(tipo)}/validate-value`,
      { method: 'POST', body: { valor }, token },
    ),
}
