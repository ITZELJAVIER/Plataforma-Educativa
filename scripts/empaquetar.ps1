# Genera paquetes descargables del proyecto (.tar.gz y .zip).
# Usa `git archive`, por lo que SOLO incluye archivos versionados:
# nunca se incluyen .env, credenciales, .venv, node_modules ni logs locales.
# Ejecutar desde cualquier directorio: powershell -File scripts\empaquetar.ps1

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$prefix = 'Plataforma-Educativa/'
$tar = Join-Path $root 'plataforma-deploy.tar.gz'
$zip = Join-Path $root 'plataforma-deploy.zip'

git -C $root archive --format=tar.gz --prefix=$prefix -o $tar HEAD
if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar el .tar.gz' }

git -C $root archive --format=zip --prefix=$prefix -o $zip HEAD
if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar el .zip' }

Get-Item -LiteralPath $tar, $zip | Select-Object Name, @{Name='MB';Expression={[math]::Round($_.Length / 1MB, 2)}}
