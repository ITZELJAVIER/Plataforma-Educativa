# Design

## Context

Proyecto en estado inicial: el repositorio contiene únicamente el andamiaje de
OpenSpec, la configuración de OpenCode y el entorno virtual; no existe código de
aplicación. Ver `proposal.md` para la motivación del cambio.

Restricciones que condicionan el diseño:

- El lazo de control determinista se ejecuta en la FPGA y la plataforma no
  participa en él. Los comandos de la plataforma se limitan a supervisión y
  configuración.
- La placa objetivo declarada por el proyecto es la Sipeed Tang Nano 9K
  (FPGA Gowin GW1NR-9). El enlace físico entre la FPGA y el Gateway, su
  protocolo, sus niveles eléctricos y la frecuencia de adquisición **no están
  decididos**.
- El Gateway central es obligatorio y se ejecuta en una Mini PC x86 con
  Windows 11 Pro, Docker Desktop y WSL2. No se asume que comparta equipo con la
  plataforma; la topología definitiva queda pendiente.
- MQTT es obligatorio entre el Gateway y la plataforma. Se implementa como
  adaptador detrás de un puerto, sin acoplar el dominio al protocolo.
- La estructura común de mensajes JSON es la definida por la decisión EP1
  (Envelope); sus campos concretos quedan pendientes de autorización.
- Los canales quedan separados: MQTT para Gateway↔plataforma y WebSocket para
  plataforma↔frontend.
- El stack está aprobado: React + TypeScript + Vite, Apache ECharts, FastAPI,
  PostgreSQL y Docker Compose.
- Existen tres roles fijos: administrador, docente y estudiante.
- Redis está condicionado a una necesidad futura de varios procesos.
- Este cambio se limita a cuatro capacidades; los contratos de telemetría,
  eventos, comandos e historial se definen aquí, pero su módulo funcional
  completo, el ciclo de prácticas, las sesiones y los reportes corresponden al
  cambio posterior `add-practice-lifecycle`.

## Goals / Non-Goals

**Goals:**

- Establecer un límite hexagonal estable entre el dominio y el hardware, de modo
  que la comunicación con dispositivos sea sustituible sin tocar la lógica.
- Permitir el desarrollo y la validación de la plataforma sin hardware físico.
- Fijar identidad, autorización y administración de cuentas con trazabilidad.
- Fijar el registro de dispositivos y el catálogo de periféricos como datos
  descriptivos, no como código específico de cada tarjeta.
- Fijar el contrato de comunicación con el Gateway mediante MQTT y Envelope sin
  acoplar el dominio al protocolo.
- Definir la base de servicios reproducible en el nodo de despliegue, sin
  asumir co-ubicación con el Gateway.

**Non-Goals:**

- Implementar o simular el lazo de control.
- Seleccionar el enlace físico FPGA↔Gateway, su protocolo, sus niveles
  eléctricos ni la frecuencia de adquisición.
- Definir prácticas, sesiones experimentales, pipeline completo de telemetría,
  actuación o reportes.
- Fijar producto broker MQTT, tópicos, QoS, retención de mensajes, campos del
  Envelope, ubicación del simulador ni topología definitiva de despliegue.
- Incorporar Redis, inteligencia artificial, LMS, OIDC, multi-tenencia o alta
  disponibilidad.
- Comprometer umbrales cuantitativos de rendimiento ni fijar la política de
  retención del historial.

## Decisions

### D1. Arquitectura hexagonal con puerto de dispositivo

El dominio se organiza alrededor de puertos, y toda dependencia externa
(persistencia, comunicación con hardware, canal de supervisión) se implementa como
adaptador.

- **Rationale:** el hardware es la pieza menos estable del proyecto; aislarlo es lo
  que permite avanzar sin la FPGA seleccionada.
- **Alternativas consideradas:** arquitectura en capas clásica (más simple, pero
  acopla el dominio al transporte); microservicios (descartado por costo operativo
  desproporcionado para un aula).

### D2. Simulador como primer adaptador (extendido)

