#!/usr/bin/env bash
# Despliegue de prueba en el servidor (Linux + Docker).
# Ejecutar desde cualquier directorio:  bash infrastructure/deploy.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -f .env ]; then
  echo "ERROR: no existe .env. Copia .env.example a .env y edítalo primero."
  exit 1
fi

if grep -q '^POSTGRES_PASSWORD=CambiarEstaContraseña' .env; then
  echo "ERROR: cambia POSTGRES_PASSWORD en .env antes de desplegar."
  exit 1
fi

COMPOSE=(docker compose --env-file .env -f infrastructure/compose/compose.prod.yaml)

echo "[1/3] Validando compose..."
"${COMPOSE[@]}" config >/dev/null

echo "[2/3] Construyendo y levantando servicios..."
"${COMPOSE[@]}" up -d --build

echo "[3/3] Estado:"
"${COMPOSE[@]}" ps

echo
echo "Frontend: https://$(grep '^DOMAIN=' .env | cut -d= -f2)/"
echo "API docs: https://$(grep '^DOMAIN=' .env | cut -d= -f2)/docs"
echo "Ver logs: ${COMPOSE[*]} logs -f proxy"
