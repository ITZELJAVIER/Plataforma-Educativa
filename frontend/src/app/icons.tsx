import type { ReactNode } from 'react'

import type { IconName } from './navigation'

const TRAZOS: Record<IconName, ReactNode> = {
  inicio: (
    <>
      <path d="M3 10.8 12 3.5l9 7.3" />
      <path d="M5.6 9.5V20.5h12.8V9.5" />
      <path d="M9.6 20.5v-6h4.8v6" />
    </>
  ),
  dispositivos: (
    <>
      <rect x="6.5" y="6.5" width="11" height="11" rx="1.5" />
      <path d="M9.5 3v3.5M14.5 3v3.5M9.5 17v3.5M14.5 17v3.5" />
      <path d="M3 9.5h3.5M3 14.5h3.5M17 9.5h3.5M17 14.5h3.5" />
    </>
  ),
  catalogo: (
    <>
      <path d="M12 3 3 7.8l9 4.8 9-4.8L12 3Z" />
      <path d="M3 12.5 12 17.3l9-4.8" />
      <path d="M3 17 12 21.8 21 17" />
    </>
  ),
  usuarios: (
    <>
      <circle cx="9" cy="8" r="3.2" />
      <path d="M3 20v-1.6A4.2 4.2 0 0 1 7.2 14.2h3.6A4.2 4.2 0 0 1 15 18.4V20" />
      <path d="M17 5.4a3.2 3.2 0 0 1 0 5.2M18 14.6a4.2 4.2 0 0 1 3 4V20" />
    </>
  ),
  perfil: (
    <>
      <circle cx="12" cy="8" r="3.6" />
      <path d="M5 20.5v-1.8A5.2 5.2 0 0 1 10.2 13.5h3.6a5.2 5.2 0 0 1 5.2 5.2v1.8" />
    </>
  ),
  configuracion: (
    <>
      <path d="M4 7h9M17 7h3M4 17h3M11 17h9" />
      <circle cx="15" cy="7" r="2" />
      <circle cx="9" cy="17" r="2" />
    </>
  ),
  monitoreo: (
    <>
      <path d="M3 12h3l2.2-5 3.6 10 2.8-7 1.8 2h4.6" />
      <path d="M4 20.5h16" />
    </>
  ),
  salir: (
    <>
      <path d="M14.5 4H19a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-4.5" />
      <path d="M10 8.5 13.5 12 10 15.5" />
      <path d="M13.5 12H4" />
    </>
  ),
  canales: (
    <>
      <circle cx="5" cy="7" r="1.5" />
      <circle cx="5" cy="12" r="1.5" />
      <circle cx="5" cy="17" r="1.5" />
      <path d="M8.5 7H20M8.5 12H20M8.5 17H20" />
    </>
  ),
  medida: (
    <>
      <path d="M4 17.5h16" />
      <path d="M6 17.5V11M12 17.5V6M18 17.5v-8" />
      <path d="M4 20.5h16" />
    </>
  ),
  rango: (
    <>
      <path d="M4 7h16M4 17h16" />
      <circle cx="9" cy="7" r="2" />
      <circle cx="15" cy="17" r="2" />
    </>
  ),
  menu: (
    <>
      <path d="M4 7h16M4 12h16M4 17h16" />
    </>
  ),
  cerrar: (
    <>
      <path d="M6 6l12 12M18 6 6 18" />
    </>
  ),
  sol: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4" />
    </>
  ),
  luna: (
    <>
      <path d="M20 14.2A8.2 8.2 0 0 1 9.8 4a8.5 8.5 0 1 0 10.2 10.2Z" />
    </>
  ),
  sistema: (
    <>
      <rect x="3" y="4.5" width="18" height="12" rx="1.5" />
      <path d="M8.5 20h7M12 16.5V20" />
    </>
  ),
  actualizar: (
    <>
      <path d="M20 11a8 8 0 1 0-2.3 6.2" />
      <path d="M20 5v6h-6" />
    </>
  ),
  buscar: (
    <>
      <circle cx="10.5" cy="10.5" r="6" />
      <path d="m15 15 5 5" />
    </>
  ),
  editar: (
    <>
      <path d="m4 20 4.5-1 10-10-3.5-3.5-10 10L4 20Z" />
      <path d="m13.5 6.5 3.5 3.5" />
    </>
  ),
  detalle: (
    <>
      <rect x="4" y="3.5" width="16" height="17" rx="1.5" />
      <path d="M8 8h8M8 12h8M8 16h5" />
    </>
  ),
  eventos: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7v5l3.5 2" />
    </>
  ),
  informacion: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 11v5" />
      <circle cx="12" cy="8" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
  etiqueta: (
    <>
      <path d="M4 4h8l8 8-8 8-8-8V4Z" />
      <circle cx="8" cy="8" r="1.2" />
    </>
  ),
  estado: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="m8 12 2.5 2.5L16 9" />
    </>
  ),
  calendario: (
    <>
      <rect x="3.5" y="5" width="17" height="15" rx="1.5" />
      <path d="M8 3v4M16 3v4M3.5 9.5h17" />
    </>
  ),
  flecha: (
    <>
      <path d="m9 6 6 6-6 6" />
    </>
  ),
  check: (
    <>
      <path d="m5 12.5 4.5 4.5L19 7" />
    </>
  ),
  alerta: (
    <>
      <path d="M12 3.5 21 19.5H3L12 3.5Z" />
      <path d="M12 9v4.5" />
      <circle cx="12" cy="16.5" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
}

interface IconProps {
  name: IconName
  className?: string
  size?: number
}

export function Icon({ name, className, size = 20 }: IconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {TRAZOS[name]}
    </svg>
  )
}
