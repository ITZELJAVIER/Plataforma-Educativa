# Spec Delta

## Purpose

Define la estructura base de servicios, el Gateway central, el enlace MQTT, la
estructura común de mensajes Envelope, la configuración, la persistencia, la API
y los canales de comunicación de la plataforma, junto con los servicios
transversales que sostienen a las demás capacidades.

## ADDED Requirements

### Requirement: Orquestación con Docker Compose

El sistema SHALL definir sus servicios de plataforma en un archivo de Docker
Compose que incluya al menos la API, el frontend servido y la base de datos, de
modo que la plataforma se levante con un único comando documentado. El despliegue
del Gateway SHALL documentarse por separado, sin asumir co-ubicación.

#### Scenario: Arranque en entorno limpio

- **GIVEN** un equipo con Docker disponible y el repositorio clonado
- **WHEN** se ejecuta el comando de arranque documentado
- **THEN** los servicios de API, frontend y base de datos quedan disponibles

#### Scenario: Despliegue del Gateway

- **GIVEN** una instalación de la plataforma con Gateway central
- **WHEN** se consulta la documentación de despliegue
- **THEN** identifica el nodo designado y no presupone que comparta equipo con la plataforma

### Requirement: Gateway central obligatorio

El sistema SHALL incluir un Gateway central como componente obligatorio del
enlace entre los dispositivos y la plataforma, desplegado en una Mini PC x86 con
Windows 11 Pro, Docker Desktop y WSL2. La plataforma SHALL NOT asumir que el
Gateway y ella comparten el mismo equipo.

#### Scenario: Gateway presente

- **GIVEN** una plataforma desplegada conforme a este cambio
- **WHEN** se revisa la arquitectura y la documentación de despliegue
- **THEN** el Gateway central aparece como componente obligatorio

#### Scenario: Enlace con el Gateway

- **GIVEN** un Gateway desplegado en el nodo designado
- **WHEN** la plataforma se comunica con él
- **THEN** la comunicación se realiza mediante el canal MQTT definido en este cambio

### Requirement: Configuración por variables de entorno

El sistema SHALL obtener toda su configuración de variables de entorno, incluida
la correspondiente al enlace Gateway↔plataforma, y SHALL NOT contener credenciales
ni secretos en archivos versionados.

#### Scenario: Variable obligatoria ausente

- **GIVEN** una configuración a la que le falta una variable obligatoria
- **WHEN** se inicia el servicio correspondiente
- **THEN** el servicio falla al iniciar y emite un mensaje que identifica la variable faltante

#### Scenario: Repositorio sin secretos

- **GIVEN** el repositorio versionado
- **WHEN** se revisan los archivos de configuración incluidos
- **THEN** ninguno contiene contraseñas ni claves reales

#### Scenario: Configuración del enlace sin secretos

- **GIVEN** el enlace Gateway↔plataforma configurado
- **WHEN** se revisan los archivos versionados
- **THEN** no aparecen credenciales reales del canal MQTT

### Requirement: Persistencia en PostgreSQL

El sistema SHALL persistir los datos de la plataforma en PostgreSQL como fuente de
verdad, y SHALL conservarlos entre reinicios de los servicios.

#### Scenario: Persistencia tras reinicio

- **GIVEN** datos registrados en la plataforma
- **WHEN** se reinician los servicios de la API y de la base de datos
- **THEN** los datos siguen disponibles sin pérdida

### Requirement: API REST versionada

El sistema SHALL exponer sus operaciones mediante una API REST bajo un prefijo de
versión, y SHALL mantener documentadas las rutas vigentes.

#### Scenario: Consulta de la documentación de la API

- **GIVEN** la plataforma en ejecución
- **WHEN** se consulta la documentación de la API
- **THEN** refleja las rutas vigentes bajo el prefijo de versión

### Requirement: Canal WebSocket de telemetría

El sistema SHALL exponer un canal WebSocket autenticado destinado al envío de
telemetría hacia el frontend, y SHALL rechazar su apertura cuando no exista una
sesión válida. Este canal SHALL utilizarse entre la plataforma y el frontend; el
canal entre el Gateway y la plataforma SHALL ser MQTT.

#### Scenario: Apertura sin sesión válida

- **GIVEN** un cliente sin sesión autenticada
- **WHEN** intenta abrir el canal WebSocket
- **THEN** el sistema rechaza la conexión

#### Scenario: Apertura con sesión válida

- **GIVEN** un usuario autenticado con permiso de supervisión
- **WHEN** abre el canal WebSocket
- **THEN** el sistema acepta la conexión y la asocia a su sesión

### Requirement: Puerto de comunicación con dispositivos

El sistema SHALL acceder a los dispositivos exclusivamente a través de un puerto
de adaptador, y SHALL NOT contener lógica del dominio que dependa de un adaptador
concreto.

#### Scenario: Incorporación de un adaptador nuevo

- **GIVEN** un adaptador adicional que implementa el puerto
- **WHEN** se incorpora a la plataforma
- **THEN** el dominio opera sin cambios y el nuevo adaptador queda disponible por configuración

### Requirement: Sustitución de adaptador por configuración

El sistema SHALL permitir seleccionar el adaptador activo mediante configuración,
sin recompilar ni modificar el código del dominio.

#### Scenario: Cambio de adaptador configurado

