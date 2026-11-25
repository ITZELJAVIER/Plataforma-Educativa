export const DEVICE_STATES = ['conectado', 'desconectado', 'desconocido'] as const

export type DeviceState = (typeof DEVICE_STATES)[number]

export interface Device {
  id: string
  nombre: string
  tipo: string
  perfil_hardware: string
  ubicacion: string | null
  habilitado: boolean
  adaptador: string
  estado: DeviceState
}

export interface DeviceStateEvent {
  device_id: string
  estado_anterior: DeviceState
  estado_nuevo: DeviceState
  ocurrido_en: string
}

export interface DeviceInput {
  id: string
  nombre: string
  tipo: string
  perfil_hardware: string
  ubicacion?: string | null
  adaptador?: string | null
}

export interface DeviceConfigInput {
  id?: string | null
  nombre?: string | null
  tipo?: string | null
  perfil_hardware?: string | null
  ubicacion?: string | null
  habilitado?: boolean | null
  adaptador?: string | null
}
