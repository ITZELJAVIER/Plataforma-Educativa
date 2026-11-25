# device-management

Registro, configuración lógica, estado de conexión y desactivación de los
dispositivos que supervisa la plataforma. Las rutas están versionadas bajo
`/api/v1` y requieren una sesión válida enviada como
`Authorization: Bearer <token>`.

Esta capacidad no define el enlace físico FPGA↔Gateway, no implementa
telemetría, WebSocket ni ciclo de vida de prácticas.

## Relación con el catálogo de periféricos

`peripheral-catalog` describe **tipos** reutilizables mediante metadatos.
`device-management` administra **instancias** registradas. Un dispositivo declara
un `tipo` por su identificador, sin duplicar la definición del catálogo y sin
añadir reglas de propiedad por usuario.

## Modelo de dispositivo

| Campo | Descripción |
| --- | --- |
| `id` | Identificador único e inmutable del dispositivo. |
| `nombre` | Nombre legible asignado por el administrador. |
| `tipo` | Identificador del tipo declarado en el catálogo. |
| `perfil_hardware` | Perfil de hardware declarado; no fija enlace físico. |
| `ubicacion` | Ubicación lógica opcional. |
| `habilitado` | Indica si el dispositivo puede usarse operativamente. |
| `adaptador` | Adaptador configurado; por defecto `simulado`. |
| `estado` | `conectado`, `desconectado` o `desconocido`. |

El identificador no puede modificarse. Un dispositivo sin información reportada
por el adaptador se expone como `desconocido`; no se asume `desconectado`.

## Rutas

| Método y ruta | Uso | Acceso |
| --- | --- | --- |
| `GET /api/v1/devices` | Lista los dispositivos registrados | Administrador, docente y estudiante |
| `GET /api/v1/devices/{id}` | Consulta un dispositivo | Administrador, docente y estudiante |
| `POST /api/v1/devices` | Registra un dispositivo | Administrador |
| `PATCH /api/v1/devices/{id}` | Modifica la configuración lógica | Administrador |
| `POST /api/v1/devices/{id}/deactivate` | Desactiva sin eliminar el registro | Administrador |
| `GET /api/v1/devices/{id}/events` | Consulta cambios de estado registrados | Administrador, docente y estudiante |

Las operaciones no explícitamente permitidas se deniegan. Una petición sin
sesión válida se rechaza con error de autenticación; una operación de gestión
para docente o estudiante se rechaza con error de autorización. No se han
definido asignaciones de dispositivos por rol: la consulta autenticada es la
única forma de lectura prevista en este cambio.

## Ciclo de registro, configuración y desactivación

1. El administrador registra `id`, `nombre`, `tipo`, `perfil_hardware` y,
   opcionalmente, `ubicacion` y `adaptador`. Un `id` repetido se rechaza.
2. El administrador puede modificar `nombre`, `ubicacion`, `tipo`,
   `perfil_hardware`, `habilitado` y `adaptador`. El `id` permanece inmutable.
   Cada configuración queda registrada en auditoría con actor, recurso e
   instante del servidor.
3. El administrador puede desactivar un dispositivo. El registro permanece
   consultable; el servicio deja de consultar su adaptador y no establece
   comunicación operativa con él.

## Estado de conexión y eventos

El dominio obtiene el estado únicamente del puerto de dispositivo. El adaptador
simulado y el adaptador MQTT cumplen el mismo contrato; el dominio no referencia
MQTT, broker, tópicos, QoS, retención, TLS ni campos del Envelope EP1.

Cada transición registra un evento con:

- `device_id`
- `estado_anterior`
- `estado_nuevo`
- `ocurrido_en`, instante del servidor

En esta etapa las pruebas usan un transporte falso y un sobre Envelope opaco. La
validación real contra un broker queda pendiente de las tareas `8.5` y `9.1`.
Los campos concretos del Envelope EP1 siguen pendientes de autorización; no se
fijan en este documento.

## Selección de adaptador

El adaptador activo se selecciona por configuración (`DEVICE_ADAPTER`, con valor
inicial `simulado`) y se inyecta en el caso de uso. Cambiar el adaptador no
requiere modificar el dominio. No se fija producto broker, tópicos, QoS,
retención ni parámetros de TLS.

## Escenarios cubiertos

- Registro válido y rechazo de identificador duplicado.
- Rechazo de cualquier intento de modificar el identificador.
- Estados `conectado`, `desconectado` y `desconocido` derivados del adaptador.
- Eventos de transición con estado anterior, estado nuevo e instante.
- Configuración lógica persistida y registrada en auditoría.
- Desactivación sin pérdida del registro.
- Restricción de gestión al administrador y consulta autenticada para docente y
  estudiante.
- Contrato idéntico para el adaptador simulado y el adaptador MQTT sobre el
  transporte falso autorizado.
