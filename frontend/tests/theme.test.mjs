import assert from 'node:assert/strict'
import test from 'node:test'

import {
  isThemePreference,
  resolveTheme,
  themePreferenceLabel,
} from '../src/app/theme.ts'

test('solo se aceptan las tres preferencias definidas', () => {
  assert.equal(isThemePreference('sistema'), true)
  assert.equal(isThemePreference('claro'), true)
  assert.equal(isThemePreference('oscuro'), true)
  assert.equal(isThemePreference('auto'), false)
  assert.equal(isThemePreference(null), false)
})

test('la preferencia explícita prevalece sobre el sistema', () => {
  assert.equal(resolveTheme('claro', true), 'claro')
  assert.equal(resolveTheme('oscuro', false), 'oscuro')
})

test('sin preferencia guardada se respeta el sistema', () => {
  assert.equal(resolveTheme('sistema', true), 'oscuro')
  assert.equal(resolveTheme('sistema', false), 'claro')
})

test('las etiquetas de preferencia son estables', () => {
  assert.equal(themePreferenceLabel('sistema'), 'Según el sistema')
  assert.equal(themePreferenceLabel('claro'), 'Claro')
  assert.equal(themePreferenceLabel('oscuro'), 'Oscuro')
})
