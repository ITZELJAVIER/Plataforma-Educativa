import assert from 'node:assert/strict'
import test from 'node:test'

import { describirCampos } from '../src/features/peripherals/metadata.ts'

function definicionBase(tipo, overrides = {}) {
  return {
    tipo,
    canales: [],
    sentido: null,
    unidad: null,
    rango: null,
    resolucion: null,
    frecuencia: null,
    ...overrides,
  }
}

test('un tipo nuevo se describe solo con sus metadatos, sin lista fija', () => {
  const desconocido = definicionBase('espectrofotometro', {
    canales: ['CAN-1', 'CAN-2'],
    sentido: 'lectura',
    unidad: 'nm',
    rango: { minimo: 200, maximo: 800 },
    resolucion: 0.5,
    frecuencia: 10,
  })

  const campos = describirCampos(desconocido)
  const etiquetas = campos.map((campo) => campo.etiqueta)

  assert.deepEqual(etiquetas, [
    'Canales',
    'Sentido',
    'Unidad',
    'Rango',
    'Resolución',
    'Frecuencia',
  ])
  assert.equal(campos[0].valor, 'CAN-1, CAN-2')
  assert.equal(campos[1].valor, 'lectura')
  assert.equal(campos[2].valor, 'nm')
  assert.equal(campos[3].valor, '200 – 800')
  assert.equal(campos[4].valor, '0.5')
  assert.equal(campos[5].valor, '10')
})

test('la frecuencia no se muestra cuando no se declara', () => {
  const campos = describirCampos(
    definicionBase('sensor personalizado', {
      canales: ['A'],
      sentido: 'entrada',
      unidad: 'grados Celsius',
      rango: { minimo: 0, maximo: 100 },
      resolucion: 1,
    }),
  )

  assert.ok(!campos.some((campo) => campo.etiqueta === 'Frecuencia'))
  assert.equal(campos.length, 5)
})

test('los metadatos opcionales ausentes se omiten sin romper la tarjeta', () => {
  const campos = describirCampos(definicionBase('LED'))

  assert.deepEqual(campos, [{ etiqueta: 'Canales', valor: 'sin declarar' }])
})
