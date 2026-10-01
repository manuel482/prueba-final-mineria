# Ejecución y entrega

Prepara el entorno según [instalación](GUIA_INSTALACION.md). Todos los comandos siguientes parten de la carpeta que contiene `src`; en Linux/macOS sustituye `.\.venv\Scripts\python.exe` por `./.venv/bin/python`.

## Ejecución completa

```powershell
.\.venv\Scripts\python.exe src\pipeline.py --stage all
.\.venv\Scripts\python.exe src\verificar_entrega.py --json evidencias\comprobacion_local.json
```

`all` ejecuta, en orden: **extract → bronze (incluye validate) → silver → gold → mining → verify → notify**. Prepara automáticamente los binarios que falten desde `entrega/` y reconstruye los CSV y la base desde los Excel, por lo que funciona en una descarga nueva de GitHub. La ejecución construye y verifica una base temporal antes de reemplazar SQLite en `data/`. Las salidas auxiliares se recalculan durante el proceso; no se deben refrescar dashboards hasta completarlo.

Consulta `evidencias/pipeline.log`. `estado_ejecucion.json` registra `EN_PROCESO`, `ERROR` u `OK`. La notificación es un archivo local; no envía correos ni mensajes.

## Flujo de Persona D · Manuel

Para ejecutar la parte de soporte e integración de una sola vez:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe src\persona_d_entrega.py
```

Este comando ejecuta y verifica el pipeline, genera evidencias del dataset original y de consultas SQL, ejecuta `notebooks/Proyecto_KDD.ipynb` con `nbconvert --execute --inplace` para conservar las salidas visibles y escribe `evidencias/persona_d_resumen.json` con el tamaño y SHA-256 de `data/proyecto_kdd.sqlite`.

La base SQLite se comparte por Drive con los otros tres integrantes; no se publica en GitHub porque ronda los 420 MB. Si la base ya fue generada y validada, usa `--sin-pipeline`.

## Etapas individuales

Para diagnóstico puedes usar `--stage extract`, `bronze`, `validate`, `silver`, `gold`, `mining`, `verify` o `notify`. Cada etapa necesita las salidas de las anteriores:

| Etapa | Entrada necesaria | Resultado |
| --- | --- | --- |
| extract | Dos Excel de `data/` | CSV originales |
| bronze | CSV originales | Tablas Bronze y validación |
| validate | Tablas Bronze | Control de carga |
| silver | Bronze | Tablas limpias, rechazos y perfiles |
| gold | Silver y `sql/02_gold.sql` | Hechos, dimensiones, vistas, CSV y gráficos |
| mining | Gold Retail | Modelos, predicciones y métricas |
| verify | Todas las tablas calculadas | Integridad, relaciones, esquema y entorno |
| notify | Proceso ya completado y verificado | Estado local de finalización |

No ejecutes `notify` para ocultar un error: solo escribe el estado y no reconstruye ni valida las tablas. Tras corregir un fallo, la ruta recomendada es repetir `all` y el verificador externo.

## Crear un ZIP completo

Después de una ejecución y comprobación correctas:

```powershell
.\.venv\Scripts\python.exe src\empaquetar.py
```

El script comprueba la base, crea **`ProyectoKDD_Entrega.zip` en la carpeta superior**, incorpora los CSV y SQLite ya calculados, genera un manifiesto SHA-256 dentro del ZIP y comprueba su integridad. No altera `MANIFEST_SHA256.json` del repositorio ni incluye `.git`, entornos virtuales, cachés o las partes de `entrega/`, porque el ZIP final ya contiene los binarios preparados. Si ya existe el ZIP de salida, lo reemplaza al finalizar correctamente.

Para elegir otro destino, fuera de la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe src\empaquetar.py --salida 'C:\Entregas\ProyectoKDD_Entrega.zip'
```

Este ZIP completo puede superar el tamaño admitido para un archivo normal de GitHub. El repositorio publica los archivos fuente y permite reproducir la entrega; no necesita almacenar de nuevo la base generada ni fragmentar el ZIP.

Para validar un ZIP recién extraído, antes de ejecutar de nuevo el pipeline:

```powershell
py -3.12 src\verificar_entrega.py --archivos
```

Consulta [comprobación](GUIA_COMPROBACION.md) y [estado de evidencias](ESTADO_Y_EVIDENCIAS.md) para completar las pruebas de Pentaho y Power BI.
