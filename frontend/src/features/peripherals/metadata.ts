import type { PeripheralType } from '../../types/peripheral'

export interface CampoMetadato {
  etiqueta: string
  valor: string
}

/**
 * Construye la vista de un tipo a partir de sus metadatos.
 * No contiene una lista fija de tipos: un tipo nuevo se muestra sin tocar este módulo.
 */
export function describirCampos(definicion: PeripheralType): CampoMetadato[] {
  const campos: CampoMetadato[] = [
    {
      etiqueta: 'Canales',
      valor: definicion.canales.length ? definicion.canales.join(', ') : 'sin declarar',
    },
  ]

  if (definicion.sentido) {
    campos.push({ etiqueta: 'Sentido', valor: definicion.sentido })
  }
  if (definicion.unidad) {
    campos.push({ etiqueta: 'Unidad', valor: definicion.unidad })
  }
  if (definicion.rango) {
    campos.push({
      etiqueta: 'Rango',
      valor: `${definicion.rango.minimo} – ${definicion.rango.maximo}`,
    })
  }
  if (definicion.resolucion != null) {
    campos.push({ etiqueta: 'Resolución', valor: String(definicion.resolucion) })
  }
  if (definicion.frecuencia != null) {
    campos.push({ etiqueta: 'Frecuencia', valor: String(definicion.frecuencia) })
  }

  return campos
}
