"""Preparación para Spoon: valida los CSV sin alterar valores, crea tablas vacías."""
from pathlib import Path
import sqlite3,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
for name,required,numbers,date in [('retail',['InvoiceNo','StockCode','Country','InvoiceDate'],['Quantity','UnitPrice'],'InvoiceDate'),('productos',['Cod_Producto','Fecha Venta','Venta'],['Cantidad','Precio Unit','Venta','Costos'],'Fecha Venta')]:
 d=pd.read_csv(ROOT/'data'/f'{name}_original.csv',dtype=str,keep_default_na=False)
 assert len(d)>100000
 for col in required: assert d[col].ne('').all(),f'Campo requerido vacío: {col}'
 for col in numbers: assert pd.to_numeric(d[col],errors='coerce').notna().all(),f'Tipo numérico inválido: {col}'
 assert pd.to_datetime(d[date],errors='coerce').notna().all()
 print(f'VALIDADO {name}: {len(d)} filas; valores fuente sin modificación')
with sqlite3.connect(ROOT/'data/proyecto_kdd.sqlite') as c:c.executescript((ROOT/'sql/01_bronze.sql').read_text())
