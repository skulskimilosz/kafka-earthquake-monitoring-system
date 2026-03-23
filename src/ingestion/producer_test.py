import websocket
import json

# Official EMSC WebSocket URL from their documentation
WS_URL = "ws://www.seismicportal.eu/standing_order/websocket"

def on_message(ws, message):
    data = json.loads(message)
    # Print only the magnitude and location for clarity
    mag = data['data']['properties']['mag']
    place = data['data']['properties']['place']
    print(f"--- New Event --- \n Magnitude: {mag} \n Location: {place} \n")

def on_open(ws):
    print("### Connected to EMSC Seismic Portal ###")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(WS_URL, on_open=on_open, on_message=on_message)
    ws.run_forever()