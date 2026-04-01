# Kafka Earthquake Monitoring System

A streaming seismic data processing system built with Apache Kafka and Spark Structured Streaming.

## Project Overview

The project provides a data pipeline that integrates seismic event ingestion, reliable transport, and processing into an analytics-ready format.
The solution is designed as the foundation of an earthquake alert application for a travel agency, with a dashboard and presentation layer planned in Streamlit.

## Portfolio Context

This repository demonstrates an end-to-end data engineering approach:

- ingestion from API and WebSocket,
- transport and buffering in Kafka,
- stream processing in Spark Structured Streaming,
- writing to an analytics layer (Parquet) ready for dashboards and alerting.

## Business Goal

The business objective of this project is to:

- ingest earthquake data in near real time,
- normalize and prepare data for analytics,
- maintain a continuous flow into reporting and visualization layers,
- provide the foundation for an earthquake alert system for a travel agency,
- reduce the time from event occurrence to data-layer visibility.

The target outcome is an alerting application that helps a travel agency with operational monitoring and seismic trend analysis.

## Architecture and Data Flow

1. Producer [src/ingestion/emsc_producer.py](src/ingestion/emsc_producer.py) ingests historical (HTTP) and live (WebSocket) data from EMSC.
2. Raw records are published to Kafka topic earthquakes-raw.
3. Processor [src/processing/spark_processor.py](src/processing/spark_processor.py) consumes Kafka data, parses JSON, and applies transformations.
4. Results are written to partitioned Parquet files in the project data layer.
5. The resulting dataset is prepared for a frontend layer (planned Streamlit app).

## Functional Scope (Current Status)

- Ingestion: backfill + live stream implemented.
- Local Kafka: broker runs via Docker Compose (KRaft).
- Processing: Spark Structured Streaming writes data to Parquet.
- Frontend: planned (Streamlit).

## Technical Requirements

- Python 3.12+
- Java 17 (recommended for `pyspark==3.5.0`)
- Docker + Docker Compose

Note: Java 21+ may cause Spark failures (`JAVA_GATEWAY_EXITED` / `UnsupportedOperationException: getSubject is not supported`).

## Documentation

Full technical documentation is maintained in [docs/README.md](docs/README.md).

- [docs/commands.md](docs/commands.md): developer commands (single source of operational commands).
- [docs/kafka-python.md](docs/kafka-python.md): end-to-end data flow.
- [docs/infrastructure.md](docs/infrastructure.md): Kafka and Docker Compose configuration.
- [docs/ingestion.md](docs/ingestion.md): detailed ingestion layer walkthrough.
- [docs/processing.md](docs/processing.md): detailed Spark processing layer walkthrough.

## Onboarding (Beginner Path)

1. Start with [docs/commands.md](docs/commands.md) to run and stop the system locally.
2. Read [docs/kafka-python.md](docs/kafka-python.md) to understand the data flow.
3. Continue with implementation details in [docs/ingestion.md](docs/ingestion.md) and [docs/processing.md](docs/processing.md).

## Running the Project

The end-user run section will be finalized after the Streamlit frontend is implemented.

For development, the pipeline currently requires three steps:

1. start local Kafka,
2. start the ingestion producer,
3. start the Spark processor.

Detailed commands are available in [docs/commands.md](docs/commands.md).
