# Proposal

## Why

El proyecto necesita una base común sobre la que se construyan las prácticas de
control en tiempo real, pero hoy solo existe el andamiaje: repositorio, entorno
virtual y OpenSpec inicializados, sin ningún contrato de comportamiento. Sin
especificaciones, las decisiones arquitectónicas ya acordadas (arquitectura
hexagonal, React, FastAPI, PostgreSQL, ECharts, Docker Compose) no son
verificables y cualquier implementación posterior definiría el comportamiento por
accidente.

Además, las decisiones autorizadas correspondientes a EP1 (estructura común de
mensajes Envelope), al Gateway central obligatorio y a la comunicación MQTT entre
Gateway y plataforma no estaban reflejadas en los artefactos del cambio. Este
cambio establece el cimiento mínimo —identidad y acceso, dispositivos, catálogo
de periféricos e infraestructura base— incorporando esos contratos como parte de
la infraestructura, sin acoplarlos al dominio.

## What Changes

- Se introduce la autenticación de usuarios, la autorización por rol
  (administrador, docente, estudiante) y la administración de cuentas.
- Se introduce el registro y la administración de dispositivos, con estado de
  conexión, configuración lógica y selección de adaptador por configuración.
- Se introduce el catálogo de periféricos compatibles descritos por metadatos y
  capacidades, extensible sin modificar la interfaz web.
- Se introduce la estructura base de la plataforma: orquestación con Docker
  Compose, configuración por variables de entorno, persistencia en PostgreSQL,
  API REST versionada, canal WebSocket de telemetría hacia el frontend y puerto
  de comunicación con dispositivos con un adaptador simulado como primera
  implementación.
- Se incorpora el Gateway central obligatorio, ejecutado en una Mini PC x86 con
  Windows 11 Pro, Docker Desktop y WSL2, como componente del enlace con los
  dispositivos. No se asume que el Gateway y la plataforma comparten equipo.
- Se establece MQTT como canal obligatorio entre el Gateway y la plataforma,
  implementado como adaptador detrás del puerto de dispositivos, sin que el
  dominio dependa del protocolo.
- Se establece la estructura común de mensajes JSON Envelope (EP1 autorizada)
  para todo intercambio Gateway↔plataforma, incluidos los mensajes del
  dispositivo simulado. Los campos concretos del Envelope quedan pendientes de
  autorización.
- Se distinguen los canales: MQTT para Gateway↔plataforma y WebSocket para
  plataforma↔frontend.
- Se establece como invariante arquitectónica que la plataforma no participa en
  el lazo crítico de control, que se ejecuta en la FPGA; los comandos de la
  plataforma se limitan a supervisión y configuración.
- Se definen contratos de telemetría, eventos, comandos e historial sobre el
  Envelope, sin adelantar la funcionalidad completa de esos módulos.
- **Fuera de alcance:** gestión de prácticas, sesiones experimentales, módulo
  funcional completo de telemetría, módulo funcional completo de comandos y
  actuación, y reportes. Se abordan en el cambio posterior
  `add-practice-lifecycle`. Tampoco se fijan broker MQTT, tópicos, QoS,
  retención de mensajes, campos del Envelope, enlace físico FPGA↔Gateway,
  niveles eléctricos, frecuencias de adquisición, ubicación del simulador ni
  topología definitiva de despliegue.

## Capabilities

### New Capabilities

- `user-auth`: autenticación de usuarios, autorización por rol, administración de
  cuentas y trazabilidad de eventos de seguridad.
- `device-management`: registro, configuración lógica, estado de conexión,
  administración de dispositivos y conformidad del dispositivo simulado y del
  adaptador MQTT con el contrato Envelope.
- `peripheral-catalog`: catálogo de periféricos compatibles y metadatos que
  describen sus capacidades y límites de operación.
- `platform-infrastructure`: estructura de servicios, Gateway central, enlace
  MQTT, Envelope EP1, configuración, persistencia, API, canales de comunicación
  y servicios transversales que sostienen a las demás capacidades.

### Modified Capabilities

Ninguna fuera de este cambio: el proyecto no tiene especificaciones consolidadas
previas. Las especificaciones delta `device-management` y
`platform-infrastructure` se ajustan dentro de este mismo cambio para reflejar
las decisiones autorizadas.

## Impact

- **Código:** se crea la estructura inicial de frontend y backend; no existe
  código previo que se modifique.
- **Datos:** se introduce el esquema inicial de usuarios, roles, dispositivos,
  perfiles de hardware, periféricos, eventos de auditoría y las estructuras de
  historial previstas por los contratos de telemetría, eventos y comandos.
- **APIs:** se introduce la API REST versionada, el canal WebSocket hacia el
  frontend y el canal MQTT de entrada desde el Gateway.
- **Infraestructura:** se introduce Docker Compose para API, frontend y base de
  datos y se documenta el despliegue del Gateway en el nodo designado (Windows
  11 Pro, Docker Desktop, WSL2), sin asumir co-ubicación. Redis no se incorpora
  en este cambio; broker, tópicos y QoS no se fijan.
- **Dependencias:** se incorporan React, TypeScript, Vite, Apache ECharts,
  FastAPI, PostgreSQL y Docker Compose, ya aprobados. No se añaden frameworks de
  inteligencia artificial, federación de identidad ni multi-tenencia.
- **Hardware:** no se modifica ni se selecciona ningún elemento del enlace
  físico entre la Tang Nano 9K y el Gateway. El cambio se valida con el
  dispositivo simulado sobre el canal MQTT.
- **Compatibilidad:** no aplica; no existen consumidores previos.
