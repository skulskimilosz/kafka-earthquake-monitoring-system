# Processing: `spark_processor.py` Step by Step

This document provides a detailed walkthrough of `src/processing/spark_processor.py`.
It is intended primarily for the author to follow the transformation logic line by line.

## File Role in the Architecture

`spark_processor.py` is the stream processing layer.

1. Reads raw JSON records from Kafka.
2. Parses them into a Spark SQL schema.
3. Normalizes and enriches records with partition fields.
4. Writes output to Parquet.
5. Maintains checkpointed offsets for restart continuity.

## Detailed Code Analysis

### 1) Spark Imports

- `SparkSession`: session configuration and lifecycle.
- `col`, `from_json`, `to_timestamp`, `year`, `month`, `dayofmonth`:
  DataFrame transformation functions.
- `StructType`, `StructField`, `StringType`, `DoubleType`:
  schema definition for JSON parsing.

### 2) `json_schema`

The schema matches the event structure produced by ingestion.

Fields:

- `id` (String)
- `properties` (object):
  - `mag` (Double)
  - `flynn_region` (String)
  - `time` (String)
  - `lon` (Double)
  - `lat` (Double)
  - `unid` (String)

Why explicit schema helps:

- improves parsing reliability,
- catches inconsistent records earlier,
- simplifies downstream transformations.

### 3) Spark Session Initialization

`SparkSession.builder` sets:

- `appName("EMSC-Spark-Streaming")`
- `spark.jars.packages = org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0`

The second option loads the Kafka connector for Spark 3.5.0.

`spark.sparkContext.setLogLevel("WARN")` reduces log noise.

### 4) Reading the Kafka Stream

`df = spark.readStream.format("kafka") ... .load()`

Key options:

- `kafka.bootstrap.servers = localhost:9092`
- `subscribe = earthquakes-raw`
- `startingOffsets = earliest`

Meaning of `earliest`:

- on first run, processing starts from the oldest available records,
- on subsequent restarts, checkpoint state takes precedence.

### 5) `processed_df` Transformations

Transformation steps:

1. `selectExpr("CAST(value AS STRING)")`
   Converts Kafka byte payload to JSON text.
2. `from_json(col("value"), json_schema).alias("data")`
   Parses JSON using the predefined schema.
3. `select("data.properties.*")`
   Projects directly into `properties` fields.
4. `withColumnRenamed("flynn_region", "place")`
   Standardizes location field name.
5. `withColumn("timestamp", to_timestamp(col("time")))`
   Converts textual time into Spark timestamp.
6. Adds partition columns:
   - `year(timestamp)`
   - `month(timestamp)`
   - `dayofmonth(timestamp)`

Result: a DataFrame ready for analytics storage.

### 6) Main Write Query

`query = processed_df.writeStream ... .start()`

Parameters:

- `format("parquet")`
- `path = data/processed_events`
- `checkpointLocation = checkpoints/spark_earthquakes`
- `partitionBy("year", "month", "day")`
- `outputMode("append")`

Why this setup:

- Parquet is efficient for analytical reads.
- Date partitions improve filtering and scan performance.
- Checkpointing stores stream progress (offsets + metadata).

### 7) Optional Console Debug Query

The secondary `debug_query` is optional and disabled by default.
You can enable it by setting `ENABLE_CONSOLE_DEBUG = True`.

- `format("console")`
- `truncate = false`

It is useful for quick validation during debugging, but it is not part of the target architecture.

The final presentation layer is planned in Streamlit, so console output remains a temporary auxiliary option.

### 8) `query.awaitTermination()`

The process stays active and continuously listens for new records.
The script exits only when the process is stopped.

## Reading Pipeline Output

After writes, directories are created in the form:

- `data/processed_events/year=YYYY/month=M/day=D/...parquet`

This is the final data layer for dashboards and analysis.

## Risks and Operational Notes

- Topic reset/recreation with an old checkpoint may cause offset errors.
- Changes in EMSC event structure require `json_schema` updates.
- Java 17 is recommended for stable `pyspark==3.5.0` execution.

## Related Documents

- `docs/ingestion.md`
- `docs/infrastructure.md`
- `docs/kafka-python.md`
