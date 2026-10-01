# Instalación y primera ejecución

## 1. Descargar el proyecto

En [GitHub](https://github.com/manuel482/prueba-final-mineria), pulsa **Code → Download ZIP** y extrae una sola vez. Abre PowerShell en la carpeta que contiene `README.md`, `requirements.txt`, `src` y `data`. El nombre de la carpeta puede terminar en `-main`; no necesitas cambiarlo ni crear otra carpeta `ProyectoKDD` dentro.

Esta versión publica código y guías directamente. Los binarios se preparan con `src/restaurar_archivos.py`, que usa las 23 partes de `entrega/` y verifica sus hashes; no debes extraer manualmente ese paquete sobre el proyecto ni usar sus guías antiguas. Si conservas una descarga anterior, trabaja en una carpeta nueva para no mezclar versiones.

GitHub conserva un paquete de binarios: los dos Excel, las figuras y los modelos se comprobaron idénticos a la última versión del ZIP y se preparan con el comando del paso 2. El pipeline crea los CSV originales y `data/proyecto_kdd.sqlite`. Si recibiste un ZIP completo generado por `src/empaquetar.py`, este puede incluir la base ya calculada; compruébala antes de usarla.

## 2. Requisitos

- Python **3.12 de 64 bits**, versión usada para la reproducción. El código de empaquetado requiere como mínimo Python 3.11.
- Espacio libre recomendado: **3 GB**, para fuentes, SQLite, entorno y un ZIP adicional.
- Conexión a Internet para instalar dependencias. Los dos Excel están en el paquete incluido; no se descargan desde sitios externos.
- SQLite viene integrado en Python. No hacen falta MySQL ni SQL Server.
- Pentaho, Java y Power BI se necesitan únicamente para las pruebas de sus respectivas aplicaciones.

En Windows confirma el intérprete:

```powershell
py -3.12 --version
py -3.12 src\restaurar_archivos.py
py -3.12 src\verificar_entrega.py --solo-fuentes --archivos
```

La preparación y la comprobación utilizan solo Python estándar. La comprobación y debe terminar en `RESULTADO: OK`. Revisa fuentes, estructura y hashes de la descarga; todavía no comprueba una ejecución del ETL. Si `py` no existe, instala Python y vuelve a abrir la terminal. Puedes sustituir `py -3.12` por `python` cuando `python --version` confirme la versión correcta.

## 3. Entorno y dependencias

Desde la raíz del proyecto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-verificado.txt
```

Se usa directamente el ejecutable del entorno para evitar problemas con la activación de PowerShell. `requirements-verificado.txt` fija las seis dependencias directas usadas en la reproducción; no fija todas las dependencias transitivas. `requirements.txt` conserva rangos compatibles como alternativa. Si cambias versiones, vuelve a entrenar los modelos antes de cargar los `.joblib`.

## 4. Crear la base y verificar

```powershell
.\.venv\Scripts\python.exe src\pipeline.py --stage all
.\.venv\Scripts\python.exe src\verificar_entrega.py --json evidencias\comprobacion_local.json
```

**`all` sí incluye `extract` en esta versión.** Lee los Excel, genera ambos CSV y recorre Bronze, Silver, Gold, minería, verificación y notificación local. La extracción de cientos de miles de filas puede tardar varios minutos. Revisa `evidencias/pipeline.log` y espera el código de salida 0; en PowerShell se consulta con `$LASTEXITCODE` inmediatamente después de cada comando.

El segundo comando debe terminar en `RESULTADO: OK`. La base se abre en modo solo lectura para comprobar integridad, conciliación de filas, claves y totales. Puedes abrirla con un cliente SQLite y ejecutar `sql/04_consultas.sql`. No crees una base vacía manualmente.

Al repetir el pipeline se reemplazan las tablas, modelos y evidencias. Conserva una copia de la base si necesitas comparar ejecuciones, cierra aplicaciones que la estén usando y no actualices Power BI durante la carga. La ejecución completa construye SQLite en una carpeta temporal y reemplaza la base de destino solo después de verificarla. Los CSV, modelos y evidencias se actualizan durante las etapas; si falla, corrige el error y repite el proceso completo.

## 5. Linux o macOS

Con Python 3.12 instalado, desde la raíz:

```bash
python3.12 src/restaurar_archivos.py
python3.12 src/verificar_entrega.py --solo-fuentes --archivos
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements-verificado.txt
./.venv/bin/python src/pipeline.py --stage all
./.venv/bin/python src/verificar_entrega.py --json evidencias/comprobacion_local.json
```

En algunas distribuciones Linux hay que instalar previamente el componente `venv` de Python. Los scripts Windows de Pentaho y su programación de tareas no se ejecutan en Linux/macOS. La preparación de Power BI Desktop descrita más abajo corresponde a Windows.

## 6. Notebook y ejecución de Persona D

Después de crear y verificar la base:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m jupyter lab notebooks\Proyecto_KDD.ipynb
```

Selecciona el kernel de este entorno y ejecuta las celdas en orden. El notebook busca la raíz del proyecto desde su carpeta y abre SQLite en modo solo lectura.

Para la integración de Manuel, la vía recomendada es ejecutar automáticamente el notebook y guardar las salidas visibles en el mismo archivo:

```powershell
.\.venv\Scripts\python.exe src\persona_d_entrega.py --sin-pipeline
```

Si todavía no se ha generado la base común, elimina `--sin-pipeline`. El script también crea una captura del dataset original, una evidencia visual y textual de consultas SQL y un resumen con SHA-256/tamaño de la base que debe compartirse por Drive con el resto del equipo.

## 7. Pentaho: configuración y prueba nativa

Instala Pentaho Data Integration con el Java que exige tu distribución. Localiza `Spoon.bat` y `Kitchen.bat`. Añade un controlador JDBC SQLite compatible que exponga `org.sqlite.JDBC`, junto a las dependencias exigidas por ese controlador, y reinicia Spoon.

1. Abre `pentaho/proyecto_completo.kjb` en Spoon.
2. Define `PROJECT_DIR` con la ruta absoluta de esta carpeta y `PYTHON_EXE` con la de `.venv\Scripts\python.exe`. Las rutas `C:/ProyectoKDD` del XML son ejemplos.
3. Abre los dos KTR y prueba la conexión `SQLite_Proyecto`, las rutas CSV y los tipos de campos. Los CSV deben existir tras el paso 4.
4. Ejecuta el job completo. Revisa filas cargadas y **Execution Results** de cada entrada. Las transformaciones sustituyen su tabla Bronze; el job termina recalculando las otras capas.
5. Para probar Kitchen desde PowerShell:

```powershell
$env:PDI_DIR = 'C:\ruta\a\data-integration'
cmd /c .\pentaho\ejecutar_windows.cmd
$LASTEXITCODE
.\.venv\Scripts\python.exe src\verificar_entrega.py
```

Exige salida 0 y revisa `evidencias/pentaho_real.log`. Después de una ejecución manual correcta, `pentaho/programar_windows.ps1` permite registrar una tarea diaria a las 08:00 para tu usuario Windows. Ejecuta ese script solo si deseas programarla; verifica una ejecución real en el Programador de tareas. El repositorio no instala ninguna tarea por sí mismo.

## 8. Power BI Desktop: configuración y prueba nativa

1. Instala Power BI Desktop en Windows y un controlador SQLite ODBC de **64 bits**.
2. Crea el DSN **ProyectoKDD** en **Orígenes de datos ODBC (64 bits)**, apuntando a la ruta absoluta de `data\proyecto_kdd.sqlite` ya generada y verificada.
3. Prueba **Obtener datos → ODBC → ProyectoKDD** y comprueba que puedes leer `gold_retail` y `gold_ventas_productos`.
4. Abre `powerbi\ProyectoKDD.pbip`. Revisa tablas, relaciones, medidas y las cuatro páginas. El modo de conexión es **Import**; debes pulsar **Actualizar** después de modificar la base.
5. Para el ejercicio Excel independiente, cambia la ruta de ejemplo de `powerbi\ejercicios_power_query.m`. No dupliques las ventas ya importadas desde SQL.
6. Contrasta los totales con `evidencias\kpis.json`. Guarda `ProyectoKDD.pbix` desde Desktop y captura páginas, vista Modelo y Power Query.

El PBIP/PBIR está preparado, pero no tiene apertura nativa comprobada. Si Desktop no lo admite, registra el error y corrige o reconstruye el modelo usando `model.bim`, `medidas.dax` y las consultas M. No presentes el proyecto JSON como un PBIX validado.

Referencias de producto: [Pentaho](https://docs.pentaho.com/install/pentaho-configuration) y [proyectos Power BI Desktop](https://learn.microsoft.com/es-es/power-bi/developer/projects/projects-overview).
