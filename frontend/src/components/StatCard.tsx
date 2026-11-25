import type { IconName } from '../app/navigation'
import { Icon } from '../app/icons'

type StatTone = 'default' | 'success' | 'warning' | 'muted'

interface StatCardProps {
  label: string
  value: string
  hint?: string
  icon?: IconName
  tone?: StatTone
}

export function StatCard({
  label,
  value,
  hint,
  icon,
  tone = 'default',
}: StatCardProps) {
  return (
    <article className={`stat-card stat-${tone}`}>
      <div className="stat-card-top">
        <span className="stat-label">{label}</span>
        {icon && (
          <span className="stat-icon">
            <Icon name={icon} size={17} />
          </span>
        )}
      </div>
      <strong className="stat-value">{value}</strong>
      {hint && <span className="stat-hint">{hint}</span>}
    </article>
  )
}
