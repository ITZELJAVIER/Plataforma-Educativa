import assert from 'node:assert/strict'
import test from 'node:test'

import {
  claseEstado,
  etiquetaEstado,
  resumirDispositivos,
} from '../src/features/devices/presentation.ts'
import { DEVICE_STATES } from '../src/types/device.ts'

function dispositivo(id, estado, habilitado = true) {
  return {
    id,
    nombre: `Dispositivo ${id}`,
    tipo: 'LED',
    perfil_hardware: 'perfil',
    ubicacion: null,
    habilitado,
    adaptador: 'simulado',
    estado,
  }
}

test('los estados expuestos son solo los tres definidos', () => {
  assert.deepEqual([...DEVICE_STATES], [
    'conectado',
    'desconectado',
    'desconocido',
  ])
})

test('las etiquetas y clases de estado son Consistentes', () => {
  assert.equal(etiquetaEstado('conectado'), 'Conectado')
  assert.equal(etiquetaEstado('desconectado'), 'Desconectado')
  assert.equal(etiquetaEstado('desconocido'), 'Desconocido')
  assert.equal(claseEstado('conectado'), 'state-connected')
  assert.equal(claseEstado('desconectado'), 'state-disconnected')
  assert.equal(claseEstado('desconocido'), 'state-unknown')
})

test('el resumen se calcula solo con registros reales', () => {
  const registros = [
    dispositivo('a', 'conectado'),
    dispositivo('b', 'desconectado'),
    dispositivo('c', 'desconocido'),
    dispositivo('d', 'conectado', false),
  ]

  assert.deepEqual(resumirDispositivos(registros), {
    total: 4,
    conectados: 2,
    desconectados: 1,
    desconocidos: 1,
    habilitados: 3,
  })
  assert.deepEqual(resumirDispositivos([]), {
    total: 0,
    conectados: 0,
    desconectados: 0,
    desconocidos: 0,
    habilitados: 0,
  })
})