El primer adaptador implementa el puerto completo y genera datos de prueba
conformes al Envelope EP1. Su ubicación de ejecución no se fija en este cambio.

- **Rationale:** permite construir y demostrar la plataforma antes de resolver las
  decisiones de hardware, y sirve como referencia de contrato. Usar el mismo
  Envelope que el enlace real garantiza que sustituir el simulador por el Gateway
  no requiera cambios en el dominio.
- **Alternativas consideradas:** esperar a la tarjeta (bloquea el proyecto); datos
  falsos embebidos en la API (contamina el dominio y no valida el puerto).
- **Extensión:** la conformidad con el Envelope procede de la decisión EP1
  autorizada; no es una decisión nueva propuesta por este cambio.

### D3. Autenticación por credencial de sesión con expiración

Las contraseñas se almacenan con hash y sal individual; la sesión se representa por
una credencial con vigencia limitada y posibilidad de invalidación explícita.

- **Rationale:** cumple los requisitos de expiración e invalidación sin introducir
  un proveedor de identidad externo, que está fuera de alcance.
- **Alternativas consideradas:** sesiones de servidor con almacén compartido
  (requiere estado distribuido, precisamente lo que Redis resolvería); OIDC
  (excluido en este cambio).
- **Nota:** la duración concreta de la vigencia es configurable y queda pendiente de
  aprobación; no se fija en las especificaciones.

### D4. Autorización por rol con alcance y denegación por defecto

Cada petición se evalúa contra el rol y el alcance del recurso; lo no concedido se
deniega.

- **Rationale:** con tres roles fijos, un modelo de permisos granulares sería
  prematuro y difícil de auditar.
- **Alternativas consideradas:** listas de control por recurso (se pospone hasta que
  existan prácticas y sesiones); permisos embebidos en el frontend (rechazado: la
  autorización real solo puede residir en el servidor).

### D5. PostgreSQL como fuente de verdad con acceso por repositorios

El acceso a datos se realiza a través de puertos de repositorio.

- **Rationale:** permite pruebas con implementaciones en memoria y mantiene el
  dominio independiente del motor.
- **Alternativas consideradas:** SQLite (descartado por concurrencia y por
  divergencia respecto de producción); almacenamiento documental (innecesario: el
  modelo es relacional).

### D6. Catálogo de periféricos dirigido por metadatos

Un periférico se describe con datos (tipo, canales, sentido, unidad, rango,
resolución, frecuencia cuando aplique) y la interfaz web se genera a partir de esa
descripción.

- **Rationale:** es la única forma de cumplir el requisito de incorporar tipos
  nuevos sin modificar el frontend.
- **Alternativas consideradas:** tipos fijos en código (rechazado: obliga a
  desplegar por cada periférico nuevo); plugins ejecutables por periférico
  (rechazado en esta etapa: superficie de seguridad innecesaria).

### D7. Canales de supervisión separados (extendido)

La telemetría se entrega al frontend por un canal WebSocket autenticado. El canal
entre el Gateway y la plataforma es MQTT. Ambos canales son distintos y no se
sustituyen entre sí.

- **Rationale:** WebSocket es el transporte con soporte nativo en navegador que
  ofrece envío del servidor sin sondeo; MQTT es el canal autorizado para el
  enlace Gateway↔plataforma y permite desacoplar el dominio del transporte mediante
  un adaptador.
- **Alternativas consideradas:** sondeo periódico (latencia y carga innecesarias);
  Server-Sent Events (unidireccional, suficiente hoy, pero no permitiría evolución
  bidireccional); un canal único para ambos límites (rechazado: mezcla
  responsabilidades de planta y de presentación).
- **Extensión:** el canal MQTT procede de decisiones autorizadas; no es una decisión
  nueva propuesta por este cambio.

### D8. Docker Compose para los servicios de la plataforma (extendido)

- **Rationale:** reproducibilidad entre Windows y Linux con costo operativo mínimo
  para un aula.
