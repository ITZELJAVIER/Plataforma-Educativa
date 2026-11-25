# Gateway central — despliegue independiente

Documento conceptual de la tarea 1.2 del cambio `add-platform-foundation`.
Describe la posición del Gateway central en la arquitectura; **no constituye una
implementación ni un procedimiento ejecutable**. Las decisiones que siguen
pendientes de autorización se identifican explícitamente.

## 1. Decisión autorizada

El Gateway central es un componente **obligatorio** del enlace entre los
dispositivos y la plataforma (decisiones D11 y D12 de `design.md`). No es opcional
y no se considera un detalle de despliegue de la plataforma.

## 2. Nodo designado

| Aspecto | Valor autorizado |
|---|---|
| Equipo | Mini PC x86 |
| Sistema operativo | Windows 11 Pro |
| Contenedores | Docker Desktop |
| Subsistema Linux | WSL2 |

Estos valores son decisiones autorizadas previamente. No se especifica dirección
IP, nombre de host, capacidad de hardware ni ubicación física: la topología
definitiva sigue pendiente de autorización.

## 3. Responsabilidades del Gateway

- Actuar como único punto central de enlace entre los dispositivos de planta y la
  plataforma.
- Recibir la información de la FPGA y de los dispositivos y entregarla a la
  plataforma mediante el canal autorizado.
- Publicar mensajes conformes al contrato común de mensajes (Envelope EP1).
- Aceptar únicamente comandos de **supervisión y configuración**; no ejecutar ni
  participar en el lazo de control determinista.
- Proveer la separación entre el borde de planta y los servicios de la plataforma,
  de modo que el dominio de la plataforma no dependa del transporte ni del hardware.

No se fija aquí la implementación interna del Gateway ni su stack de procesos.

## 4. Comunicación Gateway ↔ plataforma

- **MQTT es obligatorio** entre el Gateway y la plataforma (D7 y D12).
- WebSocket queda reservado exclusivamente para la comunicación
  plataforma ↔ frontend; no se utiliza para el enlace Gateway ↔ plataforma.
- El adaptador MQTT reside en la plataforma, detrás del puerto de comunicación con
  dispositivos (`backend/src/adapters/outbound/device/mqtt/`), de acuerdo con D1 y
  D12. El dominio no referencia MQTT, producto broker, tópicos, QoS ni retención.
- **Pendiente de autorización:** producto o broker MQTT, nombres de tópicos, QoS,
  retención de mensajes, mecanismo de autenticación y TLS del enlace. Ninguno de
  estos valores se selecciona en este documento.

## 5. Relación con la FPGA Sipeed Tang Nano 9K

- La placa objetivo declarada es Sipeed Tang Nano 9K (FPGA Gowin GW1NR-9).
- El enlace físico entre la FPGA y el Gateway, su protocolo, sus niveles eléctricos
  y la frecuencia de adquisición **no están decididos** y permanecen pendientes de
  autorización.
- El catálogo de periféricos es descriptivo y no depende de ese enlace físico.

## 6. Restricción del lazo determinista

- El lazo de control determinista se ejecuta en la FPGA.
- La plataforma **no participa** en ese lazo: no hay camino de datos desde la
  plataforma, incluidos los comandos, hacia el lazo de control.
- Los comandos que emita la plataforma se limitan a supervisión y configuración.
- Esta restricción se aplica también al Gateway: su función es de enlace y
  supervisión, no de control en tiempo real.

## 7. Contrato común de mensajes

- Todo mensaje entre el Gateway y la plataforma utiliza la estructura común JSON
  definida por la decisión EP1 (Envelope), incluidos los mensajes del dispositivo
  simulado (D13 y D14).
- **Pendiente de autorización:** los campos completos del Envelope. Este documento
  no define esquema, campos, tipos ni formatos concretos.

## 8. Separación de despliegues

- El Gateway y la plataforma se despliegan de forma independiente.
- **No se asume que compartan equipo**, sistema operativo, entorno de contenedores
  ni red. La conectividad entre ambos extremos se definirá cuando se autorice la
  topología definitiva.
- El Gateway **no** se incluye en `infrastructure/compose/compose.yaml`; ese archivo
  orquesta únicamente los servicios de la plataforma (backend, frontend y base de
  datos).
