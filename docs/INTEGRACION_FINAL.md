# Integración final del informe · Proyecto KDD

## Integrantes

- Manuel Mora — 100065865
- Stephany Ángeles — 100063069
- Erick Reynoso Torres — 100068266
- Enmanuel Jiménez — 100066650

## Soporte e integración · Persona D

Manuel Mora tiene a su cargo la ejecución completa del pipeline, la validación de la base SQLite común, el apoyo de instalación a los integrantes que trabajan con Pentaho y Power BI, la ejecución del notebook con salidas visibles, la captura del dataset original y de consultas SQL de validación, y la consolidación de las evidencias finales.

La base `data/proyecto_kdd.sqlite` se genera a partir de las fuentes originales y se valida antes de compartirse por Drive. De esta manera, los demás integrantes pueden trabajar sobre la misma instantánea de datos sin repetir la construcción de todas las capas.

## Implicaciones de la minería de datos en las empresas

La minería de datos es una herramienta fundamental en el mundo empresarial actual, ya que permite extraer información valiosa a partir de grandes volúmenes de datos. Su importancia radica en la capacidad de identificar patrones, tendencias y relaciones ocultas que no son evidentes a simple vista, lo cual facilita la toma de decisiones estratégicas más informadas.

En las empresas, la minería de datos tiene múltiples implicaciones. En primer lugar, ayuda a mejorar la eficiencia operativa mediante el análisis de procesos internos, detectando áreas de mejora y optimización. Por ejemplo, permite identificar cuellos de botella en la producción o analizar el comportamiento de los clientes para ofrecer productos o servicios más personalizados.

Además, la minería de datos es fundamental para mejorar la competitividad en el mercado. Al comprender mejor las preferencias de los consumidores y predecir comportamientos futuros, las empresas pueden diseñar campañas de marketing más efectivas, anticipar cambios en la demanda e identificar nuevas oportunidades de negocio.

Otra implicación importante es la gestión de riesgos. Con técnicas avanzadas de minería de datos, las organizaciones pueden detectar posibles fraudes, anomalías financieras o incluso prever fallos en equipos críticos, minimizando así pérdidas y costos.

## Evidencias que se integran a la entrega

La entrega final debe incorporar las salidas visibles del notebook, una muestra del dataset original, consultas SQL de control, resultados del pipeline y verificador, además de las pruebas nativas de Pentaho y Power BI generadas en los equipos que ejecutan esas aplicaciones.

Para producir automáticamente la parte reproducible de Persona D se utiliza:

```powershell
.\.venv\Scripts\python.exe src\persona_d_entrega.py
```

El detalle del procedimiento está en `docs/PERSONA_D_MANUEL.md`.
