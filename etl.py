import pandas as pd
import glob
import os

archivos = glob.glob('data/ecommerce_*.csv')
if not archivos:
   print("❌ No se encontraron los archivos. Asegurate de descargarlos en la carpeta data/")
   print("Deberías tener: ecommerce_orders.csv, ecommerce_customers.csv, etc.")
else:
    print(f"📂 Archivos encontrados: {len(archivos)}")
    for f in sorted(archivos):
        print(f"  - {os.path.basename(f)}")

# Cargar los CVs Principales
df_orders = pd.read_csv('data/ecommerce_orders.csv')
df_order_items = pd.read_csv('data/ecommerce_order_items.csv') 
df_customers = pd.read_csv('data/ecommerce_customers.csv')
df_products = pd.read_csv('data/ecommerce_products.csv') 

print(f"\n📈 Resumen:")
print(f"Orders: {len(df_orders)} filas, {len(df_orders.columns)} columnas")
print(f"Order Items: {len(df_order_items)} filas")
print(f"Customers: {len(df_customers)} filas")
print(f"Products: {len(df_products)} filas")

print("\n🔍 Primeras filas de orders:")
print(df_orders.head())
print("\n📋 Info de orders:")
print(df_orders.info())

print("---------df_orders-------------")
print(df_orders.isnull().sum())
print("---------df_order_items-------------")
print(df_order_items.isnull().sum())
print("---------df_customers-------------")
print(df_customers.isnull().sum())
print("---------df_products-------------")
print(df_products.isnull().sum())


# Ejemplo: eliminar filas con nulos en campos críticos
df_orders_clean = df_orders.dropna(subset = ['customer_id'])

# Ejemplo: rellenar con 0 en campos numéricos opcionales
#df_orders_clean = df_orders.fillna(subset = ['customer_id'])

print("cantidad de duplicados")
print(df_orders_clean.duplicated().sum())

df_orders_clean = df_orders_clean.drop_duplicates(subset=['order_id'],keep ='last')
 


df_orders_clean ['order_date'] = pd.to_datetime(df_orders_clean['order_date'])
df_orders_clean ['total_amount'] = pd.to_numeric(df_orders_clean['total_amount'])
df_order_items ['quantity'] = pd.to_numeric(df_order_items['quantity'])

print(df_orders_clean.dtypes)


df_orders = df_orders.merge(df_customers,on='customer_id')
total_amount = (df_orders.groupby(['first_name','last_name'],as_index=False) 
                .agg(
                       total_gastado=('total_amount','sum'),
                       cantidad_ordenes=('order_id','count')
                )
                 .rename(columns={
                 'first_name': 'nombre',
                 'last_name': 'apellido'
                })
                .sort_values(by='total_gastado', ascending=False)
                .head(5)
                .reset_index(drop=True)
                )

print('clientes que más han gastado')
print(total_amount)

df_orders = df_orders.merge(df_order_items, on='order_id').merge(df_products, on='product_id')
quantity = (df_orders
            .groupby(['product_name','product_id'],as_index=False)['quantity']
            .sum()
            .sort_values(by='quantity',ascending=False)
                .rename(columns={
                 'product_name': 'nombre_producto',
                 'quantity': 'cantidad'
                })
            .head(5)
            .reset_index(drop =True)
            )

print('producto mas vendido')
print(quantity)

df_orders_clean['mes'] = df_orders_clean['order_date'].dt.to_period('M')
ventas_mes = df_orders_clean.groupby('mes')['total_amount'].sum().reset_index()
ventas_mes.columns = ['mes', 'total_ventas']
print("\n📈 Ventas por mes:")
print(ventas_mes)


os.makedirs('output', exist_ok=True)
df_orders_clean.to_csv('output/df_orders_clean.csv',index=False)
ventas_mes.to_csv('output/ventas_mes_etl.csv',index=False)

df_orders_clean.to_parquet('output/df_orders_clean.parquet',index=False)
ventas_mes.to_csv('output/ventas_mes_etl.csv',index=False)


csv_size = os.path.getsize('output/df_orders_clean.csv') / 1024
parquet_size = os.path.getsize('output/df_orders_clean.parquet') / 1024

print(f"Tamaño CSV: {csv_size:.1f} KB")
print(f"Tamaño Parquet: {parquet_size:.1f} KB")
print(f"Parquet es {csv_size/parquet_size:.1f}x más chico")