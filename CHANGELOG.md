# Registro de cambios

Todas las contribuciones notables se documentan aquí. El formato se inspira en
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto sigue
[Versionado Semántico](https://semver.org/lang/es/).

## [No publicado]

### Añadido

- Documentación principal del repositorio: `README.md`, `CONTRIBUTING.md`,
  `SECURITY.md`, `CODE_OF_CONDUCT.md` y `CHANGELOG.md`.
- Plantillas de issues y Pull Request, política de seguridad y flujo de CI para
  backend y frontend.
- Protección de credenciales de prueba mediante `.gitignore`.
- Scripts `scripts/empaquetar.ps1` y `scripts/package.sh` para generar paquetes
  `.tar.gz`/`.zip` descargables solo con archivos versionados.
- Workflow `release.yml` que publica los paquetes en GitHub Releases al empujar
  una etiqueta `v*`.
- Secciones de descarga y de contenedores Docker en el README.

## [0.1.0] - 2026-11-24

### Añadido

- Estructura hexagonal del backend con FastAPI, PostgreSQL y adaptadores de
  persistencia, seguridad y dispositivos.
- Autenticación, autorización por rol, administración de usuarios y auditoría.
- Catálogo de periféricos con siete tipos base y validación de metadatos.
- Gestión de dispositivos con estados, configuración e historial de eventos.
- Interfaz React + TypeScript + Vite con vistas por rol y tema claro/oscuro.
- Orquestación Docker Compose, proxy Caddy y guías de despliegue.
- Propuesta OpenSpec `add-platform-foundation` con capacidades y tareas.

[No publicado]: https://github.com/ITZELJAVIER/Plataforma-Educativa/compare/main...HEAD
[0.1.0]: https://github.com/ITZELJAVIER/Plataforma-Educativa/releases/tag/v0.1.0
