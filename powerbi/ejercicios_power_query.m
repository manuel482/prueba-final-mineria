// Consultas independientes. Pegue cada bloque en una consulta en blanco distinta.
// 1. ExcelOriginal: conserva el original para el ejercicio de importación.
let
    Origen = Excel.Workbook(File.Contents("C:\ProyectoKDD\data\productos_original.xlsx"), null, true),
    Hoja = Origen{[Item="BD",Kind="Sheet"]}[Data],
    Encabezados = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Encabezados, {{"Fecha Venta",type date},{"Cod_Producto",type text},{"Cod_Depto",type text},{"Cod_Municipio",type text},{"Cantidad",Int64.Type},{"Precio Unit",type number},{"Venta",type number},{"Costos",type number}}),
    Renombradas = Table.RenameColumns(Tipos,{{"Cod_Producto","codigo_producto"}}),
    Validar = Table.SelectRows(Renombradas, each [codigo_producto] <> null and [Fecha Venta] <> null)
in Validar

// 2. SQLCondicional: filtro ejecutado dentro de la base SQL.
let
    Origen = Odbc.Query("dsn=ProyectoKDD", "SELECT * FROM gold_ventas_productos WHERE fecha >= '2019-01-01'"),
    Tipos = Table.TransformColumnTypes(Origen,{{"fecha",type date},{"venta",type number},{"costos",type number}})
in Tipos

// 3. AgrupacionSQL: consulta de agregación de la capa Gold.
let Origen = Odbc.Query("dsn=ProyectoKDD", "SELECT categoria, SUM(venta) AS venta, SUM(costos) AS costos FROM gold_ventas_productos GROUP BY categoria")
in Origen

// 4. FusionConsultas: Ventas y Productos son las consultas del modelo PBIP.
let
    Fusion = Table.NestedJoin(Ventas,{"producto_key"},Productos,{"producto_key"},"DimProducto",JoinKind.LeftOuter),
    Expandida = Table.ExpandTableColumn(Fusion,"DimProducto",{"categoria"},{"categoria_dimension"})
in Expandida
// Mantener estas consultas de demostración con carga deshabilitada para no duplicar las ventas.
