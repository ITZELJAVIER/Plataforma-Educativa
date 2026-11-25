import assert from 'node:assert/strict'
import test from 'node:test'

import { navItemsFor, roleLabel, VIEWS } from '../src/app/navigation.ts'
import { resumirCatalogo } from '../src/features/dashboard/summary.ts'

test('el menú de administrador incluye usuarios y el de los demás roles no', () => {
  const administrador = navItemsFor(true).map((item) => item.view)
  const lector = navItemsFor(false).map((item) => item.view)

  assert.deepEqual(administrador, [
    'inicio',
    'dispositivos',
    'catalogo',
    'usuarios',
    'perfil',
    'configuracion',
    'monitoreo',
  ])
  assert.deepEqual(lector, [
    'inicio',
    'dispositivos',
    'catalogo',
    'perfil',
    'configuracion',
    'monitoreo',
  ])
  assert.ok(lector.includes('dispositivos'))
  assert.ok(lector.includes('monitoreo'))
  assert.ok(lector.includes('configuracion'))
  assert.ok(!lector.includes('usuarios'))
})

test('todas las entradas del menú corresponden a una vista conocida', () => {
  for (const item of navItemsFor(true)) {
    assert.ok(VIEWS.includes(item.view))
    assert.ok(item.label.length > 0)
  }
})

test('las etiquetas de rol no introducen roles nuevos', () => {
  assert.equal(roleLabel('administrador'), 'Administrador')
  assert.equal(roleLabel('docente'), 'Docente')
  assert.equal(roleLabel('estudiante'), 'Estudiante')
})

test('los indicadores del catálogo se calculan solo con datos reales', () => {
  const definiciones = [
    {
      tipo: 'LED',
      canales: ['D0'],
      sentido: null,
      unidad: null,
      rango: null,
      resolucion: null,
      frecuencia: null,
    },
    {
      tipo: 'sensor',
      canales: ['A'],
      sentido: 'entrada',
      unidad: 'grados Celsius',
      rango: { minimo: 0, maximo: 100 },
      resolucion: 1,
      frecuencia: null,
    },
    {
      tipo: 'pulsador',
      canales: [],
      sentido: null,
      unidad: null,
      rango: null,
      resolucion: null,
      frecuencia: null,
    },
  ]

  assert.deepEqual(resumirCatalogo(definiciones), {
    total: 3,
    conCanales: 2,
    conUnidad: 1,
    conRango: 1,
  })
  assert.deepEqual(resumirCatalogo([]), {
    total: 0,
    conCanales: 0,
    conUnidad: 0,
    conRango: 0,
  })
})
