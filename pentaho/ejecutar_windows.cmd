@echo off
setlocal
rem Definir PDI_DIR antes de ejecutar; carpeta que contiene Kitchen.bat.
if not defined PDI_DIR set "PDI_DIR=C:\data-integration"
for %%I in ("%~dp0..") do set "PROJECT_DIR=%%~fI"
if not exist "%PDI_DIR%\Kitchen.bat" (
  echo ERROR: no existe "%PDI_DIR%\Kitchen.bat". Configura PDI_DIR.
  exit /b 2
)
if not exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
  echo ERROR: falta "%PROJECT_DIR%\.venv\Scripts\python.exe". Instala el entorno Python.
  exit /b 3
)
if not exist "%PROJECT_DIR%\pentaho\proyecto_completo.kjb" (
  echo ERROR: falta el job del proyecto.
  exit /b 4
)
call "%PDI_DIR%\Kitchen.bat" /file:"%PROJECT_DIR%\pentaho\proyecto_completo.kjb" /param:PROJECT_DIR="%PROJECT_DIR%" /param:PYTHON_EXE="%PROJECT_DIR%\.venv\Scripts\python.exe" /level:Basic /logfile:"%PROJECT_DIR%\evidencias\pentaho_real.log"
exit /b %ERRORLEVEL%
