# Plataforma Educativa IoT

[![CI](https://github.com/ITZELJAVIER/Plataforma-Educativa/actions/workflows/ci.yml/badge.svg)](https://github.com/ITZELJAVIER/Plataforma-Educativa/actions/workflows/ci.yml)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)
![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.165-009485?logo=fastapi&logoColor=white)
![React 19](https://img.shields.io/badge/React-19.3-61DAFB?logo=react&logoColor=black)
![Vite 8](https://img.shields.io/badge/Vite-8.3-646CFF?logo=vite&logoColor=white)
![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)

Plataforma web para la gestión de prácticas educativas de control y periféricos.
Expone una API REST versionada, una interfaz web por roles y un canal de enlace
con dispositivos (adaptador simulado y adaptador MQTT) detrás de un puerto de
comunicación independiente del protocolo.

> **Estado del proyecto:** base funcional en desarrollo. La autenticación, la
> administración de usuarios, el catálogo de periféricos y la gestión de
> dispositivos están implementados y probados. La orquestación Docker, el canal
> WebSocket, el endpoint de salud y el enlace completo con el Gateway siguen en
> el cambio OpenSpec `add-platform-foundation` (ver [estado](#-estado-del-cambio-openspec)).
> Docker no estaba disponible en el entorno de desarrollo, por lo que los
> despliegues con contenedores **no han sido validados aquí**.

## Tabla de contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Stack tecnológico](#-stack-tecnológico)
- [Descarga](#-descarga)
- [Puesta en marcha](#-puesta-en-marcha)
- [Configuración](#-configuración)
- [Roles y permisos](#-roles-y-permisos)
- [API REST](#-api-rest)
- [Pruebas y calidad](#-pruebas-y-calidad)
- [Docker](#-docker)
- [Despliegue](#-despliegue)
- [Estado del cambio OpenSpec](#-estado-del-cambio-openspec)
- [Contribuir](#-contribuir)
- [Licencia y autoría](#-licencia-y-autoría)

## ✨ Características

- **Identidad y acceso:** inicio/cierre de sesión con tokens, expiración e
  invalidación de sesiones y hash de contraseñas con sal individual (PBKDF2).
- **Autorización por rol:** administrador, docente y estudiante, con denegación
  por defecto y trazabilidad de eventos de seguridad.
- **Administración de usuarios:** alta, consulta, cambio de rol, desactivación y
  reactivación; la desactivación invalida las sesiones activas.
- **Catálogo de periféricos:** siete tipos base, metadatos de capacidad y
  validación de valores contra rango y resolución. Extensible sin tocar el
  frontend.
- **Gestión de dispositivos:** registro, configuración lógica, estado de conexión
  derivado del adaptador, eventos de cambio de estado y desactivación sin borrar
  el registro.
- **Adaptadores desacoplados:** el dominio define puertos; las implementaciones
  concretas son el dispositivo simulado y el adaptador MQTT, seleccionables por
  configuración.
- **Contrato común de mensajes:** estructura JSON *Envelope* (EP1) para el
  intercambio Gateway ↔ plataforma, incluido el dispositivo simulado.
- **Interfaz web:** panel, dispositivos, catálogo, usuarios, perfil,
  configuración y monitoreo, con tema claro/oscuro y navegación según rol.
- **Infraestructura:** PostgreSQL 16, Docker Compose y reverse proxy Caddy con
  HTTPS automático para el despliegue de prueba.

## 🏗️ Arquitectura

El backend sigue **arquitectura hexagonal (puertos y adaptadores)**: las reglas
de negocio viven en `domain/` y `application/`, mientras que FastAPI, PostgreSQL,
MQTT y la seguridad son adaptadores de entrada/salida. El dominio no conoce
protocolos, bases de datos ni hardware.

```text
Navegador ──HTTPS──> Caddy ──> Frontend (React/Vite :5173)
                          └──> API (FastAPI :8000) ──> PostgreSQL 16
                                      │
                                      ├── WebSocket (previsto) ──> Frontend
                                      └── Puerto de dispositivos
                                             ├── Adaptador simulado
                                             └── Adaptador MQTT ──> Gateway (independiente)
                                                                       │
                                                              FPGA Tang Nano 9K
```

**Invariante:** el lazo de control determinista se ejecuta en la FPGA. La
plataforma y el Gateway solo realizan supervisión y configuración; no existe
camino de datos hacia el lazo de control.

### Estructura del repositorio

```text
Plataforma-Educativa/
├── backend/                  API FastAPI (arquitectura hexagonal)
│   ├── docs/                 Documentación de capacidades
│   ├── src/
│   │   ├── domain/           Entidades, objetos de valor y puertos
│   │   ├── application/      Casos de uso y errores de aplicación
│   │   ├── adapters/         REST, persistencia, seguridad y dispositivos
│   │   └── infrastructure/   Bootstrap, configuración y logging
│   └── tests/                Unitarias, integración y contratos
├── frontend/                 React + TypeScript + Vite
│   ├── src/app/              Arranque, tema y navegación
│   ├── src/components/       Componentes reutilizables
│   ├── src/features/         Vistas (auth, dashboard, devices, ...)
│   ├── src/services/         Cliente de la API
│   └── tests/                Pruebas de UI y presentación
├── infrastructure/
│   ├── compose/              Compose de desarrollo y de producción + Caddyfile
│   ├── gateway/              Documentación del Gateway independiente
│   └── deploy.sh             Despliegue de prueba en Linux + Docker
├── openspec/                 Propuestas, diseño, specs y tareas
├── .github/                  CI, plantillas de issues y PR
├── .env.example              Plantilla de variables (sin secretos reales)
├── plataforma.bat            Gestor de servicios de desarrollo en Windows
└── DEPLOY.md                 Guía de despliegue y solución de problemas
```

## 🧰 Stack tecnológico

| Capa | Tecnología | Versión |
| --- | --- | --- |
| API | FastAPI + Uvicorn | 0.165.0 / 0.54.0 |
| Base de datos | PostgreSQL (`psycopg[binary]`) | 16 / 3.3.9 |
| Lenguaje backend | Python | 3.13 |
| Interfaz | React + React DOM | 19.3.1 |
| Lenguaje frontend | TypeScript + Vite | 5.9.3 / 8.3.8 |
| Pruebas backend | `unittest` + `httpx` | stdlib / 0.28.1 |
| Pruebas frontend | Node test runner | Node 26 |
| Contenedores | Docker Compose + Caddy | 2-alpine para el proxy |
| Enlace dispositivos | MQTT (adaptador) / Envelope EP1 | pendiente de fijar broker y tópicos |
| Especificación | OpenSpec | cambio `add-platform-foundation` |

## 📥 Descarga

Elige la forma que necesites:

1. **Clonar con git** (recomendado si vas a desarrollar):
   ```bash
   git clone https://github.com/ITZELJAVIER/Plataforma-Educativa.git
   cd Plataforma-Educativa
   ```
2. **Descargar un ZIP desde GitHub:** [main.zip](https://github.com/ITZELJAVIER/Plataforma-Educativa/archive/refs/heads/main.zip)
   o *Code → Download ZIP*. No incluye el historial de git.
3. **Paquete de despliegue** (`.tar.gz` y `.zip`): se genera solo con archivos
   versionados, por lo que **nunca contiene** `.env`, credenciales, entornos
   virtuales ni dependencias locales:
   ```powershell
   .\scripts\empaquetar.ps1   # Windows
   ```
   ```bash
   bash scripts/package.sh    # Linux/macOS
   ```
   Los archivos quedan en la raíz del proyecto y están ignorados por git. Si se
   publicó una etiqueta `v*`, también están en
   [Releases](https://github.com/ITZELJAVIER/Plataforma-Educativa/releases).

Guías para llevarse e imprimir:
[Guía de despliegue (PDF)](Guia_Despliegue_Plataforma_Educativa.pdf) ·
[Manual de comandos (PDF)](Manual_Comandos_Despliegue.pdf) · versiones
[HTML](Guia_Despliegue_Plataforma_Educativa.html) y
[HTML](Manual_Comandos_Despliegue.html).

## 🚀 Puesta en marcha

### Requisitos

- **Windows (desarrollo):** Python 3.13, Node.js 26 y npm, `.venv` creado en la
  raíz, dependencias instaladas y Docker Desktop con WSL2 solo si se usa Compose.
- **Linux (despliegue):** Docker Engine con plugin `compose`, DNS del dominio
  apuntando al servidor y puertos 80/443 abiertos.
- **Gateway:** nodo independiente (Mini PC x86 con Windows 11 Pro, Docker Desktop
  y WSL2). No se asuma que comparte equipo con la plataforma.

### Opción A — Gestor en Windows (recomendado en local)

El script `plataforma.bat` levanta la API en modo **en memoria** (sin PostgreSQL)
y el frontend de desarrollo:

```powershell
.\plataforma.bat start      # iniciar backend (:8000) y frontend (:5173)
.\plataforma.bat stop       # detener servicios
.\plataforma.bat restart    # reiniciar
.\plataforma.bat status     # estado de puertos y PIDs
.\plataforma.bat verify     # pruebas + build + validación OpenSpec
.\plataforma.bat open       # abrir /docs y la interfaz en el navegador
```

Sin argumentos muestra un menú interactivo. Los PIDs y logs quedan en `.run/`,
que está ignorado por git. Para arrancar sin escribir la contraseña de
administrador de desarrollo, define la variable
`PLATAFORMA_DEV_ADMIN_PASSWORD` antes de ejecutarlo. Estas variables de
desarrollo **no afectan** al punto de entrada de producción.

### Opción B — Arranque manual

```powershell
# Backend (desde la raíz del repo)
py -3.13 -m venv .venv
.\.venv\Scripts\python -m pip install -r backend/requirements-dev.txt
cd backend
..\..\.venv\Scripts\python -m uvicorn src.infrastructure.bootstrap.local_dev:app --host 127.0.0.1 --port 8000
```

```powershell
# Frontend (en otra terminal, desde frontend/)
npm ci
npm run dev
```

Abre <http://localhost:5173> y la documentación interactiva de la API en
<http://127.0.0.1:8000/docs>. El bootstrap `local_dev` crea tres usuarios
temporales (administrador, docente y estudiante) que desaparecen al detener el
proceso; las contraseñas se configuran con variables `PLATAFORMA_DEV_*` o se
solicitan por consola.

### Opción C — Docker Compose (sin validar en este entorno)

```bash
cp .env.example .env
# Edita .env antes de continuar; nunca lo subas al repositorio.
docker compose -f infrastructure/compose/compose.yaml up --build
```

Expone backend en `8000` y frontend en `5173`. Para el modo con HTTPS, consulta
la [sección Docker](#-docker) y la [guía de despliegue](DEPLOY.md).

## ⚙️ Configuración

Copia `.env.example` a `.env` y ajusta los valores. `.env` está ignorado por
git; **no subas contraseñas ni tokens**. La plantilla contiene solo valores de
ejemplo.

| Variable | Uso | Observaciones |
| --- | --- | --- |
| `DOMAIN` | Dominio del despliegue | Usado por Caddy para el certificado HTTPS |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Conexión a la base | `POSTGRES_PASSWORD` es obligatoria en producción |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Conexión a la base | `db:5432` dentro de Compose |
| `DATABASE_URL` | Alternativa a las variables `POSTGRES_*` | Si existe, tiene prioridad |
| `SESSION_TTL_SECONDS` | Vigencia del token de sesión | **Obligatoria**; entero > 0 |
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos por el navegador | Lista separada por comas |
| `BACKEND_PORT`, `FRONTEND_PORT` | Puertos internos de contenedor | 8000 y 5173 |
| `INITIAL_ADMIN_PASSWORD`, `INITIAL_DOCENTE_PASSWORD`, `INITIAL_ESTUDIANTE_PASSWORD` | Usuarios semilla | Solo si la base está vacía; cámbialos antes de usar en real |
| `VITE_API_BASE_URL` | URL de la API compilada en el frontend | Se fija en tiempo de build de Vite |
| `DEVICE_ADAPTER` | Adaptador activo (`simulado` por defecto o `mqtt`) | Se lee al arrancar el backend |
| `PLATAFORMA_DEV_ADMIN_PASSWORD`, `PLATAFORMA_DEV_DOCENTE_PASSWORD`, `PLATAFORMA_DEV_ESTUDIANTE_PASSWORD` | Usuarios del bootstrap en memoria | Solo desarrollo local |

`DATABASE_URL` y `DEVICE_ADAPTER` son opcionales y pueden añadirse a `.env`
cuando se necesiten (la plantilla no los incluye todavía). Las variables
`PLATAFORMA_DEV_*` solo afectan al bootstrap en memoria.

Los parámetros del enlace MQTT (broker, tópicos, QoS, retención, autenticación y
TLS) están **pendientes de autorización** y no se fijan en este repositorio.
Tampoco se ha seleccionado el producto broker.

## 🔐 Roles y permisos

| Rol | Acceso principal |
| --- | --- |
| Administrador | Gestión completa de usuarios, dispositivos y catálogo |
| Docente | Consulta según su alcance y uso de las vistas de práctica |
| Estudiante | Consulta según su alcance; sin administración |

Las respuestas de usuario solo contienen `id`, `role` y `active`: nunca
incluyen contraseñas ni hashes. Todas las rutas salvo `/auth/login` exigen
`Authorization: Bearer <token>`.

## 🌐 API REST

Base: `/api/v1`. Documentación automática: `/docs`, `/redoc` y `/openapi.json`.

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/auth/login` | Iniciar sesión; devuelve `token` |
| `POST` | `/auth/logout` | Cerrar sesión activa |
| `GET` | `/users/me` | Usuario autenticado |
| `GET` | `/users` | Listar usuarios (administrador) |
| `POST` | `/users` | Crear usuario (administrador) |
| `GET` | `/users/{user_id}` | Consultar usuario |
| `PATCH` | `/users/{user_id}/role` | Asignar exactamente un rol |
| `POST` | `/users/{user_id}/deactivate` | Desactivar usuario |
| `POST` | `/users/{user_id}/reactivate` | Reactivar usuario |
| `GET` | `/peripherals/types` | Listar tipos de periférico |
| `GET` | `/peripherals/types/{tipo}` | Consultar un tipo |
| `POST` | `/peripherals/types` | Registrar un tipo |
| `PATCH` | `/peripherals/types/{tipo}` | Actualizar metadatos |
| `POST` | `/peripherals/types/{tipo}/validate-value` | Validar valor contra rango/resolución |
| `GET` | `/devices` | Listar dispositivos |
| `GET` | `/devices/{device_id}` | Consultar dispositivo |
| `POST` | `/devices` | Registrar dispositivo |
| `PATCH` | `/devices/{device_id}` | Actualizar configuración lógica |
| `POST` | `/devices/{device_id}/deactivate` | Desactivar dispositivo |
| `GET` | `/devices/{device_id}/events` | Historial de cambios de estado |

Detalles y escenarios cubiertos en `backend/docs/user-auth.md`,
`backend/docs/peripheral-catalog.md` y `backend/docs/device-management.md`.

## 🧪 Pruebas y calidad

```powershell
# Backend (desde backend/)
..\..\.venv\Scripts\python -m unittest discover -s tests -t .

# Frontend (desde frontend/)
npm test
npm run build

# Todo en Windows, desde la raíz
.\plataforma.bat verify
```

Hay **99 pruebas en el backend** (unitarias, integración y contratos) y
**17 pruebas en el frontend**. `verify` ejecuta todas, el build de producción y
`openspec validate add-platform-foundation --strict`. La integración continua
(`.github/workflows/ci.yml`) repite las pruebas y el build en cada push y PR a
`main`.

## 🐳 Docker

> **Importante:** los Dockerfiles y los archivos Compose están listos, pero no
> se han construido ni ejecutado en el entorno de documentación (Docker no
> estaba instalado). Trátalo como una configuración preparada, no validada.

### Contenedores del stack

| Contenedor | Base | Función | Red / puertos | Persistencia |
| --- | --- | --- | --- | --- |
| `db` | `postgres:16-alpine` | Base de datos con healthcheck | red `plataforma`, interno | volumen `postgres_data` |
| `backend` | `python:3.13-slim` | API FastAPI (punto `asgi:app`) | `8000`, interno en producción | — |
| `frontend` | `node:26-alpine` | Vite preview del build | `5173`, interno en producción | — |
| `proxy` | `caddy:2-alpine` | HTTPS automático y enrutamiento | `80` / `443` | `caddy_data`, `caddy_config` |

Caddy envía `/api/*`, `/docs*`, `/redoc*` y `/openapi.json` al backend; el resto
de las peticiones van al frontend. El **Gateway no está incluido**: se despliega
de forma independiente (ver [infrastructure/gateway/README.md](infrastructure/gateway/README.md)).

### 1. Arranque local con Docker Compose

```bash
cp .env.example .env
# Ajusta .env antes de continuar.
docker compose -f infrastructure/compose/compose.yaml up --build
```

- Frontend: <http://localhost:5173>
- API docs: <http://localhost:8000/docs>
- Apagar: `docker compose -f infrastructure/compose/compose.yaml down`
- Apagar y borrar la base: `docker compose -f infrastructure/compose/compose.yaml down -v`

### 2. Construir las imágenes por separado

```bash
docker build -t plataforma-backend:local ./backend
docker build \
  --build-arg VITE_API_BASE_URL=http://localhost:8000/api/v1 \
  -t plataforma-frontend:local ./frontend
```

La URL de la API del frontend se fija **en tiempo de build**; cámbiala con
`--build-arg` si el backend estará en otra dirección. Para ejecutarlas sin
Compose necesitas además un contenedor PostgreSQL y pasar las variables de
entorno (`SESSION_TTL_SECONDS` y las `POSTGRES_*`) con `--env-file .env`.

### 3. Producción con HTTPS (4 contenedores)

```bash
cp .env.example .env
# Cambia POSTGRES_PASSWORD y las contraseñas INITIAL_* antes de desplegar.
bash infrastructure/deploy.sh
```

El script valida la configuración, construye las imágenes, levanta los cuatro
servicios e imprime las URLs. Requiere que el dominio resuelva al servidor y que
los puertos `80`/`443` estén abiertos.

### 4. Operación diaria

```bash
COMPOSE="docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml"

$COMPOSE ps                 # estado de contenedores
$COMPOSE logs -f backend    # logs de la API
$COMPOSE logs -f proxy      # certificados y HTTPS
$COMPOSE restart backend    # reiniciar un servicio
$COMPOSE down               # apagar conservando la base de datos
$COMPOSE down -v            # apagar y BORRAR la base de datos
```

`SESSION_TTL_SECONDS` y `POSTGRES_PASSWORD` son obligatorias en producción. Los
usuarios iniciales solo se crean cuando la base está vacía. Si necesitas
actualizar la plataforma, copia los cambios y vuelve a ejecutar
`bash infrastructure/deploy.sh`.

## ☁️ Despliegue

El despliegue de prueba usa cuatro servicios: `db` (PostgreSQL 16 con volumen
persistente), `backend` (FastAPI), `frontend` (Vite preview) y `proxy` (Caddy con
Let's Encrypt). Desde el servidor Linux, con `.env` ya configurado:

```bash
docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml config
bash infrastructure/deploy.sh
```

El script valida la configuración, construye las imágenes, levanta los servicios
e imprime la URL final y los comandos de logs.

- [DEPLOY.md](DEPLOY.md) — guía completa: DNS, firewall, Docker, verificación y
  solución de problemas.
- [Guía de despliegue (HTML)](Guia_Despliegue_Plataforma_Educativa.html) ·
  [PDF](Guia_Despliegue_Plataforma_Educativa.pdf)
- [Manual de comandos (HTML)](Manual_Comandos_Despliegue.html) ·
  [PDF](Manual_Comandos_Despliegue.pdf)
- [Gateway central](infrastructure/gateway/README.md) — componente obligatorio,
  desplegado de forma independiente; decisiones autorizadas y pendientes.

## 📊 Estado del cambio OpenSpec

El cambio activo `add-platform-foundation` define cuatro capacidades:
`user-auth`, `device-management`, `peripheral-catalog` y
`platform-infrastructure`.

| Área | Avance |
| --- | --- |
| Estructura y orquestación | Parcial: manifiestos creados; falta validación con Docker |
| Persistencia y modelo de datos | Esquema en implementación; documentación pendiente |
| Identidad, autorización y auditoría | Implementado y cubierto por pruebas |
| Catálogo de periféricos | Implementado y cubierto por pruebas |
| Gestión de dispositivos | Implementada y cubierta por pruebas |
| Puerto de dispositivos, simulado y MQTT | Contratos y adaptadores en progreso |
| WebSocket, healthcheck y servicios transversales | Pendiente |
| Integración y verificación final | Pendiente |

La lista completa de tareas está en
`openspec/changes/add-platform-foundation/tasks.md`. Los cambios de
comportamiento se gestionan con OpenSpec: propuesta, diseño, specs delta, tareas,
aplicación y archivado.

## 🤝 Contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md) para el flujo de trabajo, la convención de
commits y el uso de OpenSpec. Reporta errores con las plantillas de
[issues](.github/ISSUE_TEMPLATE). Para vulnerabilidades, sigue
[SECURITY.md](SECURITY.md) y **no abras un issue público**.

## 📄 Licencia y autoría

Distribuido bajo licencia [MIT](LICENSE).

**Autor:** ITZEL JAVIER OLVERA ·
[Repositorio en GitHub](https://github.com/ITZELJAVIER/Plataforma-Educativa)
