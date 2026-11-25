import type { Role } from '../types/user'

export const VIEWS = [
  'inicio',
  'dispositivos',
  'catalogo',
  'usuarios',
  'perfil',
  'configuracion',
  'monitoreo',
] as const

export type View = (typeof VIEWS)[number]

export type IconName =
  | 'inicio'
  | 'dispositivos'
  | 'catalogo'
  | 'usuarios'
  | 'perfil'
  | 'configuracion'
  | 'monitoreo'
  | 'salir'
  | 'canales'
  | 'medida'
  | 'rango'
  | 'menu'
  | 'cerrar'
  | 'sol'
  | 'luna'
  | 'sistema'
  | 'actualizar'
  | 'buscar'
  | 'editar'
  | 'detalle'
  | 'eventos'
  | 'informacion'
  | 'etiqueta'
  | 'estado'
  | 'calendario'
  | 'flecha'
  | 'check'
  | 'alerta'

export interface NavItem {
  view: View
  label: string
  icon: IconName
  adminOnly?: boolean
}

export interface ViewMeta {
  title: string
  description: string
  breadcrumb: string
  eyebrow: string
}

export const NAV_ITEMS: readonly NavItem[] = [
  { view: 'inicio', label: 'Inicio', icon: 'inicio' },
  { view: 'dispositivos', label: 'Dispositivos', icon: 'dispositivos' },
  { view: 'catalogo', label: 'Catálogo de periféricos', icon: 'catalogo' },
  { view: 'usuarios', label: 'Usuarios', icon: 'usuarios', adminOnly: true },
  { view: 'perfil', label: 'Mi perfil', icon: 'perfil' },
  { view: 'configuracion', label: 'Configuración', icon: 'configuracion' },
  { view: 'monitoreo', label: 'Monitoreo', icon: 'monitoreo' },
]

export const VIEW_META: Record<View, ViewMeta> = {
  inicio: {
    title: 'Inicio',
    description: 'Resumen de la plataforma a partir de los servicios disponibles.',
    breadcrumb: 'Panel principal',
    eyebrow: 'Panel principal',
  },
  dispositivos: {
    title: 'Dispositivos',
    description: 'Registro, configuración y estado de las instancias reales.',
    breadcrumb: 'Recursos',
    eyebrow: 'Recursos',
  },
  catalogo: {
    title: 'Catálogo de periféricos',
    description: 'Tipos y metadatos empleados por la plataforma.',
    breadcrumb: 'Referencia',
    eyebrow: 'Referencia',
  },
  usuarios: {
    title: 'Usuarios',
    description: 'Cuentas, roles y estado de acceso a la plataforma.',
    breadcrumb: 'Administración',
    eyebrow: 'Administración',
  },
  perfil: {
    title: 'Mi perfil',
    description: 'Información de la cuenta autenticada.',
    breadcrumb: 'Cuenta',
    eyebrow: 'Cuenta',
  },
  configuracion: {
    title: 'Configuración',
    description: 'Preferencias de interfaz e información general.',
    breadcrumb: 'Preferencias',
    eyebrow: 'Preferencias',
  },
  monitoreo: {
    title: 'Monitoreo',
    description: 'Capacidades previstas para la supervisión IoT.',
    breadcrumb: 'Operación',
    eyebrow: 'Operación',
  },
}

export function navItemsFor(esAdministrador: boolean): NavItem[] {
  return NAV_ITEMS.filter((item) => !item.adminOnly || esAdministrador)
}

export function isViewAllowed(view: View, esAdministrador: boolean): boolean {
  const item = NAV_ITEMS.find((navItem) => navItem.view === view)
  return item ? !item.adminOnly || esAdministrador : false
}

export function roleLabel(role: Role): string {
  switch (role) {
    case 'administrador':
      return 'Administrador'
    case 'docente':
      return 'Docente'
    case 'estudiante':
      return 'Estudiante'
  }
}
