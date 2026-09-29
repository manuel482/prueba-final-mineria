# Paquete de archivos binarios

Estas 23 partes existentes se conservan para preparar los Excel, figuras y modelos sin duplicar transferencias. **No extraigas el paquete entero sobre el proyecto:** contiene también una versión anterior de scripts y guías.

Desde la raíz ejecuta `python src/restaurar_archivos.py`. El script comprueba el SHA-256 del paquete y prepara únicamente 16 archivos definidos en `docs/ARCHIVOS_BINARIOS.json`. Se verificó que esos 16 archivos son idénticos a los de `ProyectoKDD_Entrega.zip` versión 2. Los archivos ya presentes se conservan.

Los scripts y las guías vigentes son los publicados directamente en `src/` y `docs/`. La base SQLite y los CSV se recalculan con `python src/pipeline.py --stage all`.
