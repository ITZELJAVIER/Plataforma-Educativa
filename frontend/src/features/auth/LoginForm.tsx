import { useState, type FormEvent } from 'react'

import { errorMessage } from '../../services/api'

interface LoginFormProps {
  onLogin: (id: string, password: string) => Promise<void>
}

export function LoginForm({ onLogin }: LoginFormProps) {
  const [id, setId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await onLogin(id, password)
    } catch (cause) {
      setError(errorMessage(cause))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="card" aria-labelledby="login-title">
      <h2 id="login-title">Iniciar sesión</h2>
      <form onSubmit={(event) => void handleSubmit(event)}>
        <label htmlFor="login-id">Identificador</label>
        <input
          id="login-id"
          name="id"
          autoComplete="username"
          value={id}
          onChange={(event) => setId(event.target.value)}
          required
        />

        <label htmlFor="login-password">Contraseña</label>
        <input
          id="login-password"
          name="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button type="submit" disabled={submitting || !id || !password}>
          {submitting ? 'Entrando…' : 'Entrar'}
        </button>
      </form>
    </section>
  )
}
