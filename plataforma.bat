@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

rem ============================================================
rem  Plataforma Educativa - gestor de servicios de desarrollo
rem  Uso: plataforma.bat [start|stop|restart|status|verify|open]
rem  Sin argumentos se muestra un menu interactivo.
rem
rem  El backend usa el bootstrap en memoria (sin PostgreSQL) y crea
rem  un administrador temporal "admin". La contrasena se toma de
rem  PLATAFORMA_DEV_ADMIN_PASSWORD (por defecto: dev-admin) para
rem  que el arranque no sea interactivo. Solo afecta a desarrollo.
rem ============================================================

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "VENV_PY=%ROOT%.venv\Scripts\python.exe"
set "RUN_DIR=%ROOT%.run"
set "BACKEND_PID_FILE=%RUN_DIR%\backend.pid"
set "FRONTEND_PID_FILE=%RUN_DIR%\frontend.pid"
set "BACKEND_OUT=%RUN_DIR%\backend.log"
set "BACKEND_ERR=%RUN_DIR%\backend.err.log"
set "FRONTEND_OUT=%RUN_DIR%\frontend.log"
set "FRONTEND_ERR=%RUN_DIR%\frontend.err.log"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"

if not defined PLATAFORMA_DEV_ADMIN_PASSWORD set "PLATAFORMA_DEV_ADMIN_PASSWORD=dev-admin"
if not exist "%RUN_DIR%" mkdir "%RUN_DIR%" >nul 2>&1

if /I "%~1"=="start" goto :start
if /I "%~1"=="stop" goto :stop
if /I "%~1"=="restart" goto :restart
if /I "%~1"=="status" goto :status
if /I "%~1"=="verify" goto :verify
if /I "%~1"=="open" goto :open
if "%~1"=="" goto :menu
echo Opcion desconocida: %~1
goto :usage

:menu
cls
echo.
echo  === Plataforma Educativa - Servicios de desarrollo ===
echo.
echo   [1] Iniciar backend y frontend
echo   [2] Detener servicios
echo   [3] Reiniciar
echo   [4] Estado
echo   [5] Verificar proyecto
echo   [6] Abrir en el navegador
echo   [0] Salir
echo.
choice /C 1234560 /N /M "Elige una opcion: "
if errorlevel 7 exit /b 0
if errorlevel 6 goto :open
if errorlevel 5 goto :verify
if errorlevel 4 goto :status
if errorlevel 3 goto :restart
if errorlevel 2 goto :stop
if errorlevel 1 goto :start

:usage
echo.
echo Uso: plataforma.bat [start^|stop^|restart^|status^|verify^|open]
echo.
exit /b 1

:check_prereqs
if not exist "%VENV_PY%" (
  echo [ERROR] No se encontro el entorno virtual: %VENV_PY%
  exit /b 1
)
if not exist "%FRONTEND_DIR%\node_modules" (
  echo [ERROR] Faltan dependencias del frontend. Ejecuta npm install en %FRONTEND_DIR%
  exit /b 1
)
exit /b 0

:port_pid
set "PORT_PID="
for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort %~1 -State Listen -ErrorAction SilentlyContinue).OwningProcess"`) do set "PORT_PID=%%P"
exit /b 0

:show_tail
set "PE_LOG=%~1"
powershell -NoProfile -Command "if (Test-Path -LiteralPath $env:PE_LOG) { Get-Content -LiteralPath $env:PE_LOG -Tail 3 }" 2>nul
exit /b 0

:start
call :check_prereqs || exit /b 1
call :port_pid %BACKEND_PORT%
if defined PORT_PID (
  echo [AVISO] El puerto %BACKEND_PORT% ya esta en uso ^(PID !PORT_PID!^). No se inicia el backend.
) else (
  echo Iniciando backend en http://127.0.0.1:%BACKEND_PORT% ...
  call :launch_backend
)
call :port_pid %FRONTEND_PORT%
if defined PORT_PID (
  echo [AVISO] El puerto %FRONTEND_PORT% ya esta en uso ^(PID !PORT_PID!^). No se inicia el frontend.
) else (
  echo Iniciando frontend en http://localhost:%FRONTEND_PORT% ...
  call :launch_frontend
)
echo.
echo Esperando a que la API responda...
set "READY=0"
for /L %%I in (1,1,20) do (
  if "!READY!"=="0" (
    powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:%BACKEND_PORT%/openapi.json' -TimeoutSec 1; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "READY=1"
    if "!READY!"=="0" ping -n 2 127.0.0.1 >nul 2>&1
  )
)
if "!READY!"=="1" (
  echo [OK] API lista. Usuario: admin / contrasena de desarrollo: %PLATAFORMA_DEV_ADMIN_PASSWORD%
) else (
  echo [AVISO] La API no respondio a tiempo. Revisa %BACKEND_ERR%
)
call :status
exit /b 0

:launch_backend
set "PE_PY=%VENV_PY%"
set "PE_BACKEND_DIR=%BACKEND_DIR%"
set "PE_BACKEND_PORT=%BACKEND_PORT%"
set "PE_BACKEND_OUT=%BACKEND_OUT%"
set "PE_BACKEND_ERR=%BACKEND_ERR%"
set "PE_PID_FILE=%BACKEND_PID_FILE%"
set "PS_CMD=$p = Start-Process -FilePath $env:PE_PY -ArgumentList @('-m','uvicorn','src.infrastructure.bootstrap.local_dev:app','--host','127.0.0.1','--port',$env:PE_BACKEND_PORT) -WorkingDirectory $env:PE_BACKEND_DIR -RedirectStandardOutput $env:PE_BACKEND_OUT -RedirectStandardError $env:PE_BACKEND_ERR -WindowStyle Hidden -PassThru; $p.Id | Set-Content -LiteralPath $env:PE_PID_FILE -NoNewline"
if exist "%BACKEND_PID_FILE%" del "%BACKEND_PID_FILE%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "%PS_CMD%"
set "BACKEND_PID="
if exist "%BACKEND_PID_FILE%" set /p BACKEND_PID=<"%BACKEND_PID_FILE%"
if defined BACKEND_PID (
  echo [OK] Backend iniciado ^(PID !BACKEND_PID!^)
) else (
  echo [ERROR] No se pudo iniciar el backend.
)
exit /b 0

