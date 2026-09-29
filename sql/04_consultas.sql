-- Evidencia del volumen y conciliación.
SELECT COUNT(*) AS filas_bronze FROM bronze_retail;
SELECT COUNT(*) AS filas_silver FROM silver_retail;
SELECT COUNT(*) AS rechazadas FROM silver_retail_rechazos;
SELECT reject_reason, COUNT(*) AS filas FROM silver_retail_rechazos GROUP BY reject_reason;
SELECT SUM(importe) AS neto_gbp, SUM(venta_bruta) AS bruto_gbp,
       SUM(devolucion) AS devoluciones_gbp FROM gold_retail;
SELECT * FROM gold_retail_mensual ORDER BY mes,pais;
SELECT * FROM gold_producto_mensual ORDER BY mes,categoria,sucursal;
SELECT cod_producto, categoria, nombre_producto, stock, precio_ultimo_observado
FROM dim_productos ORDER BY cod_producto;
SELECT * FROM silver_productos WHERE ABS(diferencia_costos)>0.01;
SELECT * FROM gold_segmentos ORDER BY cluster,monetario DESC;
-- Categoría seleccionada por parámetro (ejemplo literal).
SELECT SUM(venta) FROM gold_ventas_productos WHERE categoria IN ('LACTEA','CARNICA');
-- Validación de claves: debe devolver cero filas.
SELECT producto_key,COUNT(*) FROM dim_productos GROUP BY producto_key HAVING COUNT(*)>1;
