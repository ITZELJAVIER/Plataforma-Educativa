import type { Device, DeviceState } from '../../types/device'

const ETIQUETAS: Record<DeviceState, string> = {
  conectado: 'Conectado',
  desconectado: 'Desconectado',
  desconocido: 'Desconocido',
}

const CLASES: Record<DeviceState, string> = {
  conectado: 'state-connected',
  desconectado: 'state-disconnected',
  desconocido: 'state-unknown',
}

export interface DeviceSummary {
  total: number
  conectados: number
  desconectados: number
  desconocidos: number
  habilitados: number
}

export function etiquetaEstado(estado: DeviceState): string {
  return ETIQUETAS[estado]
}

export function claseEstado(estado: DeviceState): string {
  return CLASES[estado]
}

/** Resumen calculado únicamente a partir de registros devueltos por la API. */
export function resumirDispositivos(dispositivos: Device[]): DeviceSummary {
  return {
    total: dispositivos.length,
    conectados: dispositivos.filter((item) => item.estado === 'conectado').length,
    desconectados: dispositivos.filter((item) => item.estado === 'desconectado').length,
    desconocidos: dispositivos.filter((item) => item.estado === 'desconocido').length,
    habilitados: dispositivos.filter((item) => item.habilitado).length,
  }
}