- **Alternativas consideradas:** Kubernetes (sobredimensionado); instalación nativa
  (reintroduce la divergencia de entornos que se quiere eliminar).
- **Extensión:** el despliegue del Gateway se documenta por separado y no se asume
  que Gateway y plataforma comparten equipo. La topología definitiva queda
  pendiente de autorización.

### D9. Redis diferido detrás de un puerto de eventos

El diseño prevé la publicación de eventos como puerto; la implementación inicial
opera en un solo proceso.

- **Rationale:** el requisito prohíbe exigir Redis ahora, pero la necesidad
  aparecerá con varios procesos; el puerto evita rediseñar después.
- **Alternativas consideradas:** incorporar Redis desde el inicio (complejidad sin
  demanda real).

### D10. Alcance partido en dos cambios

Este cambio cubre identidad, dispositivos, periféricos e infraestructura; el
segundo cubre el ciclo de prácticas y la funcionalidad completa de telemetría,
eventos, comandos e historial.

- **Rationale:** reduce el tamaño de la revisión y permite estabilizar los cimientos
  antes de definir el ciclo pedagógico.
- **Trade-off aceptado:** la infraestructura se especifica sin sus consumidores
  finales; se mitiga manteniendo los contratos en el nivel de puerto.

### D11. Gateway central obligatorio (extensión de la arquitectura autorizada)

El sistema incorpora un Gateway central como componente obligatorio del enlace
entre los dispositivos y la plataforma, desplegado en una Mini PC x86 con
Windows 11 Pro, Docker Desktop y WSL2. El enlace físico entre la FPGA y el
Gateway sigue sin decidirse.

- **Rationale:** es una decisión autorizada previamente que debía reflejarse en los
  artefactos; registrar evita que la implementación lo trate como opcional.
- **Extensión de la arquitectura autorizada, no una decisión nueva de la usuaria
  en este documento.**

### D12. MQTT detrás de un puerto y un adaptador (extensión de la arquitectura autorizada)

MQTT es el canal obligatorio entre el Gateway y la plataforma. Se introduce como
adaptador del puerto de comunicación con dispositivos; el dominio no referencia
el protocolo ni un producto broker concreto.

- **Rationale:** cumple la decisión autorizada de comunicación y preserva D1: el
  transporte es sustituible sin tocar la lógica de negocio.
- **Extensión de la arquitectura autorizada, no una decisión nueva de la usuaria
  en este documento.** Broker, tópicos, QoS y retención permanecen pendientes.

### D13. Envelope EP1 como estructura común (extensión de la arquitectura autorizada)

Todo mensaje entre el Gateway y la plataforma, incluidos los del dispositivo
simulado, utiliza la estructura común de mensajes JSON definida por EP1. Los
campos concretos no se fijan aquí.

- **Rationale:** es una decisión autorizada (EP1) que debía incorporarse al
  contrato de la infraestructura para evitar implementaciones divergentes.
- **Extensión de la arquitectura autorizada, no una decisión nueva de la usuaria
  en este documento.**

### D14. Simulador conforme al Envelope (extensión de D2)

El dispositivo simulado produce y consume mensajes conformes al Envelope a través
del mismo puerto que el adaptador MQTT. Su ubicación de ejecución no se decide.

- **Rationale:** mantiene un único contrato de prueba para el simulador y para el
  enlace real, sin requerir hardware.
- **Extensión de la arquitectura autorizada, no una decisión nueva de la usuaria
  en este documento.**

### D15. Contratos de telemetría, eventos, comandos e historial (extensión de D10)

Los contratos de telemetría, eventos, comandos e historial se definen sobre el
Envelope y el puerto de dispositivo; su persistencia se prevé en el modelo de
datos. La funcionalidad completa corresponde al cambio posterior.

- **Rationale:** el contexto autorizado exige que esas capacidades existan como
  contrato, sin adelantar la implementación que D10 reserva a otro cambio.
- **Extensión de la arquitectura autorizada, no una decisión nueva de la usuaria
  en este documento.**

## Risks / Trade-offs

