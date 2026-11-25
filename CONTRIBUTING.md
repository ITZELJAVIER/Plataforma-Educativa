# Cómo contribuir

Gracias por interesarte en la Plataforma Educativa. Este documento explica cómo
preparar el entorno, proponer cambios y enviar una contribución que pueda
revisarse fácilmente.

## 1. Preparar el entorno

1. Haz un fork y clona tu copia:
   ```bash
   git clone https://github.com/<tu-usuario>/Plataforma-Educativa.git
   cd Plataforma-Educativa
   ```
2. Backend (Python 3.13):
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\python -m pip install -r backend/requirements-dev.txt
   # Linux/macOS: .venv/bin/python -m pip install -r backend/requirements-dev.txt
   ```
3. Frontend (Node.js 26):
   ```bash
   cd frontend && npm ci
   ```
4. Copia `.env.example` a `.env` solo si vas a trabajar con Docker/PostgreSQL.
   **Nunca subas `.env` ni credenciales al repositorio.**

En Windows puedes usar `plataforma.bat start` para levantar el entorno en
memoria sin PostgreSQL y `plataforma.bat verify` para comprobarlo todo.

## 2. Ramas y commits

- `main`: rama estable; no commits directos.
- `feature/<nombre>`, `fix/<nombre>`, `docs/<nombre>`, `refactor/<nombre>`.
- Commits cortos con prefijo: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`,
  `build:`, `ci:` o `chore:`.
  Ejemplo: `docs: ampliar README con la API versionada`.

## 3. Flujo de trabajo con OpenSpec

Los cambios que modifican comportamiento pasan por OpenSpec antes de
implementarse:

1. Propón el cambio con la skill `/opsx-propose` (o el comando equivalente).
2. Revisa y ajusta `proposal.md`, `design.md`, los `specs/` delta y `tasks.md`
   con `/opsx-update`.
3. Valida con `openspec validate <change> --strict`.
4. Implementa las tareas con `/opsx-apply`.
5. Sincroniza las specs consolidadas con `/opsx-sync` y archiva con
   `/opsx-archive` cuando todo esté verificado.

El cambio activo es `add-platform-foundation`; su estado se resume en el
[README](README.md#-estado-del-cambio-openspec).

## 4. Antes de abrir un Pull Request

Ejecuta y pega el resultado en la descripción del PR:

```bash
# Desde backend/
python -m unittest discover -s tests -t .

# Desde frontend/
npm test
npm run build

# Desde la raíz (si tienes el CLI de OpenSpec)
openspec validate add-platform-foundation --strict
```

Comprueba además que:

- [ ] Las pruebas nuevas cubren el comportamiento cambiado.
- [ ] La documentación afectada está actualizada (`README.md`, `backend/docs/`).
- [ ] El dominio no depende de FastAPI, PostgreSQL, MQTT ni de hardware.
- [ ] No hay secretos, `.env`, tokens ni credenciales en el diff.
- [ ] El build del frontend termina sin errores de TypeScript.

## 5. Reportar problemas

Usa las plantillas de [issues](.github/ISSUE_TEMPLATE). Incluye pasos de
reproducción, entorno, rama/commit y fragmentos de log **sin información
sensible**. Para temas de seguridad, escribe a la dirección indicada en
[SECURITY.md](SECURITY.md) en lugar de abrir un issue público.

## 6. Código de conducta

La participación se rige por [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
