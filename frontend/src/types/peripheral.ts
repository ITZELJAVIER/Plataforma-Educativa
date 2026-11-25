export interface ValueRange {
  minimo: number
  maximo: number
}

export interface PeripheralType {
  tipo: string
  canales: string[]
  sentido: string | null
  unidad: string | null
  rango: ValueRange | null
  resolucion: number | null
  frecuencia: number | null
}

export interface PeripheralTypeInput {
  tipo?: string | null
  canales: string[]
  sentido?: string | null
  unidad?: string | null
  rango?: ValueRange | null
  resolucion?: number | null
  frecuencia?: number | null
}
