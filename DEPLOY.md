# Despliegue de prueba en servidor Linux + Docker

Dominio confirmado: **sistematizacion.itsoeh.edu.mx**
Acceso: SSH con sudo/root. Modo: Docker + PostgreSQL + HTTPS.

> En este equipo (Windows) no hay Docker, así que la orquestación no pudo
> validarse aquí. Los comandos de abajo se ejecutan en el servidor.

---

## 1. Comprobar DNS y puertos (en tu PC o en el servidor)

El dominio debe resolver a la IP pública del servidor:

```bash
dig +short sistematizacion.itsoeh.edu.mx
# o: nslookup sistematizacion.itsoeh.edu.mx
```

Debe devolver una IP. Si no, crea/ajusta el registro **A** en el DNS antes de
continuar. Caddy necesita que el puerto 80 esté accesible desde Internet para
emitir el certificado.

En el servidor abre los puertos:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

Si usas `firewalld`, usa `firewall-cmd --add-service=http --permanent` y
`--add-service=https --permanent` + `--reload`.

---

## 2. Instalar Docker (si no está)

```bash
sudo apt update && sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Cierra sesión y vuelve a entrar para que el grupo `docker` aplique. Verifica:

```bash
docker --version
docker compose version
```

---

## 3. Subir el proyecto al servidor

Desde PowerShell, en `C:\Plataforma Educativa`:

```powershell
tar -czf plataforma-deploy.tar.gz `
  --exclude=node_modules --exclude=.venv --exclude=.run `
  --exclude=__pycache__ --exclude=.git `
  -C "C:\Plataforma Educativa" .
scp plataforma-deploy.tar.gz usuario@IP_DEL_SERVIDOR:/tmp/
```

En el servidor:

```bash
sudo mkdir -p /opt/plataforma-educativa
sudo tar -xzf /tmp/plataforma-deploy.tar.gz -C /opt/plataforma-educativa
sudo chown -R $USER:$USER /opt/plataforma-educativa
cd /opt/plataforma-educativa
```

---

## 4. Crear el archivo de entorno

```bash
cp .env.example .env
nano .env
```

Cambia obligatoriamente:

- `POSTGRES_PASSWORD` → una contraseña segura (quita el valor `CambiarEstaContraseña`).
- `DOMAIN` → debe ser `sistematizacion.itsoeh.edu.mx` (ya viene así).

El resto de variables ya apuntan al dominio y a la API por HTTPS. Las
contraseñas `INITIAL_*` son las de prueba del archivo `CREDENCIALES_PRUEBAS.txt`
y solo se aplican si la base está vacía.

---

## 5. Validar y levantar

```bash
docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml config
bash infrastructure/deploy.sh
```

El script valida el compose, construye las imágenes y levanta cuatro servicios:

| Servicio | Función |
|---|---|
| `db` | PostgreSQL 16 con volumen persistente |
| `backend` | FastAPI en `8000` (no expuesto al exterior) |
| `frontend` | Vite preview en `5173` (no expuesto al exterior) |
| `proxy` | Caddy en `80`/`443`, HTTPS automático con Let's Encrypt |

Ver logs del proxy si tarda el certificado:

```bash
docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml logs -f proxy
```

---

## 6. Verificar

```bash
curl -I https://sistematizacion.itsoeh.edu.mx/
curl -s https://sistematizacion.itsoeh.edu.mx/openapi.json | head -c 200

curl -X POST https://sistematizacion.itsoeh.edu.mx/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"id":"admin","password":"dev-admin"}'
```

También entra a `https://sistematizacion.itsoeh.edu.mx/` en el navegador e
inicia sesión con cualquiera de las cuentas de `CREDENCIALES_PRUEBAS.txt`.

---

## Comandos útiles

```bash
# Estado
docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml ps

# Reiniciar un servicio
docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml restart backend

# Apagar conservando la base de datos
docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml down

# Apagar y BORRAR la base de datos (volver a sembrar usuarios al levantar)
docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml down -v

# Actualizar tras copiar cambios
bash infrastructure/deploy.sh
```

---

## Solución de problemas

- **Caddy no emite certificado:** confirma que `dig +short sistematizacion.itsoeh.edu.mx`
  devuelve la IP del servidor, que el puerto 80 está abierto y que ningún otro
  proceso (Apache/Nginx) ocupa 80 o 443. Revisa `logs proxy`.
- **502 en `/api`:** el backend puede estar fallando por variables de entorno.
  Revisa `logs backend`; `SESSION_TTL_SECONDS` y `POSTGRES_PASSWORD` son obligatorias.
- **No puedo hacer login:** las contraseñas iniciales solo se crean cuando la
  tabla de usuarios está vacía. Si ya creaste usuarios, cambia la contraseña con
  la API o recrea el volumen con `down -v` (borra datos).
- **CORS:** si abres la app por una IP en vez del dominio, ajusta
  `CORS_ALLOWED_ORIGINS` en `.env` y reinicia (`up -d --force-recreate backend`).

## Seguridad

`dev-admin`, `clave-docente` y `clave-estudiante` son credenciales de prueba.
Cámbialas en `.env` antes de cualquier uso real y no subas `.env` al repositorio.
