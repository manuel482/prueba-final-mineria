# Estado y evidencias

| Componente | Archivos publicados | Alcance verificable | Pendiente |
| --- | --- | --- | --- |
| Fuentes | Dos Excel, hashes, perfiles y muestras | Integridad de originales y volumen | Capturas de los Excel abiertos para la entrega académica |
| Python / SQLite | ETL, minería, esquemas, métricas y figuras | Reconstrucción desde Excel y verificador de integridad, filas, relaciones y KPI | Capturas de consultas si las exige la consigna |
| Pentaho Bronze | KJB, dos KTR, conexión y launcher | XML bien formado | Ejecutar Spoon/Kitchen, guardar log real y capturas |
| Automatización | Script para tarea Windows | Revisión de configuración | Registrar y probar la tarea en el equipo del estudiante |
| Notebook | Notebook para ejecutar; métricas y gráficos en evidencias | Código y consultas revisables; requiere SQLite generado | Ejecutar todas las celdas en el entorno de Jupyter del estudiante |
| Power BI | PBIP/PBIR, modelo, M, DAX y cuatro páginas | JSON sintácticamente válido y tablas fuente calculadas | Abrir, actualizar y comprobar en Desktop; guardar PBIX y capturas |
| Entrega ZIP | Empaquetador y manifiesto | Validación previa y control de integridad del ZIP generado | Generar el ZIP tras una ejecución local si se requiere entrega comprimida |

El ZIP original pasó 124 controles sin errores. La evidencia de la nueva reproducción se registra en `evidencias/comprobacion_publicacion.json` y `evidencias/reproduccion_publicacion.json`.

**Límite:** el repositorio no contiene un PBIX validado en Desktop, capturas nativas de Spoon ni una tarea realmente programada. Los logs de Python y las validaciones XML/JSON no sustituyen esas pruebas.

La preparación de los 16 binarios se comprobó en una carpeta vacía, usando las partes publicadas y comparando los hashes con la última versión del ZIP.
