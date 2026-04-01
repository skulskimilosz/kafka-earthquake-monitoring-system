from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, year, month, dayofmonth
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Schema for incoming Kafka messages.
# The producer sends full event objects, and relevant fields are under `properties`.
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

# Optional console output for troubleshooting only.
# Keep disabled by default; the main output is Parquet.
ENABLE_CONSOLE_DEBUG = False

# Initialize Spark with Kafka connector support.
spark = SparkSession.builder \
    .appName("EMSC-Spark-Streaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Read the stream from Kafka.
# Kafka buffers records, so temporary processing slowdowns do not drop events.
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "earthquakes-raw") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON payload and project normalized event fields.
processed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), json_schema).alias("data")) \
    .select("data.properties.*") \
    .withColumnRenamed("flynn_region", "place") \
    .withColumn("timestamp", to_timestamp(col("time"))) \
    .withColumn("year", year(col("timestamp"))) \
    .withColumn("month", month(col("timestamp"))) \
    .withColumn("day", dayofmonth(col("timestamp")))

# Write the normalized stream to partitioned Parquet (analytics layer).
query = processed_df.writeStream \
    .format("parquet") \
    .option("path", "data/processed_events") \
    .option("checkpointLocation", "checkpoints/spark_earthquakes") \
    .partitionBy("year", "month", "day") \
    .outputMode("append") \
    .start()

print("[+] Spark Streaming is processing EMSC data into Parquet...")

if ENABLE_CONSOLE_DEBUG:
    # Temporary terminal preview for debugging; do not use as the primary output.
    debug_query = processed_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

query.awaitTermination()