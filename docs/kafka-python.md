# Data Flow and Kafka in This Project

This document explains the full path of data from EMSC to the Parquet layer and Kafka's role in the architecture.

## End-to-End: Source to Data Layer

1. EMSC HTTP API (backfill)
   Producer retrieves event history for the last 24 hours.
2. EMSC WebSocket (live)
   Producer receives new events in near real time.
3. Kafka topic `earthquakes-raw`
   Each event is published as JSON value + key (`id`/`unid`).
4. Spark Structured Streaming
   Reads from Kafka, parses JSON, and applies transformations.
5. Parquet `data/processed_events`
   Analytics-ready data partitioned by `year/month/day`.
6. Checkpoint `checkpoints/spark_earthquakes`
   Stores streaming progress and offsets for restarts.

## What Kafka Provides in This Architecture

- decoupling between ingestion and processing,
- buffering when Spark is temporarily slower,
- durable offset ordering for stream processing,
- ability to add additional consumers (e.g., alerting, ML, frontend API).

## How the Producer Publishes a Record

In `emsc_producer.py`:

- `topic`: `earthquakes-raw`
- `key`: `event.id` or `event.properties.unid`
- `value`: full event JSON
- `acks='all'`: stronger write acknowledgement guarantees

Why the key is useful:

- stabilizes partition assignment,
- helps with downstream deduplication.

## How Spark Consumes a Record

In `spark_processor.py`:

- source: `.format("kafka")`
- bootstrap: `localhost:9092`
- subscribe: `earthquakes-raw`
- start offset: `earliest`

Spark reads `value` as bytes, casts it to `STRING`, then parses with `from_json(...)` into a DataFrame schema.

## Transformations and Data Model

Spark selects `data.properties.*`, including:

- `mag`
- `flynn_region` (renamed to `place`)
- `time` (converted to `timestamp`)
- `lon`, `lat`
- `unid`

Then partition columns are added:

- `year`
- `month`
- `day`

## Write Path and Restart Semantics

Streaming query settings:

- write to Parquet,
- `outputMode("append")`,
- `checkpointLocation` enabled.

On restart, Spark resumes from checkpointed offsets.
If the topic is reset/recreated, checkpoints can become inconsistent and may require reset.

## Logical Diagram

```text
EMSC HTTP (backfill) -----\
                           >---- emsc_producer.py ----> Kafka: earthquakes-raw ----> spark_processor.py ----> Parquet
EMSC WebSocket (live) ----/                                  |                                   |
                                                               +-- key: id/unid                   +-- offset checkpoint
```
