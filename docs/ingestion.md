# Ingestion: `emsc_producer.py` Step by Step

This document is a detailed walkthrough of `src/ingestion/emsc_producer.py`.
Its purpose is to help the author understand the logic almost line by line.

## File Role in the Architecture

`emsc_producer.py` is the system entry point.

1. It fetches historical data (backfill) from the EMSC HTTP API.
2. It switches to the live EMSC WebSocket stream.
3. It sends each event as JSON to Kafka topic `earthquakes-raw`.

## Detailed Code Analysis

### 1) Imports

- `json`, `os`, `time`: standard tools for serialization, configuration, and retry handling.
- `requests`: HTTP backfill requests.
- `websocket`: WebSocket client for live stream ingestion.
- `KafkaProducer` from `kafka`: event publishing to broker.
- `datetime`, `timedelta`: time window calculation for backfill.
- `RequestException`: explicit HTTP transport error handling.

### 2) Constants and Environment Configuration

- `KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')`
  Reads broker address from ENV; fallback is local broker.
- `KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'earthquakes-raw')`
  Allows topic switching without code changes.
- `HTTP_API_URL` is the EMSC FDSNWS endpoint for historical data.
- `WS_URL` is the EMSC standing-order WebSocket endpoint.

### 3) `KafkaProducer` Construction

Key parameters:

- `bootstrap_servers=[KAFKA_BROKER]`
  Broker address used by the producer.
- `value_serializer=lambda x: json.dumps(x).encode('utf-8')`
  Converts Python objects -> JSON text -> UTF-8 bytes.
- `key_serializer=lambda x: str(x).encode('utf-8') if x is not None else None`
  Serializes event keys (`event_id`) into bytes.
- `acks='all'`
  Broker acknowledges write only after quorum durability.

### 4) `fetch_historical_data(hours=24)`

This is the cold-start phase, so the pipeline does not start with empty data.

Function steps:

1. Logs start and requested backfill window.
2. Computes `start_time = now_utc - hours` and converts to ISO format.
3. Sends `GET` to `HTTP_API_URL` with `starttime` parameter.
4. Uses `response.raise_for_status()` for HTTP 4xx/5xx failures.
5. Parses JSON and reads `payload.get('features', [])`.
6. If `features` is a list:
   sends each event via `send_to_kafka(event)`.
7. If payload shape differs:
   logs a warning.

Error handling:

- `RequestException`: network, timeout, and HTTP transport issues.
- `ValueError`: invalid JSON body.
- `Exception`: fallback guard for unexpected failures.

### 5) `send_to_kafka(event_data)`

Core function for publishing a single event.

1. Resolves event key:
   - first `event_data['id']`,
   - fallback `event_data['properties']['unid']`.
2. Calls `producer.send(KAFKA_TOPIC, key=event_id, value=event_data)`.
3. Registers `future.add_errback(...)` for async delivery failure logging.

Why the key matters:

- improves partition consistency,
- helps identify duplicates downstream.

### 6) `on_message(ws, message)`

WebSocket frame callback.

1. Parses incoming frame with `json.loads(message)`.
2. Checks whether the frame contains `data`.
3. If yes, treats `raw_payload['data']` as event and sends to Kafka.
4. Logs event identifier for observability.

Error handling:

- `json.JSONDecodeError`: invalid frame payload.
- `Exception`: any other callback error.

### 7) `on_open`, `on_error`, `on_close`

Auxiliary connection callbacks:

- `on_open`: confirms successful WebSocket connection.
- `on_error`: logs transport-level errors.
- `on_close`: logs status code and close message.

### 8) `if __name__ == "__main__":` Runtime Block

Main runtime sequence:

1. `fetch_historical_data(hours=24)`
   Runs backfill first to include the latest 24h events.
2. `producer.flush()`
   Ensures all backfill records are delivered before live streaming starts.
3. Infinite `while True` loop:
   - creates `websocket.WebSocketApp(...)` with callbacks,
   - runs `run_forever(ping_interval=30)`,
   - on failure waits 5 seconds and retries.

Result: the process self-recovers after temporary connection interruptions.

## What to Monitor in Practice

- Whether Kafka accepts records (`kafka` container and broker logs).
- Whether EMSC endpoints respond (HTTP and WSS).
- Whether WebSocket retry loops happen too frequently.
- Whether `event_id` is present for most records.

## Related Documents

- `docs/processing.md`
- `docs/infrastructure.md`
- `docs/kafka-python.md`
