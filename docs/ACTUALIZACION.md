# Actualización del 28 de septiembre de 2026

## Procedencia

Base de esta publicación: `ProyectoKDD_Entrega.zip`, versión 2, modificada el **27 de septiembre de 2026 a las 17:11:51 UTC**.

- Tamaño del ZIP: **146 947 357 bytes**.
- SHA-256: `b8273fb8aad23bab26e25b5ca79c3f0834e892640ae0eec4db06257220241124`.
- La revisión del ZIP original completó **124 controles, cero errores**: fuentes, manifiesto, integridad de la base y conciliación.
- Se conservaron los Excel originales y el informe Word. La metodología y los resultados de referencia provienen de esa entrega.

El repositorio solicitado como `manuel482/Aplicacion-de-prueba-supermercado` tiene ahora el nombre `manuel482/prueba-final-mineria`. GitHub confirmó la misma identidad de repositorio; esta publicación mantiene su historial.

## Cambios

1. Proyecto publicado directamente en carpetas navegables desde GitHub; se conserva el paquete existente en `entrega/` únicamente como fuente de binarios. Se verificó por SHA-256 que los 16 archivos restaurados son idénticos a los de la última versión del ZIP. Se reemplaza el procedimiento antiguo por una preparación selectiva que no sobrescribe scripts ni guías.
2. SQLite y los dos CSV originales se generan localmente desde los Excel. Se añaden `.gitignore` y reglas de finales de línea para evitar publicar cachés y archivos regenerables grandes.
3. `--stage all` incluye la extracción de Excel. Una descarga nueva ya no depende de CSV ni de una base preexistente.
4. La ejecución completa escribe SQLite en una carpeta temporal y solo reemplaza la base de destino después de verificar integridad y relaciones. Los resultados auxiliares todavía se actualizan por etapa.
5. El estado pasa a `EN_PROCESO` al comenzar y a `ERROR` si falla, evitando conservar un `OK` de una ejecución anterior.
6. El verificador añade modo `--solo-fuentes`, controles de KPI contra SQL y validación sintáctica XML/JSON. Las comprobaciones de estructura no se presentan como ejecución nativa.
7. El notebook encuentra la raíz sin depender del nombre de la carpeta y abre SQLite en modo solo lectura. Se publica sin salidas guardadas para que se ejecute en orden.
8. Instalación, ejecución y comprobación reescritas para esta distribución, con pasos Windows y Linux/macOS. Se separan dependencias del pipeline y del notebook y se registran las versiones directas usadas.
9. El empaquetador valida los resultados, incluye la base generada y crea un manifiesto dentro del ZIP sin modificar el manifiesto del repositorio.

Consulta [estado y evidencias](ESTADO_Y_EVIDENCIAS.md) para el alcance de las pruebas y los pendientes nativos.

## Muestras públicas

Las muestras y perfiles públicos excluyen NIT, nombres de clientes, identificadores de clientes y facturas y códigos de vendedor. El generador aplica la misma exclusión al repetir el pipeline. Los controles de volumen y las métricas analíticas no cambian.
