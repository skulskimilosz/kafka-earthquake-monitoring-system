from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, year, month, dayofmonth
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# 1. Uproszczony schemat - bo Producer wysyła już środek JSONa
json_schema = StructType([
    StructField("id", StringType(), True),
    StructField("properties", StructType([
        StructField("mag", DoubleType(), True),
        StructField("flynn_region", StringType(), True),
        StructField("time", StringType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
        StructField("unid", StringType(), True)
    ]), True)
])

# 1b. Debug do konsoli jest tylko pomocniczy.
# Zostawiamy go wyłączonego domyślnie, żeby głównym wyjściem był Spark -> Parquet.
ENABLE_CONSOLE_DEBUG = False

# 2. SESJA SPARK
spark = SparkSession.builder \
    .appName("EMSC-Spark-Streaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 3. ODCZYT Z KAFKI
# Kafka działa tu jako "bufor" – jeśli Spark na chwilę stanie, dane w Kafce poczekają.
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "earthquakes-raw") \
    .option("startingOffsets", "earliest") \
    .load()

# 4. Transformacja - wchodzimy od razu do properties
processed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), json_schema).alias("data")) \
    .select("data.properties.*") \
    .withColumnRenamed("flynn_region", "place") \
    .withColumn("timestamp", to_timestamp(col("time"))) \
    .withColumn("year", year(col("timestamp"))) \
    .withColumn("month", month(col("timestamp"))) \
    .withColumn("day", dayofmonth(col("timestamp")))

# 5. ZAPIS (Srebrna warstwa danych)
query = processed_df.writeStream \
    .format("parquet") \
    .option("path", "data/processed_events") \
    .option("checkpointLocation", "checkpoints/spark_earthquakes") \
    .partitionBy("year", "month", "day") \
    .outputMode("append") \
    .start()

print("[+] Spark Streaming is processing EMSC data into Parquet...")

if ENABLE_CONSOLE_DEBUG:
    # TYMCZASOWY PODGLĄD W TERMINALU - wlaczaj tylko przy debugowaniu.
    debug_query = processed_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

query.awaitTermination()