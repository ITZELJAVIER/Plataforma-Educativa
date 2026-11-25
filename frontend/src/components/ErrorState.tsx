import { Icon } from '../app/icons'

interface ErrorStateProps {
  message: string
  title?: string
  onRetry?: () => void
  retrying?: boolean
  compact?: boolean
}

export function ErrorState({
  message,
  title = 'No fue posible completar la operación',
  onRetry,
  retrying = false,
  compact = false,
}: ErrorStateProps) {
  return (
    <div className={`error-state${compact ? ' compact' : ''}`} role="alert">
      <span className="error-icon" aria-hidden="true">
        <Icon name="alerta" size={compact ? 17 : 20} />
      </span>
      <div>
        <p className="error-title">{title}</p>
        <p className="error-message">{message}</p>
        {onRetry && (
          <button
            type="button"
            className="button ghost"
            disabled={retrying}
            onClick={onRetry}
          >
            <Icon name="actualizar" size={16} />
            {retrying ? 'Reintentando…' : 'Reintentar'}
          </button>
        )}
      </div>
    </div>
  )
}
