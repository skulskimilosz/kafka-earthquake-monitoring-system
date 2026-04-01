# Bash Commands for the Author

This file centralizes development commands for day-to-day work.

## 1) Kafka (Docker Compose)

Start broker:

```bash
docker compose up -d
```

Container status:

```bash
docker compose ps
```

Live Kafka logs:

```bash
docker compose logs -f kafka
```

Stop containers:

```bash
docker compose down
```

Stop + remove Kafka data (local state reset):

```bash
docker compose down -v
```

## 2) EMSC Producer (`emsc_producer.py`)

Run (default configuration):

```bash
python src/ingestion/emsc_producer.py
```

Run with environment variables:

```bash
KAFKA_BROKER=localhost:9092 KAFKA_TOPIC=earthquakes-raw python src/ingestion/emsc_producer.py
```

Stop producer (when running in background or another terminal):

```bash
pkill -f "python src/ingestion/emsc_producer.py"
```

## 3) Spark Consumer/Processor (`spark_processor.py`)

Run processor:

```bash
python src/processing/spark_processor.py
```

Stop processor (when running in background or another terminal):

```bash
pkill -f "python src/processing/spark_processor.py"
```

## 4) Spark Streaming Diagnostics

Inspect output directories:

```bash
find data/processed_events -maxdepth 4 -type d | sort
```

Inspect checkpoints:

```bash
find checkpoints/spark_earthquakes -maxdepth 3 -type f | sort
```

Reset Spark checkpoint (warning: offset state will be lost):

```bash
rm -rf checkpoints/spark_earthquakes
```

## 5) Typical Start/Stop Sequence

Start:

1. `docker compose up -d`
2. `python src/ingestion/emsc_producer.py`
3. `python src/processing/spark_processor.py`

Stop:

1. `pkill -f "python src/processing/spark_processor.py"`
2. `pkill -f "python src/ingestion/emsc_producer.py"`
3. `docker compose down`
