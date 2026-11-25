import type { ReactNode } from 'react'

import { Icon } from '../app/icons'
import type { IconName } from '../app/navigation'

interface EmptyStateProps {
  title: string
  description: string
  icon?: IconName
  action?: ReactNode
  compact?: boolean
}

export function EmptyState({
  title,
  description,
  icon = 'informacion',
  action,
  compact = false,
}: EmptyStateProps) {
  return (
    <div className={`empty-state${compact ? ' compact' : ''}`}>
      <span className="empty-icon" aria-hidden="true">
        <Icon name={icon} size={compact ? 18 : 22} />
      </span>
      <div>
        <p className="empty-title">{title}</p>
        <p className="empty-description">{description}</p>
        {action && <div className="empty-action">{action}</div>}
      </div>
    </div>
  )
}
