CREATE UNIQUE INDEX ix_dim_fecha ON dim_fecha(fecha);
CREATE UNIQUE INDEX ix_dim_producto ON dim_productos(producto_key);
CREATE UNIQUE INDEX ix_dim_retail ON dim_retail_producto(stock_key);
CREATE INDEX ix_retail_fecha ON gold_retail(fecha);
CREATE INDEX ix_retail_stock ON gold_retail(stock_key);
CREATE INDEX ix_ventas_fecha ON gold_ventas_productos(fecha);
CREATE INDEX ix_ventas_producto ON gold_ventas_productos(producto_key);
CREATE TABLE "bronze_productos" (
"Fecha Venta" TEXT,
  "Nit" TEXT,
  "Nombre Cliente" TEXT,
  "Tipo Cliente" TEXT,
  "Sucursal" TEXT,
  "Cod_Depto" TEXT,
  "Cod_Municipio" TEXT,
  "Cod_Vendedor" TEXT,
  "Cod_Categoria" TEXT,
  "Nombre Categoría" TEXT,
  "Cod_Linea" TEXT,
  "Nombre Linea" TEXT,
  "Cod_Producto" TEXT,
  "Cantidad" TEXT,
  "Precio Unit" TEXT,
  "Costo Unit" TEXT,
  "Venta" TEXT,
  "Costos" TEXT
);
CREATE TABLE "bronze_retail" (
"InvoiceNo" TEXT,
  "StockCode" TEXT,
  "Description" TEXT,
  "Quantity" TEXT,
  "InvoiceDate" TEXT,
  "UnitPrice" TEXT,
  "CustomerID" TEXT,
  "Country" TEXT
);
CREATE TABLE "dim_cliente" (
"customer_key" TEXT
);
CREATE TABLE "dim_fecha" (
"fecha" TEXT,
  "ano" INTEGER,
  "trimestre" INTEGER,
  "mes" INTEGER,
  "dia" INTEGER,
  "ano_mes" TEXT
);
CREATE TABLE "dim_pais" (
"pais" TEXT
);
CREATE TABLE "dim_productos" (
"producto_key" TEXT,
  "cod_producto" TEXT,
  "cod_categoria" TEXT,
  "categoria" TEXT,
  "cod_linea" TEXT,
  "linea" TEXT,
  "precio_ultimo_observado" REAL,
  "fecha_precio" TEXT,
  "nombre_producto" TEXT,
  "stock" TEXT
);
CREATE TABLE "dim_retail_producto" (
"stock_key" TEXT,
  "producto" TEXT
);
CREATE TABLE "gold_features_ml" (
"CustomerID" TEXT,
  "corte" TEXT,
  "num__recencia" REAL,
  "num__frecuencia" REAL,
  "num__monetario" REAL,
  "num__unidades" REAL,
  "num__ticket" REAL,
  "cat__pais_Australia" REAL,
  "cat__pais_Austria" REAL,
  "cat__pais_Bahrain" REAL,
  "cat__pais_Belgium" REAL,
  "cat__pais_Brazil" REAL,
  "cat__pais_Canada" REAL,
  "cat__pais_Channel Islands" REAL,
  "cat__pais_Cyprus" REAL,
  "cat__pais_Czech Republic" REAL,
  "cat__pais_Denmark" REAL,
  "cat__pais_EIRE" REAL,
  "cat__pais_European Community" REAL,
  "cat__pais_Finland" REAL,
  "cat__pais_France" REAL,
  "cat__pais_Germany" REAL,
  "cat__pais_Greece" REAL,
  "cat__pais_Iceland" REAL,
  "cat__pais_Israel" REAL,
  "cat__pais_Italy" REAL,
  "cat__pais_Japan" REAL,
  "cat__pais_Malta" REAL,
  "cat__pais_Netherlands" REAL,
  "cat__pais_Norway" REAL,
  "cat__pais_Poland" REAL,
  "cat__pais_Portugal" REAL,
  "cat__pais_Saudi Arabia" REAL,
  "cat__pais_Singapore" REAL,
  "cat__pais_Spain" REAL,
  "cat__pais_Sweden" REAL,
  "cat__pais_Switzerland" REAL,
  "cat__pais_USA" REAL,
  "cat__pais_United Arab Emirates" REAL,
  "cat__pais_United Kingdom" REAL,
  "cat__pais_Unspecified" REAL
);
CREATE TABLE "gold_predicciones" (
"CustomerID" TEXT,
  "frecuencia" INTEGER,
  "monetario" REAL,
  "unidades" INTEGER,
  "pais" TEXT,
  "recencia" REAL,
  "ticket" REAL,
  "gasto_futuro" REAL,
  "recompra" INTEGER,
  "corte" TEXT,
  "prob_recompra" REAL,
  "gasto_predicho" REAL
);
CREATE TABLE "gold_retail" (
"source_row" INTEGER,
  "InvoiceNo" TEXT,
  "StockCode" TEXT,
  "Description" TEXT,
  "Quantity" INTEGER,
  "InvoiceDate" TIMESTAMP,
  "UnitPrice" REAL,
  "CustomerID" TEXT,
  "Country" TEXT,
  "is_cancelled" INTEGER,
  "is_return" INTEGER,
  "is_outlier" INTEGER,
  "fecha" TEXT,
  "importe" REAL,
  "venta_bruta" REAL,
  "devolucion" REAL,
  "customer_key" TEXT,
  "stock_key" TEXT,
  "pais" TEXT,
  "tramo_cantidad" TEXT
);
CREATE TABLE "gold_segmentos" (
"CustomerID" TEXT,
  "recencia" REAL,
  "frecuencia" INTEGER,
  "monetario" REAL,
  "cluster" INTEGER
);
CREATE TABLE "gold_ventas_productos" (
"source_row" INTEGER,
  "fecha" TEXT,
  "nit" TEXT,
  "cliente" TEXT,
  "tipo_cliente" TEXT,
  "sucursal" TEXT,
  "cod_depto" TEXT,
  "cod_municipio" TEXT,
  "cod_vendedor" TEXT,
  "cod_categoria" TEXT,
  "categoria" TEXT,
  "cod_linea" TEXT,
  "linea" TEXT,
  "cod_producto" TEXT,
  "cantidad" INTEGER,
  "precio_unit" REAL,
  "costo_unit" REAL,
  "venta" REAL,
  "costos" REAL,
  "duplicado_candidato" INTEGER,
  "diferencia_venta" REAL,
  "diferencia_costos" REAL,
  "utilidad" REAL,
  "margen" REAL,
  "producto_key" TEXT
);
CREATE TABLE "silver_productos" (
"source_row" INTEGER,
  "fecha" TIMESTAMP,
  "nit" TEXT,
  "cliente" TEXT,
  "tipo_cliente" TEXT,
  "sucursal" TEXT,
  "cod_depto" TEXT,
  "cod_municipio" TEXT,
  "cod_vendedor" TEXT,
  "cod_categoria" TEXT,
  "categoria" TEXT,
  "cod_linea" TEXT,
  "linea" TEXT,
  "cod_producto" TEXT,
  "cantidad" INTEGER,
  "precio_unit" REAL,
  "costo_unit" REAL,
  "venta" REAL,
  "costos" REAL,
  "duplicado_candidato" INTEGER,
  "diferencia_venta" REAL,
  "diferencia_costos" REAL
);
CREATE TABLE "silver_productos_rechazos" (
"source_row" INTEGER,
  "fecha" TIMESTAMP,
  "nit" TEXT,
  "cliente" TEXT,
  "tipo_cliente" TEXT,
  "sucursal" TEXT,
  "cod_depto" TEXT,
  "cod_municipio" TEXT,
  "cod_vendedor" TEXT,
  "cod_categoria" TEXT,
  "categoria" TEXT,
  "cod_linea" TEXT,
  "linea" TEXT,
  "cod_producto" TEXT,
  "cantidad" INTEGER,
  "precio_unit" REAL,
  "costo_unit" REAL,
  "venta" REAL,
  "costos" REAL,
  "duplicado_candidato" INTEGER
);
CREATE TABLE "silver_retail" (
"source_row" INTEGER,
  "InvoiceNo" TEXT,
  "StockCode" TEXT,
  "Description" TEXT,
  "Quantity" INTEGER,
  "InvoiceDate" TIMESTAMP,
  "UnitPrice" REAL,
  "CustomerID" TEXT,
  "Country" TEXT,
  "is_cancelled" INTEGER,
  "is_return" INTEGER,
  "is_outlier" INTEGER
);
CREATE TABLE "silver_retail_rechazos" (
"source_row" INTEGER,
  "InvoiceNo" TEXT,
  "StockCode" TEXT,
  "Description" TEXT,
  "Quantity" INTEGER,
  "InvoiceDate" TIMESTAMP,
  "UnitPrice" REAL,
  "CustomerID" REAL,
  "Country" TEXT,
  "reject_reason" TEXT
);
CREATE VIEW gold_producto_mensual AS
SELECT substr(fecha,1,7) AS mes, categoria, sucursal,
 SUM(venta) AS venta, SUM(costos) AS costos, SUM(utilidad) AS utilidad,
 SUM(cantidad) AS cantidad,
 SUM(utilidad)/NULLIF(SUM(venta),0) AS margen
FROM gold_ventas_productos GROUP BY substr(fecha,1,7), categoria, sucursal;
CREATE VIEW gold_retail_mensual AS
SELECT substr(fecha,1,7) AS mes, pais, SUM(importe) AS venta_neta,
 SUM(venta_bruta) AS venta_bruta, SUM(devolucion) AS devoluciones,
 COUNT(DISTINCT InvoiceNo) AS facturas, COUNT(*) AS lineas
FROM gold_retail GROUP BY substr(fecha,1,7), pais;