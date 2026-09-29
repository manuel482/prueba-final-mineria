-- SQLite. Agregaciones analíticas ejecutadas después de cargar Gold.
DROP VIEW IF EXISTS gold_retail_mensual;
CREATE VIEW gold_retail_mensual AS
SELECT substr(fecha,1,7) AS mes, pais, SUM(importe) AS venta_neta,
 SUM(venta_bruta) AS venta_bruta, SUM(devolucion) AS devoluciones,
 COUNT(DISTINCT InvoiceNo) AS facturas, COUNT(*) AS lineas
FROM gold_retail GROUP BY substr(fecha,1,7), pais;
DROP VIEW IF EXISTS gold_producto_mensual;
CREATE VIEW gold_producto_mensual AS
SELECT substr(fecha,1,7) AS mes, categoria, sucursal,
 SUM(venta) AS venta, SUM(costos) AS costos, SUM(utilidad) AS utilidad,
 SUM(cantidad) AS cantidad,
 SUM(utilidad)/NULLIF(SUM(venta),0) AS margen
FROM gold_ventas_productos GROUP BY substr(fecha,1,7), categoria, sucursal;
CREATE INDEX IF NOT EXISTS ix_retail_fecha ON gold_retail(fecha);
CREATE INDEX IF NOT EXISTS ix_retail_stock ON gold_retail(stock_key);
CREATE INDEX IF NOT EXISTS ix_ventas_fecha ON gold_ventas_productos(fecha);
CREATE INDEX IF NOT EXISTS ix_ventas_producto ON gold_ventas_productos(producto_key);
CREATE UNIQUE INDEX IF NOT EXISTS ix_dim_producto ON dim_productos(producto_key);
CREATE UNIQUE INDEX IF NOT EXISTS ix_dim_fecha ON dim_fecha(fecha);
CREATE UNIQUE INDEX IF NOT EXISTS ix_dim_retail ON dim_retail_producto(stock_key);
