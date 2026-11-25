import { Icon } from '../app/icons'
import type { IconName } from '../app/navigation'
import { themePreferenceLabel, type ResolvedTheme, type ThemePreference } from '../app/theme'

interface ThemeToggleProps {
  theme: ResolvedTheme
  preference?: ThemePreference
  onChange: (preference: ThemePreference) => void
  variant?: 'compact' | 'full'
}

const ICONOS: Record<ThemePreference, IconName> = {
  sistema: 'sistema',
  claro: 'sol',
  oscuro: 'luna',
}

export function ThemeToggle({
  theme,
  preference = 'sistema',
  onChange,
  variant = 'compact',
}: ThemeToggleProps) {
  const opciones: ThemePreference[] =
    variant === 'compact' ? ['claro', 'oscuro'] : ['sistema', 'claro', 'oscuro']

  return (
    <div
      className={`theme-toggle ${variant === 'compact' ? 'compact' : 'full'}`}
      role="group"
      aria-label="Preferencia de tema"
    >
      {opciones.map((opcion) => {
        const activo = variant === 'compact' ? theme === opcion : preference === opcion
        return (
          <button
            key={opcion}
            type="button"
            className={activo ? 'theme-option active' : 'theme-option'}
            aria-pressed={activo}
            title={themePreferenceLabel(opcion)}
            onClick={() => onChange(opcion)}
          >
            <Icon name={ICONOS[opcion]} size={16} />
            {variant === 'full' && <span>{themePreferenceLabel(opcion)}</span>}
          </button>
        )
      })}
    </div>
  )
}
