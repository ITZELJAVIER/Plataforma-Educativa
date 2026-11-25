import assert from 'node:assert/strict'
import test from 'node:test'

import {
  BASE_TYPE_NAMES,
  esTipoBase,
} from '../src/features/peripherals/baseTypes.ts'

test('la clasificación visual reconoce los siete tipos base documentados', () => {
  assert.deepEqual([...BASE_TYPE_NAMES], [
    'LED',
    'pulsador',
    'entrada digital',
    'salida digital',
    'sensor',
    'motor con PWM',
    'pantalla',
  ])

  for (const tipo of BASE_TYPE_NAMES) {
    assert.equal(esTipoBase(tipo), true)
  }
})

test('un tipo personalizado no se clasifica como base', () => {
  assert.equal(esTipoBase('espectrofotometro'), false)
  assert.equal(esTipoBase('LED auxiliar'), false)
})

test('la comparación tolera mayúsculas y espacios', () => {
  assert.equal(esTipoBase('  motor   con   pwm '), true)
  assert.equal(esTipoBase('Pulsador'), true)
})
