# Spec Delta

## Purpose

Define el registro, la configuración lógica, el estado de conexión y la
administración de los dispositivos que la plataforma supervisa, sin fijar el
enlace físico ni el protocolo de comunicación entre la FPGA y el Gateway.

## ADDED Requirements

### Requirement: Registro de dispositivos

El sistema SHALL permitir registrar un dispositivo con identificador único,
nombre, tipo y perfil de hardware, y SHALL rechazar el registro cuando el
identificador ya exista.

#### Scenario: Registro válido

- **GIVEN** un administrador autenticado
- **WHEN** registra un dispositivo con un identificador no utilizado y datos válidos
- **THEN** el dispositivo queda disponible para consulta en el catálogo

#### Scenario: Identificador duplicado

- **GIVEN** un dispositivo ya registrado
- **WHEN** se intenta registrar otro dispositivo con el mismo identificador
- **THEN** el sistema rechaza la operación indicando que el identificador ya existe

### Requirement: Identificador inmutable

El sistema SHALL tratar el identificador de un dispositivo registrado como
inmutable y SHALL rechazar cualquier intento de modificarlo.

#### Scenario: Intento de cambio de identificador

- **GIVEN** un dispositivo registrado
- **WHEN** el administrador intenta modificar su identificador
- **THEN** el sistema rechaza la modificación y conserva el identificador original

### Requirement: Estado de conexión observable

El sistema SHALL exponer el estado de conexión de cada dispositivo como
conectado, desconectado o desconocido, derivado de la información reportada por
el adaptador activo.

#### Scenario: Estado reportado por el adaptador

- **GIVEN** un dispositivo con adaptador activo
- **WHEN** el adaptador informa que la comunicación se estableció
- **THEN** el sistema expone el dispositivo como conectado

#### Scenario: Estado sin información

- **GIVEN** un dispositivo registrado que nunca ha reportado información
- **WHEN** se consulta su estado
- **THEN** el sistema lo expone como desconocido

### Requirement: Configuración lógica del dispositivo

El sistema SHALL permitir modificar el nombre, la ubicación, el tipo, el perfil de
hardware y el estado de habilitación de un dispositivo, sin requerir cambios en el
enlace físico.

#### Scenario: Actualización de configuración lógica

- **GIVEN** un dispositivo registrado
- **WHEN** el administrador actualiza su ubicación
- **THEN** la nueva configuración se persiste y el cambio queda registrado

### Requirement: Selección de adaptador por configuración

El sistema SHALL determinar el adaptador de comunicación de cada dispositivo
mediante configuración, y SHALL NOT requerir cambios en la lógica del dominio para
sustituirlo. El adaptador MQTT, que implementa el puerto sobre el canal
Gateway↔plataforma, SHALL ser una de las implementaciones seleccionables.

#### Scenario: Sustitución de adaptador

- **GIVEN** un dispositivo configurado con un adaptador
- **WHEN** el administrador cambia el adaptador configurado y se restablece la conexión
- **THEN** el dispositivo opera con el nuevo adaptador sin cambios en el dominio

#### Scenario: Selección del adaptador MQTT

- **GIVEN** un dispositivo configurado con el adaptador simulado
- **WHEN** se cambia el adaptador configurado a MQTT y se reinicia el servicio
- **THEN** el dispositivo opera con el nuevo adaptador sin cambios en el dominio

Nota: el producto broker y los tópicos no se fijan en este cambio y permanecen
pendientes de autorización.

### Requirement: Dispositivo simulado

El sistema SHALL proveer un dispositivo simulado registrable como cualquier otro,
que reporte estado de conexión y datos de prueba sin requerir hardware físico, y
SHALL emitir y consumir mensajes conformes al Envelope EP1 a través del mismo
puerto de dispositivo que el adaptador real.

#### Scenario: Operación sin hardware

- **GIVEN** la plataforma desplegada sin hardware conectado
- **WHEN** se registra y habilita el dispositivo simulado
- **THEN** el dispositivo aparece conectado y reporta datos de prueba mediante mensajes conformes al Envelope

#### Scenario: Conformidad con el Envelope

- **GIVEN** un dispositivo simulado registrado y habilitado
- **WHEN** emite un mensaje de estado
- **THEN** el mensaje utiliza la estructura común Envelope definida para el canal Gateway↔plataforma

Nota: la ubicación de ejecución del simulador queda pendiente de autorización.

### Requirement: Desactivación sin pérdida de historial

El sistema SHALL permitir desactivar un dispositivo, impidiendo su uso operativo
y conservando su registro para consulta histórica.

#### Scenario: Desactivación de dispositivo

- **GIVEN** un dispositivo registrado
- **WHEN** el administrador lo desactiva
- **THEN** no se establece comunicación con él y su registro permanece consultable

### Requirement: Eventos de cambio de estado

El sistema SHALL registrar cada cambio de estado de conexión con el estado
anterior, el estado nuevo y el instante del servidor.

#### Scenario: Transición de estado

- **GIVEN** un dispositivo conectado
- **WHEN** el adaptador informa la pérdida de comunicación
- **THEN** se registra un evento con el estado anterior, el nuevo estado y el instante

### Requirement: Permisos de administración de dispositivos

El sistema SHALL restringir el registro, la modificación, la desactivación y el
cambio de adaptador al rol administrador, y SHALL permitir la consulta en modo
lectura a los roles docente y estudiante según su alcance.

#### Scenario: Docente consulta dispositivos

- **GIVEN** un docente autenticado
- **WHEN** consulta el catálogo de dispositivos
- **THEN** obtiene la información en modo lectura sin poder modificarla
