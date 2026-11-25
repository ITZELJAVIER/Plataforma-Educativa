# Tasks

## 1. Estructura del repositorio y orquestación

- [x] 1.1 Crear la estructura de carpetas de backend, frontend e infraestructura, incluida la ubicación del adaptador MQTT, y verificar que coincide con la documentada en `design.md`
- [ ] 1.2 Crear el archivo de Docker Compose con los servicios de API, frontend y base de datos, documentar el despliegue del Gateway en el nodo designado, y verificar que `docker compose config` valida la orquestación sin errores y que la documentación no asume co-ubicación
- [ ] 1.3 Crear el archivo de variables de entorno de ejemplo, incluidos los parámetros del enlace MQTT sin fijar broker, tópicos ni credenciales, y verificar que no contiene credenciales reales
- [ ] 1.4 Documentar los prerrequisitos de arranque (Docker con WSL2 en Windows y Docker Desktop en el nodo Gateway) y verificar que un equipo limpio puede levantar los servicios siguiendo solo esa documentación, sin asumir que Gateway y plataforma comparten equipo
- [ ] 1.5 Configurar el análisis estático y el formato del backend, y verificar que se ejecutan sin hallazgos

## 2. Persistencia y modelo de datos

- [ ] 2.1 Definir el esquema inicial de usuarios, roles, dispositivos, perfiles de hardware, periféricos, auditoría y las estructuras de historial previstas por los contratos de telemetría, eventos y comandos, sin implementar sus módulos funcionales, y verificar que las migraciones se aplican sobre una base vacía
- [ ] 2.2 Implementar los puertos de repositorio del dominio y verificar que las pruebas se ejecutan con implementaciones en memoria
- [ ] 2.3 Verificar que los datos persisten tras reiniciar los servicios de API y base de datos
- [ ] 2.4 Documentar el modelo de datos y verificar que sus entidades y contratos de historial coinciden con los de `design.md`

## 3. Identidad y autorización

- [x] 3.1 Implementar el almacenamiento de contraseñas con hash y sal individual, y verificar que ninguna contraseña se guarda ni se registra en claro
- [x] 3.2 Implementar el inicio y el cierre de sesión, y verificar los escenarios de credenciales válidas, credenciales inválidas y cuenta desactivada
- [x] 3.3 Implementar la expiración y la invalidación de sesiones, y verificar el rechazo de una credencial vencida o cerrada
- [x] 3.4 Implementar la autorización por rol con denegación por defecto, y verificar la matriz de permisos de administrador, docente y estudiante
- [x] 3.5 Escribir las pruebas de los escenarios de `user-auth` y verificar que todas pasan

## 4. Administración de usuarios y auditoría

- [x] 4.1 Implementar las operaciones de administración de usuarios y verificar que la desactivación invalida las sesiones activas
- [x] 4.2 Validar la asignación de exactamente un rol y verificar el rechazo de usuarios sin rol
- [x] 4.3 Implementar el registro de auditoría de eventos de seguridad y verificar que un inicio de sesión, un fallo y un cambio de rol generan registros con actor, recurso e instante
- [x] 4.4 Documentar las operaciones de administración de usuarios y verificar que la documentación coincide con las rutas implementadas

## 5. Catálogo de periféricos

- [x] 5.1 Implementar los siete tipos base de periférico y verificar que la consulta del catálogo los devuelve
- [x] 5.2 Implementar la validación de metadatos y verificar el rechazo de un periférico sin tipo y de un sensor sin unidad, rango o resolución
- [x] 5.3 Implementar la validación de valores contra rango y resolución, y verificar los escenarios de valor fuera de rango y valor incompatible con la resolución
- [x] 5.4 Implementar la unicidad de canales por periférico y verificar el rechazo de canales duplicados
- [x] 5.5 Verificar que un tipo de periférico nuevo se registra y se expone a la interfaz sin modificar el frontend
- [x] 5.6 Escribir las pruebas de los escenarios de `peripheral-catalog` y verificar que todas pasan
- [x] 5.7 Documentar el esquema de metadatos de periférico y verificar que cubre los siete tipos base

## 6. Gestión de dispositivos

