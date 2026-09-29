# Comprobación del proyecto

## 1. Comprobar una descarga nueva

Desde la raíz, antes de recalcular resultados:

```powershell
py -3.12 src\restaurar_archivos.py
py -3.12 src\verificar_entrega.py --solo-fuentes --archivos
```

Debe terminar en `RESULTADO: OK` y devolver código 0. El primer comando prepara los archivos binarios y valida que coinciden con la última entrega. El verificador comprueba los Excel, sus hashes, los archivos del manifiesto y la sintaxis XML/JSON de Pentaho y Power BI. **No requiere la base SQLite y no certifica la ejecución de esas aplicaciones.**

`MANIFEST_SHA256.json` describe los archivos publicados. Si editas código, guías o resultados, sus hashes cambiarán. No uses `--archivos` para juzgar una copia modificada: utiliza la comprobación de contenido del paso 2. El ZIP completo generado por `empaquetar.py` lleva su propio manifiesto con la base y los CSV.

## 2. Comprobar el proceso completo

Primero sigue [instalación](GUIA_INSTALACION.md) y ejecuta `src/pipeline.py --stage all`. Después:

```powershell
.\.venv\Scripts\python.exe src\verificar_entrega.py --json evidencias\comprobacion_local.json
$LASTEXITCODE
```

El verificador debe devolver 0, un resultado `OK` y cero errores. Comprueba fuentes, integridad SQLite, tablas, conciliación de filas, claves sin duplicados ni huérfanos, totales frente a `kpis.json`, evidencias y estructura de los archivos nativos. Abre la base en modo solo lectura: no crea una base vacía si falta.

## 3. Conteos SQL de referencia

| Tabla o regla | Resultado |
| --- | ---: |
| bronze_retail | 541 909 |
| bronze_productos | 299 169 |
| silver_retail | 536 639 |
| silver_retail_rechazos | 5 270 |
| silver_productos | 299 169 |
| silver_productos_rechazos | 0 |
| gold_retail | 536 639 |
| gold_ventas_productos | 299 169 |
| dim_productos | 60 |
| gold_predicciones | 4 612 |
| gold_segmentos | 2 889 |

Debe cumplirse **Bronze = Silver + rechazos** para ambas fuentes y **Gold = Silver** para cada tabla de hechos. Ejecuta `sql/04_consultas.sql` en un cliente SQLite y guarda capturas reales de los resultados. Los conteos corresponden a los Excel incluidos; si los cambias, documenta las diferencias.

## 4. KPI y minería

| Indicador | Valor de referencia |
| --- | ---: |
| Venta neta Retail (GBP) | 9 748 131,074 |
| Venta bruta Retail (GBP) | 10 642 110,804 |
| Devoluciones Retail (GBP) | 893 979,730 |
| Venta Productos (moneda no especificada) | 5 461 711 163,714 |
| Accuracy de clasificación | 0,67346 |
| Recall de clasificación | 0,23649 |
| AUC | 0,67337 |
| RMSE de regresión (GBP) | 1 158,5653 |
| R² de regresión | 0,47407 |
| Clusters seleccionados | 2 |
| Silhouette | 0,44176 |

Los importes de Productos y Retail no se suman entre sí. Los cálculos usan valores completos; la tabla solo redondea para lectura. Consulta `evidencias/kpis.json`, `metricas.json`, `matriz_confusion.csv` y los PNG. Las diferencias numéricas mínimas entre bibliotecas/plataformas no implican cambios en las filas.

El split temporal usa mayo-agosto de 2011 para entrenamiento, septiembre para validación y octubre-noviembre para prueba. Comprueba 7 844 observaciones de entrenamiento, 1 923 de validación y 4 612 de prueba. Las métricas guardadas y los `.joblib` son referencias reproducibles; la presencia de esos archivos no garantiza compatibilidad con cualquier versión de scikit-learn.

## 5. Pentaho: evidencia nativa

1. Abre el KJB y los dos KTR en Spoon. Verifica Java, JDBC, conexión, rutas y tipos.
2. Ejecuta el job completo y luego Kitchen siguiendo la guía de instalación.
3. Exige código 0 y revisa las filas cargadas de cada KTR en `evidencias/pentaho_real.log`.
4. Vuelve a ejecutar el verificador Python y compara los conteos.
5. Guarda capturas del job, transformaciones, conexión y **Execution Results**.
6. Si programas una tarea, prueba una ejecución y conserva historial y código de salida.

Un XML bien formado no prueba que Spoon haya ejecutado el job. `pipeline.log` corresponde a Python; no debe presentarse como un log de Pentaho.

## 6. Power BI: evidencia nativa

Configura el DSN `ProyectoKDD` de 64 bits hacia la misma base. Abre el PBIP en Desktop y actualiza. Comprueba relaciones uno a muchos, filtros por fecha y categoría, segmentadores, matriz y mapa Retail. Contrasta los totales con SQL y `kpis.json`.

Guarda el PBIX y capturas de las cuatro páginas, vista Modelo, DAX, Power Query y conexión. Si el proyecto no abre, registra el error y corrige o recrea el modelo antes de presentarlo como validado. Los códigos territoriales del segundo dataset requieren un catálogo comprobado; no los geocodifiques como si fueran nombres de lugares.

## 7. Diagnóstico

| Problema | Acción |
| --- | --- |
| Falta SQLite o un CSV en una descarga nueva | Instala dependencias y ejecuta `--stage all`; son archivos generados |
| `ModuleNotFoundError` | Instala con el `python.exe` del mismo entorno usado para ejecutar |
| No existe `py -3.12` | Instala Python 3.12 o usa el ejecutable de esa instalación |
| `database is locked` | Cierra Desktop, Spoon, clientes SQLite y otras ejecuciones del pipeline |
| Hash distinto | Usa una descarga limpia o identifica la edición; no alteres el hash para ocultarla |
| Etapa fallida | Lee el primer error de `pipeline.log`, corrige y repite `all` |
| `org.sqlite.JDBC` no encontrado | Instala el driver y sus dependencias según tu versión de PDI; reinicia Spoon |
| DSN no aparece | Comprueba que driver, administrador ODBC y Desktop sean de 64 bits |
| Espacio insuficiente | Deja espacio para fuentes, SQLite, temporales y el ZIP; no empaquetes cachés |

El cierre académico requiere tanto las comprobaciones automáticas como las pruebas nativas de [ESTADO_Y_EVIDENCIAS.md](ESTADO_Y_EVIDENCIAS.md).
