# Infrastructure and Kafka Configuration

This document explains the `docker-compose.yml` setup and its role in the end-to-end data flow.

## Purpose of the Current Infrastructure

- run a single Kafka broker locally,
- use KRaft mode (without Zookeeper),
- keep persistent storage through a Docker volume.

This is a minimal but fully sufficient setup for local development.

## Detailed `docker-compose.yml` Breakdown

### Service `kafka`

- `image: bitnamilegacy/kafka:3.7.0`
  Broker image version aligned with the current project stack.
- `container_name: kafka`
  Stable container name for easier diagnostics and logs.
- `ports: "9092:9092"`
  Exposes the broker at `localhost:9092`.
- `volumes: kafka_data:/bitnami/kafka`
  Persists Kafka log data across container restarts.

### KRaft Configuration Variables

- `KAFKA_CFG_NODE_ID=1`
  Broker node identifier.
- `KAFKA_CFG_PROCESS_ROLES=controller,broker`
  A single process acts as both controller and broker.
- `KAFKA_KRAFT_CLUSTER_ID=abcdefghijklmnopqrstuv`
  KRaft cluster identifier.

### Controller Configuration

- `KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093`
  Controller quorum definition; one voter on port 9093.
- `KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER`
  Listener name for controller communication.

### Listeners and Client Routing

- `KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093`
  Broker listens on two local listeners.
- `KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092`
  Address announced to clients (producer/spark).
- `KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT`
  Maps listener names to protocols.
- `KAFKA_CFG_INTER_BROKER_LISTENER_NAME=PLAINTEXT`
  Listener used for broker-to-broker communication.
- `ALLOW_PLAINTEXT_LISTENER=yes`
  Explicitly allows plaintext traffic in a development environment.

## Logical Project Configuration

- Raw events topic: `earthquakes-raw`.
- Producer publishes events with key (`id` or `unid`).
- Spark reads from the same topic via `spark-sql-kafka` connector.

## Developer Operations

The full command list for daily operations is maintained in one place:
`docs/commands.md`.

## Common Issues and Meaning

- Client cannot connect to `localhost:9092`:
  usually a container state problem or `ADVERTISED_LISTENERS` mismatch.
- Spark reports offset errors after topic reset:
  checkpoint stores stale offsets and must be refreshed.
- No data in Spark while producer is running:
  verify producer and Spark are using the same topic.
