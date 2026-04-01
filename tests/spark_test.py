import re
import subprocess
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# --- Configuration ---
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "earthquakes-raw"


def ensure_java_compatibility() -> None:
    """Fail fast with a clear message when Java is incompatible with Spark/Hadoop stack."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("[!] Java is not installed or not available in PATH.")
        print("[!] Install Java 17 and try again.")
        sys.exit(1)

    version_output = f"{result.stderr}\n{result.stdout}".strip()
    first_line = version_output.splitlines()[0] if version_output else ""
    match = re.search(r'"(\d+)(?:\.|$)', first_line)

    if not match:
        print("[!] Could not detect Java version from `java -version` output.")
        print(f"[!] Raw output: {first_line or '<empty>'}")
        sys.exit(1)

    java_major = int(match.group(1))
    if java_major >= 21:
        print(f"[!] Detected Java {java_major}, which is not compatible with this Spark setup.")
        print("[!] Use Java 17 for pyspark 3.5.0 + hadoop 3.3.4.")
        print("[!] Example (SDKMAN): sdk install java 17.0.18-ms && sdk default java 17.0.18-ms")
        sys.exit(1)


ensure_java_compatibility()

# 1. Initialize Spark Session with Kafka support
# This will download the necessary JAR files (connectors) automatically
spark = SparkSession.builder \
    .appName("KafkaConnectivityTest") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

# Set log level to WARN to avoid messy output
spark.sparkContext.setLogLevel("WARN")

print(f"[*] Starting Spark Stream. Listening to {KAFKA_TOPIC}...")

# 2. Read Stream from Kafka
# We treat Kafka as a DataFrame source
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# 3. Simple Transformation
# Kafka sends data in 'value' column as bytes. We cast it to String to see the JSON.
raw_output = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# 4. Write Stream to Console
# This is for debugging only! 
query = raw_output.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()