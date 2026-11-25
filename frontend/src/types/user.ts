export const ROLES = ['administrador', 'docente', 'estudiante'] as const

export type Role = (typeof ROLES)[number]

export interface User {
  id: string
  role: Role
  active: boolean
}

export interface TokenResponse {
  token: string
}