- [Solapamiento entre `device-management` y `peripheral-catalog`] → El catálogo
  define tipos y metadatos; la gestión de dispositivos define instancias. Un
  requisito sobre definiciones pertenece al catálogo; uno sobre instancias, a
  dispositivos.
- [Las especificaciones se escriben antes de conocer el hardware] → Ninguna spec
  fija enlace FPGA↔Gateway, protocolo, niveles eléctricos ni frecuencia; solo se
  especifica el contrato del puerto.
- [El simulador se aleja del comportamiento real] → Las pruebas del adaptador se
  escriben contra el contrato del puerto y del Envelope, no contra el simulador.
- [Desbordamiento de alcance hacia el ciclo de prácticas] → Los non-goals son
  explícitos y el segundo cambio ya está nombrado.
- [El mecanismo de autenticación puede necesitar revisión] → Se encapsula tras un
  puerto de identidad para no propagar detalles a las demás capacidades.
- [MQTT podría acoplarse al dominio] → D1 y D12 exigen adaptador y puerto; las
  pruebas de contrato se ejecutan con simulador y con MQTT.
- [Confusión entre los canales MQTT y WebSocket] → D7 establece límites distintos:
  Gateway↔plataforma y plataforma↔frontend.
- [Gateway y plataforma podrían no compartir equipo] → No se asume co-ubicación;
  la topología definitiva queda como pregunta abierta.
- [Envelope sin campos definidos] → La spec exige su uso pero no fija campos; la
  decisión concreta sigue pendiente de autorización.
- [Historial sin política de retención] → Los contratos y la persistencia se
  prevén; la política de retención queda pendiente.
- [Docker en Windows requiere WSL2] → Se documenta como prerrequisito; no se asume
  disponibilidad.
- [Diferencia de fin de línea entre Windows y contenedores Linux] → Se abordará con
  `.gitattributes` en un cambio propio; no se modifica aquí.
- [La Tang Nano 9K podría no exponer E/S suficientes o compatibles para los siete
  tipos de periférico] → El catálogo es descriptivo y no depende de la tarjeta; la
  verificación física queda como cuestión abierta.

## Migration Plan

- No aplica migración de datos: no existen datos ni esquema previos.
- Despliegue: levantar los servicios de plataforma con el comando documentado de
  Docker Compose y verificar el enlace MQTT con el Gateway desplegado en el nodo
  designado, sin asumir co-ubicación.
- Reversión: descartar los artefactos del cambio y volver al baseline `006239b`. No
  hay estado persistente que revertir en esta etapa.

## Open Questions

- ¿Qué enlace físico y qué protocolo unirán la Tang Nano 9K con el Gateway? No
  afecta a las specs: el puerto de adaptador es agnóstico.
- ¿Comparten el Gateway y la plataforma el mismo equipo o se despliegan en nodos
  separados? La topología definitiva está pendiente de autorización; no se asume
  co-ubicación.
- ¿Qué producto o broker MQTT, qué tópicos, qué QoS y qué retención de mensajes se
  utilizarán? Pendiente de autorización.
- ¿Cuáles son los campos completos del Envelope EP1? Pendiente de autorización.
- ¿Dónde se ejecutará el dispositivo simulado, en el Gateway o en la plataforma?
  Pendiente de autorización.
- ¿Qué mecanismo de autenticación y TLS se aplicará al enlace MQTT? Pendiente de
  autorización.
- ¿Qué frecuencia de adquisición y qué factores de decimado se usarán? Se declarará
  por periférico cuando se conozca.
- ¿Dispone la Tang Nano 9K de E/S suficientes y con niveles compatibles para los
  siete tipos de periférico previstos? Requiere verificación sobre la tarjeta.
- ¿Qué vigencia y estrategia de renovación tendrá la credencial de sesión? Se
  configura sin cambiar las specs.
- ¿Qué umbrales cuantitativos de rendimiento y disponibilidad se exigirán? No se
  fijan en este cambio.
- ¿Cuál será la política de retención del historial? Pendiente de autorización.