- [x] 6.1 Implementar el registro de dispositivos y verificar el rechazo de un identificador duplicado
- [x] 6.2 Verificar que el identificador de un dispositivo registrado no puede modificarse
- [x] 6.3 Implementar la exposición del estado de conexión derivado del adaptador activo, incluido el adaptador MQTT, y verificar los estados conectado, desconectado y desconocido
- [x] 6.4 Implementar la configuración lógica y el registro de eventos de cambio de estado, y verificar que cada transición deja un evento con estado anterior, estado nuevo e instante conforme al contrato de eventos del Envelope
- [x] 6.5 Implementar la desactivación de dispositivos y verificar que impide el uso operativo sin eliminar el registro
- [x] 6.6 Verificar que la administración de dispositivos está restringida al administrador y que docente y estudiante acceden solo en lectura según su alcance
- [x] 6.7 Escribir las pruebas de los escenarios de `device-management` y verificar que todas pasan
- [x] 6.8 Documentar la administración de dispositivos y verificar que la documentación describe el ciclo de registro, configuración y desactivación

## 7. Puerto de dispositivo y adaptadores

- [ ] 7.1 Definir el contrato del puerto de comunicación con dispositivos en términos del Envelope EP1 y verificar que el dominio no depende de ningún adaptador concreto ni del protocolo MQTT
- [ ] 7.2 Implementar el adaptador simulado conforme al Envelope y verificar que un dispositivo simulado se registra, aparece conectado y reporta datos de prueba sin hardware FPGA
- [ ] 7.3 Implementar el adaptador MQTT como implementación del puerto y su selección por configuración, y verificar que el cambio de adaptador surte efecto al reiniciar el servicio sin acoplar el dominio al protocolo
- [ ] 7.4 Escribir las pruebas de contrato del puerto y verificar que se ejecutan contra el adaptador simulado y contra el adaptador MQTT con el mismo resultado
- [ ] 7.5 Documentar cómo incorporar un adaptador nuevo, incluidos el simulado y el MQTT, y verificar que el procedimiento no requiere cambios en el dominio

## 8. API, canales y servicios transversales

- [ ] 8.1 Exponer la API REST bajo un prefijo de versión y verificar que la documentación generada refleja las rutas vigentes
- [ ] 8.2 Implementar el canal WebSocket autenticado entre la plataforma y el frontend y verificar el rechazo de conexiones sin sesión válida y la aceptación con sesión válida
- [ ] 8.3 Implementar el punto de verificación de salud y verificar que reporta degradación cuando la base de datos no responde o cuando el canal Gateway↔plataforma no está disponible, identificando la dependencia afectada
- [ ] 8.4 Implementar el registro estructurado de eventos y errores, y verificar que un error produce un registro con nivel, contexto e instante
- [ ] 8.5 Verificar que la plataforma opera sin Redis, sin hardware FPGA y con el dispositivo simulado sobre el canal MQTT, comprobando que el funcionamiento no depende de un producto broker ni de tópicos concretos
- [ ] 8.6 Documentar la configuración por variables de entorno, incluidos los parámetros del enlace MQTT, y verificar que el arranque falla con mensaje explícito cuando falta una variable obligatoria
- [ ] 8.7 Verificar que los contratos de telemetría, eventos, comandos e historial están descritos sobre el Envelope y que su implementación funcional no se adelanta al cambio `add-practice-lifecycle`

## 9. Integración y verificación final

- [ ] 9.1 Verificar el arranque completo desde un entorno limpio con el comando documentado, incluido el enlace MQTT con el Gateway y el dispositivo simulado, sin asumir co-ubicación
- [ ] 9.2 Ejecutar la suite completa de pruebas y verificar que pasa en su totalidad
- [ ] 9.3 Verificar por revisión de dependencias que no existe ningún camino de datos desde la plataforma, incluidos los comandos de supervisión, hacia el lazo de control determinista de la FPGA
- [ ] 9.4 Verificar que ninguna especificación del cambio depende del enlace físico FPGA↔Gateway, del protocolo físico, de los niveles eléctricos, de las frecuencias de adquisición, del producto broker, de los tópicos, de la QoS, de la retención, de los campos completos del Envelope, de la ubicación del simulador ni de la topología definitiva, y que estas decisiones permanecen identificadas como pendientes
- [ ] 9.5 Ejecutar `openspec validate add-platform-foundation --strict` y verificar que el cambio resulta válido

## Workflow follow-up

- Revisar los artefactos antes de iniciar la implementación.
- Iniciar el flujo de aplicación solo tras la aprobación de la revisión.
- Archivar el cambio cuando la implementación esté verificada y revisada.