- **GIVEN** una plataforma operando con un adaptador
- **WHEN** se modifica la configuración para usar otro adaptador y se reinicia el servicio
- **THEN** la plataforma opera con el adaptador recién configurado

### Requirement: Canal MQTT Gateway-plataforma

El sistema SHALL utilizar MQTT como canal obligatorio de comunicación entre el
Gateway y la plataforma, implementado como adaptador detrás del puerto de
comunicación con dispositivos. El dominio SHALL NOT depender del protocolo MQTT
ni de un producto broker concreto.

#### Scenario: Recepción desde el Gateway

- **GIVEN** un Gateway desplegado y un adaptador MQTT configurado
- **WHEN** el Gateway envía un mensaje conforme al Envelope
- **THEN** el adaptador lo entrega al puerto de dispositivo sin modificar el dominio

#### Scenario: Sustitución del adaptador

- **GIVEN** un caso de prueba del dominio
- **WHEN** se ejecuta con el adaptador MQTT o con el adaptador simulado
- **THEN** el resultado del dominio es el mismo y no referencia el protocolo

Nota: el producto broker, los tópicos, la QoS y la retención no se fijan en este
cambio y permanecen pendientes de autorización.

### Requirement: Estructura común de mensajes (Envelope EP1)

El sistema SHALL usar la estructura común de mensajes JSON definida por la
decisión EP1 (Envelope) para todo mensaje intercambiado entre el Gateway y la
plataforma, incluidos los mensajes del dispositivo simulado. Los campos concretos
del Envelope SHALL permanecer pendientes de autorización y SHALL NOT fijarse en
este cambio.

#### Scenario: Mensaje conforme al Envelope

- **GIVEN** un mensaje enviado por el Gateway a la plataforma
- **WHEN** el adaptador MQTT lo entrega al dominio
- **THEN** el mensaje utiliza la estructura Envelope autorizada

#### Scenario: Origen simulado

- **GIVEN** un dispositivo simulado habilitado sin hardware FPGA
- **WHEN** emite un mensaje de estado o telemetría
- **THEN** el mensaje utiliza la misma estructura Envelope que el enlace real

### Requirement: Redis no obligatorio

El sistema SHALL NOT requerir Redis para operar con un único proceso de API.

#### Scenario: Despliegue sin Redis

- **GIVEN** una configuración de despliegue sin servicio de Redis
- **WHEN** se inicia la plataforma con un único proceso de API
- **THEN** la plataforma opera y el canal WebSocket entrega telemetría a sus clientes

### Requirement: Separación entre control y supervisión

El sistema SHALL NOT establecer ningún camino de datos que permita a la plataforma
influir en el lazo de control determinista, que se ejecuta en la FPGA. Los
comandos emitidos por la plataforma SHALL limitarse a supervisión y configuración.

#### Scenario: Revisión de la arquitectura

- **GIVEN** la arquitectura documentada y desplegada
- **WHEN** se revisan las dependencias entre persistencia, API y borde de planta
- **THEN** no existe ninguna conexión desde la plataforma hacia el lazo de control

#### Scenario: Comando de supervisión

- **GIVEN** un comando emitido por la plataforma hacia un dispositivo
- **WHEN** se inspecciona su camino de datos
- **THEN** no altera el lazo de control determinista de la FPGA

### Requirement: Contratos de telemetría, eventos, comandos e historial

El sistema SHALL definir sobre el Envelope y el puerto de dispositivo los
contratos de mensajes de telemetría, eventos, comandos e historial, y SHALL prever
su persistencia. La implementación funcional completa de estos módulos SHALL
corresponder al cambio posterior `add-practice-lifecycle` y SHALL NOT adelantarse
en este cambio. La política de retención del historial SHALL permanecer pendiente
de autorización.

#### Scenario: Contratos disponibles sin módulo funcional

- **GIVEN** las especificaciones de este cambio
- **WHEN** se revisan los contratos de mensajería
- **THEN** telemetría, eventos, comandos e historial están descritos sobre el Envelope sin definir su funcionalidad completa

#### Scenario: Persistencia prevista

- **GIVEN** un evento de dispositivo recibido por el adaptador MQTT
- **WHEN** se registra en la plataforma
- **THEN** queda disponible para consulta histórica sin fijar una política de retención

### Requirement: Verificación de salud de los servicios

El sistema SHALL exponer un punto de verificación de salud que distinga la
disponibilidad de la API, de la base de datos y del canal Gateway↔plataforma.

#### Scenario: Base de datos no disponible

- **GIVEN** la API en ejecución
- **WHEN** la base de datos deja de responder
- **THEN** el punto de salud reporta el servicio como degradado e identifica la dependencia afectada

#### Scenario: Canal MQTT no disponible

- **GIVEN** la API y la base de datos disponibles
- **WHEN** el canal Gateway↔plataforma deja de responder
- **THEN** el punto de salud reporta degradación e identifica el canal afectado

### Requirement: Registro estructurado de eventos

El sistema SHALL registrar eventos y errores de forma estructurada, incluyendo
nivel, contexto e instante del servidor.

#### Scenario: Error registrado

- **GIVEN** la plataforma en ejecución
- **WHEN** se produce un error en una operación
- **THEN** queda un registro consultable con nivel, contexto e instante del servidor
