# Persona D · Manuel Mora · Soporte e integración final

## Integrantes del equipo

| Integrante | Matrícula |
| --- | --- |
| Manuel Mora | 100065865 |
| Stephany Ángeles | 100063069 |
| Erick Reynoso Torres | 100068266 |
| Enmanuel Jiménez | 100066650 |

## Responsabilidades de Manuel

Manuel actúa como **Persona D: soporte e integración**. Su función es asegurar que todos trabajen sobre una misma base validada, que el notebook conserve las salidas visibles y que las evidencias finales puedan reproducirse.

### Primer día

1. Ejecutar el pipeline completo.
2. Verificar que el resultado sea `OK`.
3. Compartir `data/proyecto_kdd.sqlite` por Google Drive con A, B y C. La base ronda los 420 MB y se mantiene fuera de GitHub.
4. Registrar el tamaño y SHA-256 de la base compartida para que todos validen que usan el mismo archivo.

Comandos:

```powershell
.\.venv\Scripts\python.exe src\pipeline.py --stage all
.\.venv\Scripts\python.exe src\verificar_entrega.py --json evidencias\comprobacion_local.json
.\.venv\Scripts\python.exe src\persona_d_entrega.py --sin-pipeline
```

También puede hacerse todo con:

```powershell
.\.venv\Scripts\python.exe src\persona_d_entrega.py
```

## Soporte para A y B

### Python y rutas

- Trabajar siempre desde la raíz del repositorio.
- Usar el Python del entorno: `.venv\Scripts\python.exe`.
- La base común debe quedar en `data\proyecto_kdd.sqlite`.
- No crear bases SQLite vacías para resolver errores de ruta.

### Pentaho

- Instalar Java compatible con la versión de Pentaho Data Integration.
- Instalar un driver JDBC SQLite que exponga `org.sqlite.JDBC`.
- Definir `PROJECT_DIR` con la ruta absoluta del proyecto.
- Definir `PYTHON_EXE` con la ruta absoluta de `.venv\Scripts\python.exe`.
- Probar la conexión antes de ejecutar el KJB.

### Power BI

- Usar Power BI Desktop de 64 bits.
- Instalar un controlador SQLite ODBC de 64 bits.
- Crear el DSN **ProyectoKDD** apuntando a `data\proyecto_kdd.sqlite`.
- Probar primero `gold_retail` y `gold_ventas_productos` mediante **Obtener datos → ODBC**.
- Abrir `powerbi\ProyectoKDD.pbip`, actualizar y validar los KPI.

## Notebook con salidas visibles

El script `src/persona_d_entrega.py` ejecuta el notebook en el mismo archivo mediante `jupyter nbconvert`. Al finalizar, `notebooks/Proyecto_KDD.ipynb` conserva los `execution_count` y los resultados de las celdas.

La ejecución requiere que `data/proyecto_kdd.sqlite` exista y haya pasado el verificador. Si se desea repetir únicamente esta parte:

```powershell
.\.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace notebooks\Proyecto_KDD.ipynb --ExecutePreprocessor.timeout=-1
```

## Evidencias de Manuel

El script genera localmente:

- `evidencias/persona_d_dataset_original.png`: vista del dataset original.
- `evidencias/persona_d_consultas_sql.png`: consultas SQL de validación.
- `evidencias/persona_d_consultas_sql.txt`: resultados SQL en texto.
- `evidencias/persona_d_resumen.json`: estado de la integración, hash y tamaño de la base.
- Notebook ejecutado con salidas visibles.

Los PNG están excluidos de Git por diseño para evitar publicar capturas con datos sensibles; deben incorporarse al informe/entrega académica de forma controlada.

## Integración del informe

Antes de entregar:

- Unificar las secciones de A, B, C y D.
- Mantener una sola terminología para Bronze, Silver, Gold, KDD, ETL, SQLite, Pentaho y Power BI.
- Incluir los cuatro integrantes y sus matrículas.
- Sustituir notas de trabajo por resultados verificables o por una descripción precisa de la validación local requerida.
- Añadir las capturas del dataset, consultas SQL, notebook, Pentaho y Power BI cuando se hayan generado en el equipo correspondiente.
- Contrastar los resultados con `docs/GUIA_COMPROBACION.md`.

## Implicaciones empresariales de la minería de datos

La minería de datos es una herramienta fundamental en el mundo empresarial actual, ya que permite extraer información valiosa a partir de grandes volúmenes de datos. Su importancia radica en la capacidad de identificar patrones, tendencias y relaciones ocultas que no son evidentes a simple vista, lo cual facilita la toma de decisiones estratégicas más informadas.

En las empresas, la minería de datos tiene múltiples implicaciones. En primer lugar, ayuda a mejorar la eficiencia operativa mediante el análisis de procesos internos, detectando áreas de mejora y optimización. Por ejemplo, permite identificar cuellos de botella en la producción o analizar el comportamiento de los clientes para ofrecer productos o servicios más personalizados.

Además, la minería de datos es fundamental para mejorar la competitividad en el mercado. Al comprender mejor las preferencias de los consumidores y predecir comportamientos futuros, las empresas pueden diseñar campañas de marketing más efectivas, anticipar cambios en la demanda e identificar nuevas oportunidades de negocio.

Otra implicación importante es la gestión de riesgos. Con técnicas avanzadas de minería de datos, las organizaciones pueden detectar posibles fraudes, anomalías financieras o incluso prever fallos en equipos críticos, minimizando así pérdidas y costos.
