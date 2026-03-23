import json
import os
import time
import requests
import websocket
from kafka import KafkaProducer
from datetime import datetime, timedelta
from requests.exceptions import RequestException

# --- Configuration ---
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'earthquakes-raw')
# EMSC API for historical data (FDSNWS)
HTTP_API_URL = "https://www.seismicportal.eu/fdsnws/event/1/query?format=json"
# EMSC WebSocket for real-time data
WS_URL = "wss://www.seismicportal.eu/standing_order/websocket"

# --- Kafka Producer Setup ---
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    key_serializer=lambda x: str(x).encode('utf-8') if x is not None else None,
    acks='all'
)

def fetch_historical_data(hours=24):
    """
    Fetches historical earthquake data to avoid an empty map on startup.
    This is the 'Batch' part of our ingestion.
    """
    print(f"[*] Starting Backfill: Fetching last {hours} hours of events...")
    
    # Calculate time window
    start_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    
    try:
        # Request data from EMSC HTTP API
        response = requests.get(f"{HTTP_API_URL}&starttime={start_time}", timeout=15)
        response.raise_for_status()
        payload = response.json()
        events = payload.get('features', [])
        if isinstance(events, list):
            print(f"[+] Found {len(events)} historical events. Sending to Kafka...")
            for event in events:
                send_to_kafka(event)
            print("[+] Backfill completed successfully.")
        else:
            print("[!] Unexpected HTTP payload: 'features' is not a list.")
    except RequestException as e:
        print(f"[!] HTTP API request failed: {e}")
    except ValueError as e:
        print(f"[!] Invalid JSON in HTTP response: {e}")
    except Exception as e:
        print(f"[!] Critical error during backfill: {e}")

def send_to_kafka(event_data):
    """Sends a single earthquake event to Kafka."""
    try:
        # Use 'unid' (Unique ID) as the Kafka Key for deduplication
        event_id = event_data.get('id') or event_data.get('properties', {}).get('unid')
        future = producer.send(KAFKA_TOPIC, key=event_id, value=event_data)
        future.add_errback(lambda exc: print(f"[!] Kafka delivery failed for event {event_id}: {exc}"))
    except Exception as e:
        print(f"[!] Kafka production error: {e}")

def on_message(ws, message):
    """Real-time message handler."""
    try:
        raw_payload = json.loads(message)
        if 'data' in raw_payload:
            event = raw_payload['data']
            print(f"[*] New real-time event: {event.get('id')}")
            send_to_kafka(event)
    except json.JSONDecodeError as e:
        print(f"[!] Invalid JSON frame from WebSocket: {e}")
    except Exception as e:
        print(f"[!] Error while processing WebSocket frame: {e}")

def on_open(ws):
    print("[+] WebSocket connection established. Streaming live data...")

def on_error(ws, error):
    print(f"[!] WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"[!] WebSocket closed: code={close_status_code}, msg={close_msg}")

if __name__ == "__main__":
    # STEP 1: Cold Start / Backfill
    fetch_historical_data(hours=24)
    producer.flush() # Ensure all historical data is in Kafka
    
    # STEP 2: Live Ingestion
    while True:
        try:
            ws_app = websocket.WebSocketApp(
                WS_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws_app.run_forever(ping_interval=30)
        except Exception as e:
            print(f"[!] Connection dropped: {e}. Retrying in 5 seconds...")
            time.sleep(5)