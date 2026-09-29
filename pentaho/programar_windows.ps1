# Ejecutar manualmente SOLO después de probar Kitchen desde ejecutar_windows.cmd.
$ErrorActionPreference = 'Stop'
$ProjectPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Launcher = Join-Path $PSScriptRoot 'ejecutar_windows.cmd'
if (-not (Test-Path -LiteralPath $Launcher)) { throw "Falta $Launcher" }
if (-not $env:PDI_DIR -or -not (Test-Path -LiteralPath (Join-Path $env:PDI_DIR 'Kitchen.bat'))) {
    throw 'Define PDI_DIR con la ruta que contiene Kitchen.bat antes de programar.'
}
# La tarea usa un wrapper con PDI_DIR explícito; no hereda variables de la consola.
$Wrapper = Join-Path $PSScriptRoot 'ejecutar_programado.cmd'
$Lines = @(
    '@echo off',
    ('set "PDI_DIR=' + $env:PDI_DIR + '"'),
    ('call "' + $Launcher + '"'),
    'exit /b %ERRORLEVEL%'
)
Set-Content -LiteralPath $Wrapper -Value $Lines -Encoding Default
$Action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument ('/d /c ""' + $Wrapper + '""') -WorkingDirectory $ProjectPath
$Trigger = New-ScheduledTaskTrigger -Daily -At '08:00'
$Settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'ProyectoKDD_ETL' -Action $Action -Trigger $Trigger -Settings $Settings -Description 'ETL local Pentaho Pandas SQLite' -User $env:USERNAME
Write-Host 'Tarea registrada. Verifica el usuario, historial y código de salida en el Programador de tareas.'
