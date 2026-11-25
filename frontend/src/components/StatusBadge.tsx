import type { ReactNode } from 'react'

type Tone = 'neutral' | 'info' | 'success' | 'warning' | 'danger'

interface StatusBadgeProps {
  children: ReactNode
  tone?: Tone
  dot?: boolean
  className?: string
}

export function StatusBadge({
  children,
  tone = 'neutral',
  dot = false,
  className = '',
}: StatusBadgeProps) {
  return (
    <span className={`status-badge tone-${tone} ${className}`.trim()}>
      {dot && <span className="status-dot" aria-hidden="true" />}
      {children}
    </span>
  )
}
