# Project Documentation

This is the central entry point for project documentation.
All architecture, code, and data-flow descriptions are maintained in the `docs/` directory.

The documentation is structured to support both:

- quick onboarding for new readers,
- deep implementation analysis for the author and technical team.

## Is It Overwhelming?

For beginners, it can be.
That is why the docs are split into two reading paths: quick orientation and deep technical detail.

## Beginner Path (15-25 min)

1. `../README.md`
   Project goal, business context, and end-to-end system behavior.
2. `commands.md`
   How to run, stop, and troubleshoot the system locally.
3. `kafka-python.md`
   Data flow from EMSC to Parquet without deep code details.

After this path, a beginner should understand the overall process and component dependencies.

## Deep-Dive Path for the Author (30-60 min)

1. `infrastructure.md`
   Detailed Kafka broker setup (Docker Compose, KRaft).
2. `ingestion.md`
   Detailed walkthrough of `src/ingestion/emsc_producer.py`.
3. `processing.md`
   Detailed walkthrough of `src/processing/spark_processor.py`.

## Full Document List

1. `commands.md`
2. `kafka-python.md`
3. `infrastructure.md`
4. `ingestion.md`
5. `processing.md`

## Who This Documentation Is For

- Author: detailed explanation of logic and responsibilities in each pipeline stage.
- Project audience: clear process and dependency overview needed to understand the system.

## Documentation Scope

- Bash operational commands for day-to-day development.
- Streaming architecture: EMSC -> Kafka -> Spark -> Parquet.
- Kafka configuration and parameter rationale.
- Transformations and partitioning strategy.
- Restart behavior (checkpoints and offsets).