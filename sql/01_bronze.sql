-- SQLite. Bronze conserva las columnas originales como TEXT.
CREATE TABLE IF NOT EXISTS bronze_retail (
"InvoiceNo" TEXT,
"StockCode" TEXT,
"Description" TEXT,
"Quantity" TEXT,
"InvoiceDate" TEXT,
"UnitPrice" TEXT,
"CustomerID" TEXT,
"Country" TEXT
);
CREATE TABLE IF NOT EXISTS bronze_productos (
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