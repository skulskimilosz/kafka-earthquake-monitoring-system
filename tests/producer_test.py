import websocket
import json

# Official EMSC WebSocket URL from their documentation.
# Prefer TLS first to avoid network policies that block plain ws.
WS_URL = "wss://www.seismicportal.eu/standing_order/websocket"

def on_message(_ws, message):
    try:
        data = json.loads(message)
        # Print only the magnitude and location for clarity.
        payload = data.get("data", {})
        properties = payload.get("properties", {})
        geometry = payload.get("geometry", {})

        mag = properties.get("mag")
        place = properties.get("place") or properties.get("flynn_region")

        if not place:
            coords = geometry.get("coordinates", [])
            if len(coords) >= 2:
                place = f"lat={coords[1]}, lon={coords[0]}"
            else:
                place = "unknown"

        print(f"--- New Event ---\nMagnitude: {mag}\nLocation: {place}\n")
    except Exception as err:
        print(f"PARSE ERROR: {err}")
        print(f"RAW MESSAGE: {message[:300]}")

def on_open(_ws):
    print("### Connected to EMSC Seismic Portal ###")


def on_error(_ws, error):
    print(f"WS ERROR: {error}")


def on_close(_ws, close_status_code, close_msg):
    print(f"WS CLOSED: code={close_status_code}, msg={close_msg}")

if __name__ == "__main__":
    websocket.enableTrace(True)
    print(f"Starting WebSocket client with URL: {WS_URL}")
    ws_app = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws_app.run_forever(ping_interval=30, ping_timeout=10)