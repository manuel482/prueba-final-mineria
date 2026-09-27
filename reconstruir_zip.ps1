$ErrorActionPreference = 'Stop'
$salida = Join-Path $PSScriptRoot 'ProyectoKDD_Entrega.zip'
$esperado = 'd0895f9f1af4e76851e9edec5d1def33572105bbd2218b1d381521dd96a621e2'
$archivos = 1..23 | ForEach-Object { Join-Path $PSScriptRoot ('entrega/ProyectoKDD_Entrega.zip.part{0:D2}' -f $_) }
foreach ($archivo in $archivos) {
    if (-not (Test-Path -LiteralPath $archivo)) { throw "Falta la parte: $archivo" }
}
$destino = [System.IO.File]::Open($salida, [System.IO.FileMode]::Create)
try {
    foreach ($archivo in $archivos) {
        $origen = [System.IO.File]::OpenRead($archivo)
        try { $origen.CopyTo($destino) }
        finally { $origen.Dispose() }
    }
}
finally { $destino.Dispose() }
$obtenido = (Get-FileHash -LiteralPath $salida -Algorithm SHA256).Hash.ToLowerInvariant()
if ($obtenido -ne $esperado) {
    Remove-Item -LiteralPath $salida -Force
    throw "La verificacion SHA-256 fallo. Descarga todas las partes de nuevo."
}
Write-Host "ZIP reconstruido y verificado: $salida"
