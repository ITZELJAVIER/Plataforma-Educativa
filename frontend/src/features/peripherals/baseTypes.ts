/**
 * Clasificación visual de los siete tipos base documentados.
 * No restringe el catálogo: cualquier tipo devuelto por la API se muestra igual.
 */
export const BASE_TYPE_NAMES = [
  'LED',
  'pulsador',
  'entrada digital',
  'salida digital',
  'sensor',
  'motor con PWM',
  'pantalla',
] as const

const NORMALIZADOS = new Set(
  BASE_TYPE_NAMES.map((tipo) => tipo.trim().toLocaleLowerCase('es').replace(/\s+/g, ' ')),
)

export function esTipoBase(tipo: string): boolean {
  return NORMALIZADOS.has(tipo.trim().toLocaleLowerCase('es').replace(/\s+/g, ' '))
}
