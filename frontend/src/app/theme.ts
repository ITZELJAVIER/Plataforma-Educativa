export type ThemePreference = 'sistema' | 'claro' | 'oscuro'
export type ResolvedTheme = 'claro' | 'oscuro'

export const THEME_STORAGE_KEY = 'plataforma-educativa-tema'

const PREFERENCIAS: readonly ThemePreference[] = ['sistema', 'claro', 'oscuro']

export function isThemePreference(value: unknown): value is ThemePreference {
  return typeof value === 'string' && PREFERENCIAS.includes(value as ThemePreference)
}

function storage(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.localStorage
  } catch {
    return null
  }
}

export function readThemePreference(): ThemePreference {
  const guardado = storage()?.getItem(THEME_STORAGE_KEY) ?? null
  return isThemePreference(guardado) ? guardado : 'sistema'
}

export function writeThemePreference(preference: ThemePreference): void {
  try {
    storage()?.setItem(THEME_STORAGE_KEY, preference)
  } catch {
    // El tema sigue funcionando durante la sesión aunque localStorage no esté disponible.
  }
}

export function resolveTheme(
  preference: ThemePreference,
  systemPrefersDark = false,
): ResolvedTheme {
  if (preference === 'claro') return 'claro'
  if (preference === 'oscuro') return 'oscuro'
  return systemPrefersDark ? 'oscuro' : 'claro'
}

export function themePreferenceLabel(preference: ThemePreference): string {
  switch (preference) {
    case 'sistema':
      return 'Según el sistema'
    case 'claro':
      return 'Claro'
    case 'oscuro':
      return 'Oscuro'
  }
}

export function applyResolvedTheme(theme: ResolvedTheme, doc?: Document): void {
  const documento = doc ?? (typeof document === 'undefined' ? null : document)
  if (!documento) return
  documento.documentElement.dataset.theme = theme
  documento.documentElement.style.colorScheme = theme === 'oscuro' ? 'dark' : 'light'
}
