import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("BatchEcommerce").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

ruta = "hdfs://localhost:9000/ecommerce/ventas_ecommerce.csv"

# 1. CARGA
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(ruta)

print("\n=== 1. CARGA ===")
df.printSchema()
total_inicial = df.count()
print("Registros cargados:", total_inicial)
df.show(5, False)

print("=== Nulos por columna (antes de limpiar) ===")
df.select([F.sum(F.col(c).isNull().cast("int")).alias(c)
           for c in df.columns]).show()

# 2. LIMPIEZA
sin_duplicados = df.dropDuplicates()
n_duplicados = total_inicial - sin_duplicados.count()

sin_nulos = sin_duplicados.dropna(subset=["category", "order_date"])
n_nulos = sin_duplicados.count() - sin_nulos.count()

df_limpio = sin_nulos.filter(F.col("quantity") > 0)
n_negativos = sin_nulos.count() - df_limpio.count()

print("\n=== 2. LIMPIEZA ===")
print("Duplicados eliminados:", n_duplicados)
print("Filas con categoria o fecha nula eliminadas:", n_nulos)
print("Filas con cantidad no positiva eliminadas:", n_negativos)
print("Registros finales:", df_limpio.count())

# 3. TRANSFORMACION
df_limpio = df_limpio \
    .withColumn("order_date", F.to_timestamp("order_date")) \
    .withColumn("total", F.col("quantity") * F.col("unit_price")) \
    .withColumn("mes", F.month("order_date"))
df_limpio.cache()

# 4. ANALISIS EXPLORATORIO
print("\n=== 4. EDA: estadisticas basicas ===")
df_limpio.select("quantity", "unit_price", "total").summary().show()

por_categoria = df_limpio.groupBy("category").agg(
    F.count("*").alias("pedidos"),
    F.sum("total").alias("ventas"),
    F.round(F.avg("total"), 0).alias("ticket_promedio")
).orderBy(F.col("ventas").desc())
print("Ventas por categoria")
por_categoria.show()

por_pago = df_limpio.groupBy("payment_method").agg(
    F.count("*").alias("pedidos")).orderBy(F.col("pedidos").desc())
print("Pedidos por medio de pago")
por_pago.show()

por_ciudad = df_limpio.groupBy("city").agg(
    F.sum("total").alias("ventas")).orderBy(F.col("ventas").desc())
print("Ventas por ciudad")
por_ciudad.show()

por_mes = df_limpio.groupBy("mes").agg(
    F.sum("total").alias("ventas")).orderBy("mes")
print("Ventas por mes")
por_mes.show(12)

# 5. VISUALIZACION
cat = por_categoria.collect()
pago = por_pago.collect()
ciu = por_ciudad.collect()
mes = por_mes.collect()

fig, ejes = plt.subplots(2, 2, figsize=(13, 9))
ejes[0][0].bar([r["category"] for r in cat], [r["ventas"] / 1e6 for r in cat])
ejes[0][0].set_title("Ventas por categoria")
ejes[0][0].set_ylabel("Millones de pesos")
ejes[0][1].bar([r["payment_method"] for r in pago], [r["pedidos"] for r in pago])
ejes[0][1].set_title("Pedidos por medio de pago")
ejes[0][1].set_ylabel("Numero de pedidos")
ejes[1][0].bar([r["city"] for r in ciu], [r["ventas"] / 1e6 for r in ciu])
ejes[1][0].set_title("Ventas por ciudad")
ejes[1][0].set_ylabel("Millones de pesos")
ejes[1][1].plot([r["mes"] for r in mes], [r["ventas"] / 1e6 for r in mes], marker="o")
ejes[1][1].set_title("Ventas por mes (2025)")
ejes[1][1].set_xlabel("Mes")
ejes[1][1].set_ylabel("Millones de pesos")
fig.suptitle("Analisis batch - ventas de comercio electronico (datos simulados)")
plt.tight_layout()
plt.savefig("/home/vboxuser/grafico_batch.png")
print("\nGrafico guardado en /home/vboxuser/grafico_batch.png")

spark.stop()
