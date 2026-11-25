import type { PeripheralType } from '../../types/peripheral'

export interface CatalogSummary {
  total: number
  conCanales: number
  conUnidad: number
  conRango: number
}

/** Indicadores calculados únicamente a partir de la respuesta real de la API. */
export function resumirCatalogo(definiciones: PeripheralType[]): CatalogSummary {
  return {
    total: definiciones.length,
    conCanales: definiciones.filter((item) => item.canales.length > 0).length,
    conUnidad: definiciones.filter((item) => item.unidad !== null).length,
    conRango: definiciones.filter((item) => item.rango !== null).length,
  }
}
