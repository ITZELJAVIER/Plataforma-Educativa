interface LoadingStateProps {
  label?: string
  compact?: boolean
}

export function LoadingState({
  label = 'Cargando información…',
  compact = false,
}: LoadingStateProps) {
  return (
    <div className={`loading-state${compact ? ' compact' : ''}`} role="status">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}
