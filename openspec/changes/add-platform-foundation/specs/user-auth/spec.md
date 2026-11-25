# Spec Delta

## Purpose

Define cómo la plataforma identifica a los usuarios, controla su acceso a los
recursos y administra las cuentas y roles de administrador, docente y estudiante.

## ADDED Requirements

### Requirement: Inicio de sesión con credenciales

El sistema SHALL permitir a un usuario activo iniciar sesión presentando
credenciales válidas, y SHALL rechazar el intento cuando las credenciales no sean
válidas o la cuenta esté desactivada. El rechazo SHALL NOT revelar si la cuenta
existe.

#### Scenario: Inicio de sesión correcto

- **GIVEN** un usuario activo con credenciales registradas
- **WHEN** el usuario presenta credenciales válidas
- **THEN** el sistema establece una sesión autenticada y registra el acceso en la auditoría

#### Scenario: Credenciales inválidas

- **GIVEN** un usuario registrado
- **WHEN** el usuario presenta una contraseña incorrecta
- **THEN** el sistema rechaza el intento con un mensaje genérico y registra el fallo

#### Scenario: Cuenta desactivada

- **GIVEN** un usuario desactivado por el administrador
- **WHEN** el usuario presenta credenciales correctas
- **THEN** el sistema rechaza el intento con el mismo mensaje genérico

### Requirement: Cierre de sesión

El sistema SHALL permitir cerrar la sesión activa y SHALL invalidar la credencial
de sesión de modo que no pueda reutilizarse después del cierre.

#### Scenario: Cierre de sesión efectivo

- **GIVEN** un usuario con sesión activa
- **WHEN** el usuario solicita cerrar sesión
- **THEN** la sesión queda invalidada y las peticiones posteriores con esa credencial se rechazan

### Requirement: Protección de credenciales

El sistema SHALL almacenar las contraseñas exclusivamente como hash con sal
individual, y SHALL NOT exponer la contraseña ni su hash en respuestas de la API,
registros ni artefactos de configuración.

#### Scenario: Respuesta de usuario sin datos sensibles

- **GIVEN** un usuario registrado
- **WHEN** se consulta la información del usuario a través de la API
- **THEN** la respuesta no incluye la contraseña ni el hash almacenado

#### Scenario: Registro sin secretos

- **GIVEN** un inicio de sesión procesado
- **WHEN** se revisa el registro del evento
- **THEN** el registro no contiene la contraseña presentada

### Requirement: Expiración de sesión

El sistema SHALL expirar las sesiones autenticadas transcurrido el periodo
configurado y SHALL exigir una nueva autenticación después de la expiración.

#### Scenario: Uso de credencial expirada

- **GIVEN** una sesión cuya vigencia ha expirado
- **WHEN** se presenta la credencial de esa sesión
- **THEN** el sistema rechaza la petición con un error de autenticación

### Requirement: Administración de usuarios

El administrador SHALL poder crear, consultar, modificar, desactivar y reactivar
usuarios. Al desactivar una cuenta, el sistema SHALL invalidar sus sesiones
activas.

#### Scenario: Creación de usuario

- **GIVEN** un administrador autenticado
- **WHEN** crea un usuario con datos válidos y un rol asignado
- **THEN** el usuario queda registrado y puede iniciar sesión si está activo

#### Scenario: Desactivación de usuario

- **GIVEN** un usuario con sesión activa
- **WHEN** el administrador desactiva la cuenta
- **THEN** el usuario no puede iniciar sesión y su sesión activa queda invalidada

### Requirement: Asignación única de rol

El sistema SHALL asignar exactamente un rol de los tres definidos a cada usuario
activo, y SHALL rechazar la creación o modificación de un usuario sin rol o con
más de uno.

#### Scenario: Usuario sin rol

- **GIVEN** un administrador autenticado
- **WHEN** intenta crear un usuario sin rol
- **THEN** el sistema rechaza la operación indicando que el rol es obligatorio

#### Scenario: Cambio de rol auditado

- **GIVEN** un usuario con rol de estudiante
- **WHEN** el administrador le asigna el rol de docente
- **THEN** el nuevo rol se aplica y el cambio queda registrado en la auditoría

### Requirement: Denegación por defecto

El sistema SHALL denegar toda operación que no esté explícitamente permitida para
el rol del usuario autenticado, y SHALL rechazar las peticiones sin sesión válida.

#### Scenario: Operación no permitida

- **GIVEN** un estudiante autenticado
- **WHEN** invoca una operación reservada al administrador
- **THEN** el sistema responde con un error de autorización y no ejecuta la operación

#### Scenario: Petición sin sesión

- **GIVEN** un cliente sin sesión válida
- **WHEN** invoca un recurso protegido
- **THEN** el sistema rechaza la petición con un error de autenticación

### Requirement: Alcance de acceso por rol

El sistema SHALL limitar el acceso a los recursos según el rol: el administrador
gestiona todos los recursos, el docente consulta los recursos que le correspondan
y el estudiante accede únicamente a los propios.

#### Scenario: Docente en modo lectura

- **GIVEN** un docente autenticado
- **WHEN** consulta el catálogo de dispositivos
- **THEN** el sistema devuelve la información en modo lectura

#### Scenario: Estudiante intenta administrar

- **GIVEN** un estudiante autenticado
- **WHEN** intenta registrar un dispositivo
- **THEN** el sistema rechaza la operación por falta de permisos

### Requirement: Auditoría de eventos de seguridad

El sistema SHALL registrar en auditoría los inicios de sesión, los cierres, los
fallos de autenticación y los cambios de rol o de estado de usuario, incluyendo
actor, acción, recurso afectado e instante del servidor.

#### Scenario: Registro de cambio de estado

- **GIVEN** un administrador autenticado
- **WHEN** desactiva la cuenta de un usuario
- **THEN** se crea un registro de auditoría con actor, acción, cuenta afectada e instante
