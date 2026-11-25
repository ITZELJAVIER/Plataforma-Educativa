import type { ReactNode } from 'react'

interface FormFieldProps {
  id: string
  label: string
  children: ReactNode
  hint?: string
  error?: string | null
  required?: boolean
  className?: string
}

export function FormField({
  id,
  label,
  children,
  hint,
  error,
  required = false,
  className = '',
}: FormFieldProps) {
  return (
    <div className={`form-field ${className}`.trim()}>
      <label htmlFor={id}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </label>
      {children}
      {error ? (
        <p className="field-error" id={`${id}-error`}>
          {error}
        </p>
      ) : hint ? (
        <p className="field-hint" id={`${id}-hint`}>
          {hint}
        </p>
      ) : null}
    </div>
  )
}
