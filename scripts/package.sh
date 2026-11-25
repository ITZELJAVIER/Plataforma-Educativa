#!/usr/bin/env bash
# Genera paquetes descargables del proyecto (.tar.gz y .zip).
# Usa `git archive`, por lo que SOLO incluye archivos versionados:
# nunca se incluyen .env, credenciales, .venv, node_modules ni logs locales.
# Uso: bash scripts/package.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

git archive --format=tar.gz --prefix=Plataforma-Educativa/ \
  -o plataforma-deploy.tar.gz HEAD
git archive --format=zip --prefix=Plataforma-Educativa/ \
  -o plataforma-deploy.zip HEAD

ls -lh plataforma-deploy.tar.gz plataforma-deploy.zip
