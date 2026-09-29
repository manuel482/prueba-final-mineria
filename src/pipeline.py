"""ETL reproducible. SQLite local; no credenciales. Ejecutar desde cualquier directorio."""
from pathlib import Path
import argparse, sqlite3, json, logging, hashlib, sys, platform, os, tempfile, shutil
from contextlib import closing
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sklearn, joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
 confusion_matrix, RocCurveDisplay, ConfusionMatrixDisplay, mean_absolute_error, mean_squared_error, r2_score, silhouette_score)
ROOT=Path(__file__).resolve().parents[1]
for sub in ['evidencias','modelos','data','sql']: (ROOT/sub).mkdir(exist_ok=True)
DB=Path(os.environ.get('KDD_DB_PATH', str(ROOT/'data/proyecto_kdd.sqlite')))
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(ROOT/'evidencias/pipeline.log',encoding='utf-8')])
plt.rcParams.update({'figure.dpi':140,'font.size':10,'axes.spines.top':False,'axes.spines.right':False})

def js(name, data):
 (ROOT/'evidencias'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def write(df,name,c):
 df.to_sql(name,c,if_exists='replace',index=False,chunksize=10000)
 logging.info('%s: %s filas, %s columnas',name,len(df),len(df.columns))
def savefig(name):
 plt.tight_layout();plt.savefig(ROOT/'evidencias'/name,bbox_inches='tight');plt.close()
def profile(d,name):
 pd.DataFrame({'columna':d.columns,'tipo':d.dtypes.astype(str).values,'nulos':d.isna().sum().values,'unicos':d.nunique().values}).to_csv(ROOT/'evidencias'/f'{name}_metadatos.csv',index=False)
 public=d.drop(columns=['nit','cliente','CustomerID','InvoiceNo','cod_vendedor'],errors='ignore')
 public.describe(include='all').to_csv(ROOT/'evidencias'/f'{name}_perfil.csv')
 public.head(20).to_csv(ROOT/'evidencias'/f'{name}_muestra.csv',index=False)
 return {'filas':len(d),'columnas':len(d.columns),'nulos':d.isna().sum().to_dict(),'duplicados_exactos':int(d.duplicated().sum())}

def extract():
 from restaurar_archivos import restore_missing
 restore_missing()
 for filename,csv in [('Online Retail.xlsx','retail_original.csv'),('productos_original.xlsx','productos_original.csv')]:
  p=ROOT/'data'/filename
  if not p.exists(): raise FileNotFoundError(f'Falta {p}; consultar README')
  logging.info('Extrayendo %s',filename)
  d=pd.read_excel(p,dtype=object);d.to_csv(ROOT/'data'/csv,index=False)
 logging.info('Extracción completada; valores del Excel conservados en CSV con fechas ISO')

def bronze():
 with closing(sqlite3.connect(DB)) as c:
  for name in ['retail','productos']:
   d=pd.read_csv(ROOT/'data'/f'{name}_original.csv',dtype=str,keep_default_na=False)
   write(d,'bronze_'+name,c)
 validate()

def validate():
 with closing(sqlite3.connect(DB)) as c:
  d=pd.read_sql_query('SELECT * FROM bronze_retail',c)
  e=pd.read_sql_query('SELECT * FROM bronze_productos',c)
  assert len(d)>100000 and len(e)>100000
  checks={'retail_filas':len(d),'productos_filas':len(e),'campos_obligatorios_vacios':{},'conversiones_invalidas':{}}
  for col in ['InvoiceNo','StockCode','InvoiceDate','Country']:
   checks['campos_obligatorios_vacios'][col]=int(d[col].fillna('').eq('').sum())
  for col in ['Quantity','UnitPrice']:
   checks['conversiones_invalidas'][col]=int(pd.to_numeric(d[col],errors='coerce').isna().sum())
  checks['conversiones_invalidas']['InvoiceDate']=int(pd.to_datetime(d.InvoiceDate,errors='coerce').isna().sum())
  js('validacion_bronze.json',checks)
  logging.info('Validación Bronze: %s',checks)
  if any(checks['campos_obligatorios_vacios'].values()) or any(checks['conversiones_invalidas'].values()):
   raise ValueError('Validación básica fallida; Bronze preservado para diagnóstico')

def silver():
 with closing(sqlite3.connect(DB)) as c:
  d=pd.read_sql_query('SELECT * FROM bronze_retail',c).replace('',np.nan)
  for col in ['Quantity','UnitPrice','CustomerID']:d[col]=pd.to_numeric(d[col],errors='coerce')
  d['InvoiceDate']=pd.to_datetime(d.InvoiceDate,errors='coerce')
  meta=profile(d,'retail'); d.insert(0,'source_row',np.arange(2,len(d)+2))
  dup=d.duplicated(subset=[x for x in d if x!='source_row'])
  rejects=d.loc[dup].assign(reject_reason='duplicado exacto candidato')
  d=d.loc[~dup].copy()
  invalid=d.InvoiceDate.isna()|d.Quantity.isna()|d.UnitPrice.isna()|d.Quantity.eq(0)|d.UnitPrice.lt(0)|d.InvoiceNo.isna()|d.StockCode.isna()|d.Country.isna()
  rejects=pd.concat([rejects,d.loc[invalid].assign(reject_reason='campo requerido o dominio inválido')])
  d=d.loc[~invalid].copy()
  d['Description']=d.Description.fillna('SIN DESCRIPCION').str.strip()
  d['Country']=d.Country.str.strip()
  # Cliente desconocido permanece NULL; nunca se imputa una identidad.
  d['CustomerID']=d.CustomerID.astype('Int64').astype('string')
  d['is_cancelled']=d.InvoiceNo.astype(str).str.upper().str.startswith('C').astype(int)
  d['is_return']=((d.Quantity<0)|(d.is_cancelled==1)).astype(int)
  q1,q3=d.Quantity.abs().quantile([.25,.75]);upper=float(q3+1.5*(q3-q1))
  p1,p3=d.UnitPrice.quantile([.25,.75]);pupper=float(p3+1.5*(p3-p1))
  d['is_outlier']=((d.Quantity.abs()>upper)|(d.UnitPrice>pupper)).astype(int)
  # Retener importes atípicos: una compra mayorista no equivale a error.
  write(rejects,'silver_retail_rechazos',c);write(d,'silver_retail',c)
  meta.update({'silver_filas':len(d),'rechazos':len(rejects),'outliers_marcados':int(d.is_outlier.sum()),'limite_iqr_cantidad_abs':upper,'limite_iqr_precio':pupper,'precio_cero':int(d.UnitPrice.eq(0).sum()),'devoluciones':int(d.is_return.sum()),'inicio':str(d.InvoiceDate.min()),'fin':str(d.InvoiceDate.max())})
  js('calidad_retail.json',meta)
  e=pd.read_sql_query('SELECT * FROM bronze_productos',c).replace('',np.nan)
  rename=dict(zip(e.columns,['fecha','nit','cliente','tipo_cliente','sucursal','cod_depto','cod_municipio','cod_vendedor','cod_categoria','categoria','cod_linea','linea','cod_producto','cantidad','precio_unit','costo_unit','venta','costos']))
  e=e.rename(columns=rename)
  nums=['cantidad','precio_unit','costo_unit','venta','costos']
  for col in nums:e[col]=pd.to_numeric(e[col],errors='coerce')
  e['fecha']=pd.to_datetime(e.fecha,errors='coerce')
  pm=profile(e,'productos');e.insert(0,'source_row',np.arange(2,len(e)+2))
  # Sin id de factura: coincidencias pueden ser ventas legítimas. Se marcan, no borran.
  e['duplicado_candidato']=e.duplicated(subset=list(rename.values()),keep=False).astype(int)
  invalid=e[['fecha','cod_producto','cantidad','precio_unit','venta','costos']].isna().any(axis=1)
  write(e.loc[invalid],'silver_productos_rechazos',c)
  e=e.loc[~invalid].copy()
  e['diferencia_venta']=e.venta-e.cantidad*e.precio_unit
  e['diferencia_costos']=e.costos-e.cantidad*e.costo_unit
  write(e,'silver_productos',c)
  pm.update({'silver_filas':len(e),'rechazos':int(invalid.sum()),'diferencias_venta_mayores_001':int(e.diferencia_venta.abs().gt(.01).sum()),'diferencias_costos_mayores_001':int(e.diferencia_costos.abs().gt(.01).sum()),'inicio':str(e.fecha.min()),'fin':str(e.fecha.max())})
  js('calidad_productos.json',pm)

def gold():
 with closing(sqlite3.connect(DB)) as c:
  d=pd.read_sql_query('SELECT * FROM silver_retail',c,parse_dates=['InvoiceDate'])
  d['fecha']=d.InvoiceDate.dt.strftime('%Y-%m-%d');d['importe']=d.Quantity*d.UnitPrice
  d['venta_bruta']=np.where(d.Quantity>0,d.importe,0.)
  d['devolucion']=np.where(d.Quantity<0,-d.importe,0.)
  d['customer_key']=d.CustomerID.fillna('DESCONOCIDO')
  d['stock_key']=d.StockCode.astype(str);d['pais']=d.Country
  d['tramo_cantidad']=pd.cut(d.Quantity.abs(),bins=[0,1,5,10,25,100,float('inf')],labels=['01 unidad','02 a 05','06 a 10','11 a 25','26 a 100','Mas de 100']).astype(str)
  write(d,'gold_retail',c)
  products=d.sort_values(['InvoiceDate','source_row']).drop_duplicates('stock_key',keep='last')[['stock_key','Description']].rename(columns={'Description':'producto'})
  write(products,'dim_retail_producto',c)
  write(pd.DataFrame({'pais':sorted(d.pais.unique())}),'dim_pais',c)
  customers=d[['customer_key']].drop_duplicates();write(customers,'dim_cliente',c)
  e=pd.read_sql_query('SELECT * FROM silver_productos',c,parse_dates=['fecha'])
  e['fecha']=e.fecha.dt.strftime('%Y-%m-%d');e['utilidad']=e.venta-e.costos
  e['margen']=np.where(e.venta.ne(0),e.utilidad/e.venta,np.nan)
  write(e,'gold_ventas_productos',c)
  # Clave compuesta: protege frente a un código reutilizado en otra categoría/línea.
  def key(x):return x.cod_producto.astype(str)+'|'+x.cod_categoria.astype(str)+'|'+x.cod_linea.astype(str)
  e['producto_key']=key(e);write(e,'gold_ventas_productos',c)
  latest=e.sort_values(['fecha','source_row']).drop_duplicates('producto_key',keep='last')
  prod=latest[['producto_key','cod_producto','cod_categoria','categoria','cod_linea','linea','precio_unit','fecha']].copy()
  prod=prod.rename(columns={'precio_unit':'precio_ultimo_observado','fecha':'fecha_precio'})
  prod['nombre_producto']=None;prod['stock']=None
  write(prod,'dim_productos',c)
  # Clave y categoría quedan en dimensión; hecho sólo se relaciona por producto_key.
  date_start=min(d.fecha.min(),e.fecha.min())[:4]+'-01-01';date_end=max(d.fecha.max(),e.fecha.max())[:4]+'-12-31'
  times=pd.date_range(date_start,date_end,freq='D')
  dates=pd.DataFrame({'fecha':times.strftime('%Y-%m-%d'),'ano':times.year,'trimestre':times.quarter,'mes':times.month,'dia':times.day,'ano_mes':times.strftime('%Y-%m')})
  write(dates,'dim_fecha',c)
  c.executescript((ROOT/'sql/02_gold.sql').read_text());c.commit()
  for table in ['gold_retail_mensual','gold_producto_mensual','dim_productos','dim_fecha','dim_pais','dim_retail_producto']:
   pd.read_sql_query(f'SELECT * FROM {table}',c).to_csv(ROOT/'data'/f'{table}.csv',index=False)
  js('kpis.json',{'retail':{'venta_neta_gbp':float(d.importe.sum()),'venta_bruta_gbp':float(d.venta_bruta.sum()),'devoluciones_gbp':float(d.devolucion.sum()),'facturas':int(d.InvoiceNo.nunique()),'clientes_identificados':int(d.CustomerID.nunique())},'productos':{'venta':float(e.venta.sum()),'costos':float(e.costos.sum()),'utilidad':float(e.utilidad.sum()),'productos':len(prod),'moneda':'no especificada en el documento'}})
  m=d.groupby(d.InvoiceDate.dt.to_period('M')).importe.sum()
  plt.figure(figsize=(9,3.6));m.plot(marker='o',color='#176b87');plt.title('Ventas netas mensuales de Online Retail');plt.ylabel('GBP');plt.xlabel('Mes');savefig('retail_tendencia.png')
  plt.figure(figsize=(9,3.6));d.groupby('Country').importe.sum().nlargest(10).sort_values().plot.barh(color='#176b87');plt.xlabel('GBP netas');plt.title('Diez países por ventas netas');savefig('retail_paises.png')
  plt.figure(figsize=(9,3.6));np.log1p(d.Quantity.abs()).hist(bins=45,color='#176b87');plt.xlabel('log(1 + cantidad absoluta)');plt.ylabel('Líneas');plt.title('Distribución de cantidades con escala logarítmica');savefig('retail_distribucion.png')
  fig,axs=plt.subplots(1,2,figsize=(10,3.7));e.groupby('categoria').venta.sum().sort_values().plot.barh(ax=axs[0],color='#176b87');axs[0].set_title('Venta por categoría');axs[0].set_xlabel('Unidades monetarias del archivo');e.groupby(e.fecha.str[:7]).venta.sum().plot(ax=axs[1],color='#da9b29');axs[1].set_title('Venta mensual');axs[1].set_xlabel('Mes');savefig('productos_eda.png')
  # Evidencia de datos reales, no captura simulada de Excel.
  fig,ax=plt.subplots(figsize=(12,3.5));ax.axis('off');sample=d[['StockCode','Quantity','InvoiceDate','UnitPrice','Country']].head(7).astype(str)
  t=ax.table(cellText=sample.values,colLabels=sample.columns,loc='center');t.auto_set_font_size(False);t.set_fontsize(8);t.scale(1,1.7);ax.set_title('Muestra tabular renderizada de los valores del dataset original');savefig('muestra_dataset.png')

def snapshots(d,cut):
 cut=pd.Timestamp(cut);start=cut-pd.Timedelta(days=90);end=cut+pd.Timedelta(days=30)
 past=d[(d.InvoiceDate>=start)&(d.InvoiceDate<cut)]
 future=d[(d.InvoiceDate>=cut)&(d.InvoiceDate<end)]
 a=past.groupby('CustomerID').agg(last=('InvoiceDate','max'),frecuencia=('InvoiceNo','nunique'),monetario=('importe','sum'),unidades=('Quantity','sum'),pais=('Country','last'))
 a['recencia']=(cut-a['last']).dt.total_seconds()/86400
 a['ticket']=a.monetario/a.frecuencia
 a['gasto_futuro']=future.groupby('CustomerID').importe.sum().reindex(a.index).fillna(0)
 a['recompra']=(a.gasto_futuro>0).astype(int);a['corte']=cut.strftime('%Y-%m-%d')
 return a.drop(columns='last').reset_index()

def mining():
 with closing(sqlite3.connect(DB)) as c:
  d=pd.read_sql_query('SELECT * FROM gold_retail WHERE CustomerID IS NOT NULL AND Quantity>0 AND UnitPrice>0 AND is_cancelled=0',c,parse_dates=['InvoiceDate'])
  cuts=['2011-05-01','2011-06-01','2011-07-01','2011-08-01','2011-09-01','2011-10-01','2011-11-01']
  allx=pd.concat([snapshots(d,x) for x in cuts],ignore_index=True)
  train=allx[allx.corte<'2011-09-01'];valid=allx[allx.corte=='2011-09-01'];test=allx[allx.corte>='2011-10-01']
  nums=['recencia','frecuencia','monetario','unidades','ticket'];cats=['pais'];features=nums+cats
  def pre():return ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums),('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),cats)])
  clf=Pipeline([('pre',pre()),('model',LogisticRegression(max_iter=1500,random_state=42))])
  clf.fit(train[features],train.recompra)
  prob=clf.predict_proba(test[features])[:,1];pred=(prob>=.5).astype(int)
  def cm(y,p,s):return {'accuracy':accuracy_score(y,p),'precision':precision_score(y,p,zero_division=0),'recall':recall_score(y,p,zero_division=0),'f1':f1_score(y,p,zero_division=0),'roc_auc':roc_auc_score(y,s)}
  cb=DummyClassifier(strategy='prior').fit(train[features],train.recompra)
  metrics={'clasificacion':cm(test.recompra,pred,prob),'clasificacion_baseline':cm(test.recompra,cb.predict(test[features]),cb.predict_proba(test[features])[:,1]),'validacion':cm(valid.recompra,clf.predict(valid[features]),clf.predict_proba(valid[features])[:,1]),'split':{'train':len(train),'validacion':len(valid),'test':len(test),'positivos_test':int(test.recompra.sum()),'cortes_train':cuts[:4],'cortes_validacion':cuts[4:5],'cortes_test':cuts[5:]},'umbral':.5}
  ConfusionMatrixDisplay.from_predictions(test.recompra,pred,display_labels=['No recompra','Recompra'],cmap='Blues');plt.title('Recompra a 30 días · prueba temporal');savefig('matriz_confusion.png')
  RocCurveDisplay.from_predictions(test.recompra,prob);plt.plot([0,1],[0,1],'--',color='gray');plt.title('Curva ROC · prueba temporal');savefig('roc.png')
  pd.DataFrame(confusion_matrix(test.recompra,pred),index=['real_no','real_si'],columns=['pred_no','pred_si']).to_csv(ROOT/'evidencias/matriz_confusion.csv')
  reg=Pipeline([('pre',pre()),('model',RandomForestRegressor(n_estimators=100,max_depth=9,min_samples_leaf=12,n_jobs=2,random_state=42))])
  reg.fit(train[features],train.gasto_futuro);rp=reg.predict(test[features])
  def rm(y,p):return {'mae':mean_absolute_error(y,p),'rmse':float(np.sqrt(mean_squared_error(y,p))),'r2':r2_score(y,p)}
  rb=DummyRegressor(strategy='mean').fit(train[features],train.gasto_futuro)
  metrics['regresion']=rm(test.gasto_futuro,rp);metrics['regresion_baseline']=rm(test.gasto_futuro,rb.predict(test[features]))
  fig,ax=plt.subplots(figsize=(7,4));ax.scatter(test.gasto_futuro,rp,s=8,alpha=.25,color='#176b87');ax.set(xlabel='Gasto real futuro GBP',ylabel='Gasto predicho GBP',xscale='symlog',yscale='symlog',title='Regresión · horizonte de 30 días');savefig('regresion.png')
  test=test.copy();test['prob_recompra']=prob;test['gasto_predicho']=rp;write(test,'gold_predicciones',c)
  joblib.dump(clf,ROOT/'modelos/clasificacion.joblib');joblib.dump(reg,ROOT/'modelos/regresion.joblib')
  # Matriz transformada con parámetros aprendidos sólo del entrenamiento.
  enc=clf.named_steps['pre'];arr=enc.transform(allx[features]);encdf=pd.DataFrame(arr,columns=enc.get_feature_names_out());encdf.insert(0,'corte',allx.corte.values);encdf.insert(0,'CustomerID',allx.CustomerID.values);write(encdf,'gold_features_ml',c)
  rfm=snapshots(d,'2011-12-10')[['CustomerID','recencia','frecuencia','monetario']]
  scale=StandardScaler();z=scale.fit_transform(np.log1p(rfm[['recencia','frecuencia','monetario']]))
  scores={};models={}
  for k in range(2,7):
   model=KMeans(n_clusters=k,n_init=10,random_state=42).fit(z);models[k]=model;scores[k]=float(silhouette_score(z,model.labels_,sample_size=min(2500,len(z)),random_state=42))
  best=max(scores,key=scores.get);rfm['cluster']=models[best].labels_;write(rfm,'gold_segmentos',c)
  summary=rfm.groupby('cluster').agg(clientes=('CustomerID','size'),recencia_media=('recencia','mean'),frecuencia_media=('frecuencia','mean'),monetario_medio=('monetario','mean'))
  summary.to_csv(ROOT/'evidencias/segmentos.csv')
  metrics['clustering']={'k':best,'silhouette':scores[best],'candidatos':scores,'clientes':len(rfm)}
  joblib.dump({'scaler':scale,'kmeans':models[best]},ROOT/'modelos/clustering.joblib')
  plt.figure(figsize=(8,4));plt.scatter(rfm.recencia, np.log1p(rfm.monetario),c=rfm.cluster,cmap='viridis',s=8,alpha=.5);plt.xlabel('Recencia en días');plt.ylabel('log(1 + gasto de 90 días)');plt.title('Segmentos de clientes');savefig('clusters.png')
  js('metricas.json',metrics)
  allx.to_csv(ROOT/'data/snapshots_modelos.csv',index=False)

def verify():
 with closing(sqlite3.connect(DB)) as c:
  counts={t: c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
  checks={'integridad_sqlite':c.execute('PRAGMA integrity_check').fetchone()[0],'conteos':counts}
  assert checks['integridad_sqlite']=='ok',checks['integridad_sqlite']
  assert counts['bronze_retail']==counts['silver_retail']+counts['silver_retail_rechazos']
  assert counts['gold_retail']==counts['silver_retail']
  for fact,key,dim in [('gold_ventas_productos','producto_key','dim_productos'),('gold_retail','stock_key','dim_retail_producto'),('gold_retail','pais','dim_pais')]:
   assert c.execute(f'SELECT COUNT(*) FROM (SELECT {key}, COUNT(*) n FROM {dim} GROUP BY {key} HAVING n>1)').fetchone()[0]==0
   assert c.execute(f'SELECT COUNT(*) FROM {fact} f LEFT JOIN {dim} d ON f.{key}=d.{key} WHERE d.{key} IS NULL').fetchone()[0]==0
  schema='\n'.join(row[0]+';' for row in c.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name"))
  (ROOT/'sql/03_esquema_ejecutado.sql').write_text(schema,encoding='utf-8')
  assert counts['bronze_productos']==counts['silver_productos']+counts['silver_productos_rechazos']
  assert counts['gold_ventas_productos']==counts['silver_productos'] and counts['silver_productos']>100000
  checks['relaciones_sin_huerfanos']=True;js('verificacion.json',checks)
  js('entorno.json',{'python':sys.version,'pandas':pd.__version__,'numpy':np.__version__,'sklearn':sklearn.__version__,'plataforma':platform.platform()})
  js('sha256_fuentes.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*.xlsx')})
  logging.info('Verificación terminada: integridad y conciliación correctas')

def notify():
 js('estado_ejecucion.json',{'estado':'OK','fecha_utc':pd.Timestamp.now(tz='UTC').isoformat(),'base':str(DB)})
 logging.info('NOTIFICACIÓN LOCAL: pipeline completado. No se envían mensajes externos.')

def run_all():
 """Construye SQLite en disco temporal y publica la base solo tras verificarla."""
 global DB
 destination=DB.resolve()
 destination.parent.mkdir(parents=True,exist_ok=True)
 # Mantiene las escrituras SQLite fuera de carpetas sincronizadas/remotas.
 with tempfile.TemporaryDirectory(prefix='proyecto-kdd-') as temporary:
  DB=Path(temporary)/'proyecto_kdd.sqlite'
  try:
   for fn in [extract,bronze,silver,gold,mining,verify]:fn()
   # Copia primero al mismo volumen del destino para poder reemplazarlo al final.
   with tempfile.NamedTemporaryFile(prefix='.proyecto_kdd.sqlite-',dir=destination.parent,delete=False) as handle:
    pending=Path(handle.name)
   try:
    shutil.copyfile(DB,pending)
    pending.replace(destination)
   finally:
    pending.unlink(missing_ok=True)
  finally:
   DB=destination
 notify()

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['extract','bronze','validate','silver','gold','mining','verify','notify','all'],default='all');a=ap.parse_args()
 try:
  if a.stage!='notify':
   js('estado_ejecucion.json',{'estado':'EN_PROCESO','etapa':a.stage,'fecha_utc':pd.Timestamp.now(tz='UTC').isoformat()})
  if a.stage=='all':
   run_all()
  else:globals()[a.stage]()
 except Exception:
  logging.exception('Fallo del pipeline');js('estado_ejecucion.json',{'estado':'ERROR','fecha_utc':pd.Timestamp.now(tz='UTC').isoformat()});raise