:launch_frontend
set "PE_FRONTEND_DIR=%FRONTEND_DIR%"
set "PE_FRONTEND_OUT=%FRONTEND_OUT%"
set "PE_FRONTEND_ERR=%FRONTEND_ERR%"
set "PE_PID_FILE=%FRONTEND_PID_FILE%"
set "PS_CMD=$p = Start-Process -FilePath 'npm.cmd' -ArgumentList @('run','dev') -WorkingDirectory $env:PE_FRONTEND_DIR -RedirectStandardOutput $env:PE_FRONTEND_OUT -RedirectStandardError $env:PE_FRONTEND_ERR -WindowStyle Hidden -PassThru; $p.Id | Set-Content -LiteralPath $env:PE_PID_FILE -NoNewline"
if exist "%FRONTEND_PID_FILE%" del "%FRONTEND_PID_FILE%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "%PS_CMD%"
set "FRONTEND_PID="
if exist "%FRONTEND_PID_FILE%" set /p FRONTEND_PID=<"%FRONTEND_PID_FILE%"
if defined FRONTEND_PID (
  echo [OK] Frontend iniciado ^(PID !FRONTEND_PID!^)
) else (
  echo [ERROR] No se pudo iniciar el frontend.
)
exit /b 0

:stop
echo Deteniendo servicios...
call :stop_one "%BACKEND_PID_FILE%" %BACKEND_PORT% backend
call :stop_one "%FRONTEND_PID_FILE%" %FRONTEND_PORT% frontend
exit /b 0

:stop_one
set "PF=%~1"
set "PORT=%~2"
set "LABEL=%~3"
set "OLD_PID="
if exist "%PF%" (
  for /f "usebackq delims=" %%L in ("%PF%") do set "OLD_PID=%%L"
  if defined OLD_PID (
    taskkill /PID !OLD_PID! /T /F >nul 2>&1
    echo [OK] !LABEL! detenido ^(PID !OLD_PID!^)
  )
  del "%PF%" >nul 2>&1
)
call :port_pid %PORT%
if defined PORT_PID (
  taskkill /PID !PORT_PID! /T /F >nul 2>&1
  echo [OK] Proceso residual en el puerto %PORT% detenido ^(PID !PORT_PID!^)
)
exit /b 0

:restart
call :stop
ping -n 3 127.0.0.1 >nul 2>&1
call :start
exit /b 0

:status
echo.
echo === Estado de servicios ===
call :port_pid %BACKEND_PORT%
if defined PORT_PID (
  echo Backend : ESCUCHANDO en %BACKEND_PORT% ^(PID !PORT_PID!^)
) else (
  echo Backend : DETENIDO
)
call :port_pid %FRONTEND_PORT%
if defined PORT_PID (
  echo Frontend: ESCUCHANDO en %FRONTEND_PORT% ^(PID !PORT_PID!^)
) else (
  echo Frontend: DETENIDO
)
echo PIDs y logs: %RUN_DIR%
exit /b 0

:verify
echo.
echo === Verificacion del proyecto ===
set "FAILED=0"

echo [1/4] Pruebas del backend ...
pushd "%BACKEND_DIR%"
"%VENV_PY%" -m unittest discover -s tests -t . > "%RUN_DIR%\verify-backend.log" 2>&1
set "RC=!ERRORLEVEL!"
popd
if "!RC!"=="0" (echo       OK) else (echo       FALLIDO & set "FAILED=1")
call :show_tail "%RUN_DIR%\verify-backend.log"

echo [2/4] Pruebas del frontend ...
pushd "%FRONTEND_DIR%"
call npm test > "%RUN_DIR%\verify-frontend.log" 2>&1
set "RC=!ERRORLEVEL!"
popd
if "!RC!"=="0" (echo       OK) else (echo       FALLIDO & set "FAILED=1")
call :show_tail "%RUN_DIR%\verify-frontend.log"

echo [3/4] Build de produccion del frontend ...
pushd "%FRONTEND_DIR%"
call npm run build > "%RUN_DIR%\verify-build.log" 2>&1
set "RC=!ERRORLEVEL!"
popd
if "!RC!"=="0" (echo       OK) else (echo       FALLIDO & set "FAILED=1")
call :show_tail "%RUN_DIR%\verify-build.log"

echo [4/4] Validacion OpenSpec ...
pushd "%ROOT%"
call openspec validate add-platform-foundation --strict > "%RUN_DIR%\verify-openspec.log" 2>&1
set "RC=!ERRORLEVEL!"
popd
if "!RC!"=="0" (echo       OK) else (echo       FALLIDO & set "FAILED=1")
call :show_tail "%RUN_DIR%\verify-openspec.log"

echo.
if "!FAILED!"=="0" (
  echo === Verificacion completada: todo OK ===
) else (
  echo === Verificacion completada CON FALLOS. Revisa los logs en %RUN_DIR% ===
)
exit /b 0

:open
start "" "http://localhost:%FRONTEND_PORT%"
start "" "http://127.0.0.1:%BACKEND_PORT%/docs"
exit /b 0
