# user-auth

API de autenticación y administración de usuarios de la plataforma. Las rutas
están versionadas bajo `/api/v1`. Las credenciales de sesión se envían en la
cabecera `Authorization: Bearer <token>`.

## Variables de entorno

La API exige `SESSION_TTL_SECONDS` (entero mayor que cero). La conexión a
PostgreSQL se construye con `DATABASE_URL` o, si esta no está definida, con
`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER` y
`POSTGRES_PASSWORD`. Si falta alguna variable obligatoria, el arranque termina
con un mensaje explícito. Los valores de ejemplo no son credenciales reales.

El frontend acepta `VITE_API_BASE_URL`; si no se define, usa
`http://localhost:8000/api/v1`. La API acepta `CORS_ALLOWED_ORIGINS` (lista
separada por comas) para autorizar el origen del navegador; por defecto permite
`http://localhost:5173`.

## Rutas

| Método y ruta | Uso | Acceso |
| --- | --- | --- |
| `POST /api/v1/auth/login` | Inicia sesión con `id` y `password`; devuelve `token` | Público |
| `POST /api/v1/auth/logout` | Invalida la sesión activa | Sesión válida |
| `GET /api/v1/users/me` | Consulta el usuario autenticado | Sesión válida |
| `GET /api/v1/users` | Lista usuarios | Administrador |
| `POST /api/v1/users` | Crea un usuario con `id`, `password` y `roles` | Administrador |
| `GET /api/v1/users/{user_id}` | Consulta un usuario | Administrador o el propio usuario |
| `PATCH /api/v1/users/{user_id}/role` | Asigna exactamente un `roles` | Administrador |
| `POST /api/v1/users/{user_id}/deactivate` | Desactiva la cuenta e invalida sus sesiones | Administrador |
| `POST /api/v1/users/{user_id}/reactivate` | Reactiva la cuenta | Administrador |

Los roles admitidos son `administrador`, `docente` y `estudiante`. Una
operación con cero o varios roles se rechaza. Las respuestas de usuario solo
contienen `id`, `role` y `active`; nunca incluyen la contraseña ni su hash.

## Escenarios cubiertos

- Inicio de sesión correcto, contraseña incorrecta, usuario inexistente y
  cuenta desactivada con mensaje genérico `Credenciales no válidas.`.
- Cierre de sesión y rechazo de la credencial reutilizada.
- Expiración de la sesión según `SESSION_TTL_SECONDS`.
- Denegación por defecto para operaciones no explícitamente permitidas.
- Creación, consulta, cambio de rol, desactivación y reactivación de usuarios.
- Auditoría de `inicio_de_sesion`, `fallo_autenticacion`, `cierre_de_sesion`,
  `cambio_de_rol`, `desactivacion_usuario` y `reactivacion_usuario`, con actor,
  acción, recurso e instante del servidor.