- **Pendiente de autorización:** topología definitiva de despliegue y ubicación de
  ejecución del dispositivo simulador.

## 9. Variables de configuración a definir posteriormente

Los siguientes parámetros deberán definirse en su momento, sin valores concretos en
este documento:

| Parámetro | Estado |
|---|---|
| Identificador del Gateway | Pendiente de definición |
| Parámetros de conexión del enlace MQTT (host, puerto y credenciales) | Pendientes de autorización; la tarea 1.3 definirá la forma de configuración sin valores reales |
| Tópicos utilizados por el enlace | Pendientes de autorización |
| QoS y retención de mensajes | Pendientes de autorización |
| Mecanismo de autenticación y TLS del enlace MQTT | Pendiente de autorización |
| Campos completos del Envelope EP1 | Pendientes de autorización |
| Enlace físico, niveles eléctricos y frecuencias FPGA ↔ Gateway | Pendientes de autorización |
| Topología definitiva y ubicación del simulador | Pendientes de autorización |

No se incorporan credenciales reales ni valores de ejemplo que puedan interpretarse
como decisiones.

## 10. Procedimiento conceptual de despliegue independiente

1. Aprovisionar la Mini PC x86 con Windows 11 Pro.
2. Instalar y verificar Docker Desktop con WSL2 en ese nodo, sin suponer que la
   plataforma se ejecutará allí.
3. Desplegar el componente Gateway de forma separada de la orquestación de la
   plataforma.
4. Definir, previa autorización, los parámetros de la sección 9.
5. Verificar que el enlace MQTT entre el Gateway y la plataforma queda establecido
   con el contrato Envelope, sin fijar broker, tópicos, QoS ni retención en esta
   documentación.
6. Verificar que no existe camino de datos desde la plataforma hacia el lazo de
   control de la FPGA.

Este procedimiento es conceptual: no se ha ejecutado y no debe interpretarse como
un despliegue validado.

## 11. Resumen de decisiones

| Decisiones autorizadas | Decisiones pendientes |
|---|---|
| Gateway central obligatorio | Producto o broker MQTT |
| Mini PC x86, Windows 11 Pro, Docker Desktop y WSL2 | Nombres de tópicos, QoS y retención |
| MQTT obligatorio Gateway ↔ plataforma | Autenticación y TLS del enlace MQTT |
| WebSocket solo plataforma ↔ frontend | Enlace físico FPGA ↔ Gateway |
| Envelope EP1 como estructura común | Niveles eléctricos y frecuencias |
| FPGA Tang Nano 9K fuera del lazo de la plataforma | Campos completos del Envelope |
| Comandos solo de supervisión y configuración | Topología definitiva y ubicación del simulador |
| Despliegue independiente, sin co-ubicación asumida | Configuración concreta del Gateway |

## 12. Dependencias con otras tareas

- Tarea 1.3: archivo de variables de entorno de ejemplo, sin credenciales ni broker
  fijado.
- Tareas 7.1–7.4: contrato del puerto, adaptador simulado y adaptador MQTT.
- Tarea 8.3: punto de salud que distinga API, base de datos y canal
  Gateway ↔ plataforma.
- Tarea 9.1: verificación final del arranque y del enlace, sin co-ubicación asumida.
- Dockerfiles de API y frontend creados en la tarea 1.2: requieren manifiestos y
  código de aplicación de tareas posteriores; su construcción no ha sido verificada.

## 13. Estado de los artefactos de la tarea 1.2

- `infrastructure/compose/compose.yaml` declara únicamente los servicios de la
  plataforma: API, frontend y base de datos. El Gateway no aparece en esa
  orquestación y se mantiene como despliegue independiente.
- Los Dockerfiles de `backend/` y `frontend/` describen la tecnología autorizada
  (FastAPI y React + TypeScript + Vite), pero todavía no pueden producir imágenes
  funcionales porque no existen los manifiestos y el código de aplicación.
- El comando previsto para la plataforma, cuando esos archivos existan, es
  `docker compose -f infrastructure/compose/compose.yaml up --build`. No se ha
  ejecutado y no debe interpretarse como un arranque validado.
- No se ha marcado la tarea 1.2 como completada: falta la verificación real con
  `docker compose config` en un entorno con Docker disponible.
