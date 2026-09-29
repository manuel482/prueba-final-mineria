# Datos del proyecto

Ejecuta `python src/restaurar_archivos.py` desde la raíz para preparar los originales desde las partes incluidas en `entrega/`. Sus bytes se verifican contra la última versión del ZIP. `pipeline.py --stage all` también realiza esta preparación si faltan.

## Fuentes conservadas

- `Online Retail.xlsx`: fuente UCI, 541 909 filas. Identificador y licencia en el README principal.
- `productos_original.xlsx`: hoja de la asignatura, 299 169 filas.

Sus hashes están en `../evidencias/sha256_fuentes.json`. La extracción conserva los valores y exporta fechas en formato ISO.

## Archivos regenerados

`python src/pipeline.py --stage all`, ejecutado desde la raíz, crea:

- `retail_original.csv` y `productos_original.csv` desde los Excel.
- `proyecto_kdd.sqlite`, con Bronze, Silver, Gold y tablas de minería.
- Dimensiones, agregados mensuales y `snapshots_modelos.csv`.

Los dos CSV originales y SQLite están excluidos de Git porque duplican datos reproducibles y aumentan considerablemente la descarga. Los CSV pequeños incluidos son resultados de referencia; el pipeline los reemplaza al ejecutarse.

El [empaquetador](../src/empaquetar.py) incluye los archivos grandes ya calculados en una entrega ZIP completa. No hace falta descargar fuentes desde enlaces externos para ejecutar este proyecto.
