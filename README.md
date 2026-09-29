# Proyecto KDD · Pandas, SQL, Pentaho y Power BI

**Autor:** Manuel Mora Matías.

Pipeline académico de analítica con arquitectura Medallion (Bronze, Silver y Gold), clasificación, regresión y segmentación de clientes. Fuentes: **541 909 registros de Online Retail** y **299 169 registros de productos**.

Esta actualización parte de **ProyectoKDD_Entrega.zip, versión 2 del 27 de septiembre de 2026**. El nombre anterior `manuel482/Aplicacion-de-prueba-supermercado` redirige a este repositorio.

## Descargar y comenzar

Pulsa **Code → Download ZIP**, extrae una sola vez y abre una terminal en la carpeta que contiene este `README.md`, `requirements.txt` y `src`. También puedes clonar el repositorio:

```bash
git clone https://github.com/manuel482/prueba-final-mineria.git
cd prueba-final-mineria
```

En Windows PowerShell, con **Python 3.12 de 64 bits**:

```powershell
py -3.12 src\restaurar_archivos.py
py -3.12 src\verificar_entrega.py --solo-fuentes --archivos
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-verificado.txt
.\.venv\Scripts\python.exe src\pipeline.py --stage all
.\.venv\Scripts\python.exe src\verificar_entrega.py --json evidencias\comprobacion_local.json
```

`--stage all` ahora incluye la extracción de los dos Excel, crea los CSV y la base SQLite, entrena los modelos y valida los resultados. Espera a que termine con código 0 antes de continuar. Las instrucciones detalladas incluyen Linux/macOS y diagnóstico.

**La descarga de GitHub contiene el código organizado y los binarios empaquetados en `entrega/`.** `restaurar_archivos.py` prepara los dos Excel, las figuras y los modelos de referencia, verificando que son idénticos a los de la última entrega. No sobrescribe código ni guías. La base `data/proyecto_kdd.sqlite` (aproximadamente 420 MB) y los dos CSV originales se regeneran localmente y están excluidos de Git. Las 23 partes existentes se reutilizan únicamente para recuperar estos binarios; el código y las guías vigentes están en las carpetas navegables del repositorio. Las salidas pequeñas se conservan como referencia.

## Guías y documentos

| Recurso | Uso |
| --- | --- |
| [Instalación](docs/GUIA_INSTALACION.md) | Preparar Python, SQLite, Pentaho y Power BI |
| [Ejecución](docs/GUIA_EJECUCION.md) | Ejecutar todo, repetir etapas y crear la entrega ZIP |
| [Comprobación](docs/GUIA_COMPROBACION.md) | Revisar conteos, KPI, modelos, hashes y errores |
| [Estado y evidencias](docs/ESTADO_Y_EVIDENCIAS.md) | Qué está validado y qué requiere aplicaciones nativas |
| [Cambios de esta publicación](docs/ACTUALIZACION.md) | Procedencia del ZIP y correcciones |
| [Informe Word](Informe_Proyecto_KDD.docx) | Metodología, resultados e interpretación |

## Organización

| Carpeta | Contenido |
| --- | --- |
| `data/` | Excel originales, dimensiones, agregados y snapshots; [detalle](data/README.md) |
| `src/` | Extracción, ETL, minería, verificación y empaquetado |
| `sql/` | Esquemas y consultas para comprobación |
| `notebooks/` | Notebook listo para ejecutar; resultados de referencia en `evidencias/` |
| `pentaho/` | Job KJB, transformaciones KTR y ejecución en Windows |
| `powerbi/` | Proyecto PBIP/PBIR, modelo, Power Query y medidas DAX |
| `modelos/` | Modelos entrenados de referencia, regenerables |
| `evidencias/` | Métricas, perfiles, gráficos y registros de las ejecuciones |
| `docs/` | Guías y trazabilidad |

**Estado:** Python y SQLite se reproducen automáticamente. Pentaho y Power BI tienen comprobaciones de estructura, pero siguen pendientes la ejecución real en Spoon/Kitchen, la apertura en Desktop, el PBIX y las capturas nativas. Consulta la matriz de evidencias antes de presentar la entrega como completa.

## Fuentes

- Chen (2015), [Online Retail, UCI](https://doi.org/10.24432/C5BW33), licencia CC BY 4.0; importes en GBP.
- [Hoja proporcionada para el curso](https://docs.google.com/spreadsheets/d/1PaHUYIpdg1RiEf09nbtdFLS1B9aT8cFK/edit), conservada en `productos_original.xlsx`; no se declara licencia ni moneda en la fuente. Sus importes se analizan por separado.
