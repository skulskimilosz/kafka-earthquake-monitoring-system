# Ingestion: `emsc_producer.py` krok po kroku

Ten dokument jest szczegolowym opisem dzialania `src/ingestion/emsc_producer.py`.
Jego celem jest umozliwienie autorowi zrozumienia logiki niemal linia po linii.

## Rola pliku w architekturze

`emsc_producer.py` jest brama wejsciowa systemu.

1. Pobiera dane historyczne (backfill) z EMSC HTTP API.
2. Przechodzi na strumien live z EMSC WebSocket.
3. Wysyla kazde zdarzenie jako JSON do topiku Kafka `earthquakes-raw`.

## Szczegolowa analiza kodu

### 1) Importy

- `json`, `os`, `time`: standardowe narzedzia do serializacji, konfiguracji i retry.
- `requests`: HTTP backfill.
- `websocket`: klient WebSocket dla live streamu.
- `KafkaProducer` z `kafka`: publikacja zdarzen do brokera.
- `datetime`, `timedelta`: wyliczanie okna czasowego dla backfillu.
- `RequestException`: jawna obsluga bledow transportu HTTP.

### 2) Konfiguracja stale i zmienne srodowiskowe

- `KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')`
	Odczytuje adres brokera z ENV; fallback to lokalny broker.
- `KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'earthquakes-raw')`
	Pozwala przelaczac topic bez zmian w kodzie.
- `HTTP_API_URL` to endpoint FDSNWS EMSC do pobran historycznych.
- `WS_URL` to endpoint standing order WebSocket EMSC.

### 3) Konstrukcja `KafkaProducer`

Parametry sa kluczowe:

- `bootstrap_servers=[KAFKA_BROKER]`
	Adres brokera, do ktorego producer wysyla rekordy.
- `value_serializer=lambda x: json.dumps(x).encode('utf-8')`
	Kazdy obiekt Python -> tekst JSON -> bajty UTF-8.
- `key_serializer=lambda x: str(x).encode('utf-8') if x is not None else None`
	Klucz wiadomosci (`event_id`) jest serializowany jako bajty.
- `acks='all'`
	Broker potwierdza zapis dopiero po replikacyjnym quorum (najbezpieczniejszy tryb potwierdzen).

### 4) `fetch_historical_data(hours=24)`

To faza cold-start, zeby pipeline nie startowal od pustego zbioru.

Kroki funkcji:

1. Loguje start i liczbe godzin backfillu.
2. Liczy `start_time = now_utc - hours` i konwertuje do ISO.
3. Wysyla `GET` pod `HTTP_API_URL` z parametrem `starttime`.
4. `response.raise_for_status()` wymusza blad dla HTTP 4xx/5xx.
5. Parsuje JSON i pobiera `payload.get('features', [])`.
6. Jesli `features` jest lista:
	 wysyla kazdy event przez `send_to_kafka(event)`.
7. Jesli payload ma inny ksztalt: loguje ostrzezenie.

Obsluga bledow:

- `RequestException`: problemy sieciowe, timeouty, statusy HTTP.
- `ValueError`: niepoprawny JSON.
- `Exception`: bezpiecznik na nieoczekiwane przypadki.

### 5) `send_to_kafka(event_data)`

To centralna funkcja publikacji pojedynczego zdarzenia.

1. Wyznacza klucz zdarzenia:
	 - najpierw `event_data['id']`,
	 - fallback: `event_data['properties']['unid']`.
2. Wywoluje `producer.send(KAFKA_TOPIC, key=event_id, value=event_data)`.
3. Rejestruje `future.add_errback(...)`, aby logowac bledy dostarczenia asynchronicznego.

Dlaczego klucz jest wazny:

- Umozliwia bardziej stabilne partycjonowanie.
- Pomaga identyfikowac duplikaty na dalszych etapach.

### 6) `on_message(ws, message)`

Callback dla ramek WebSocket.

1. Parsuje surowa ramke `json.loads(message)`.
2. Sprawdza, czy ramka ma klucz `data`.
3. Jesli tak, traktuje `raw_payload['data']` jako event i wysyla do Kafka.
4. Loguje identyfikator zdarzenia dla obserwowalnosci.

Obsluga bledow:

- `json.JSONDecodeError`: niepoprawna ramka.
- `Exception`: kazdy inny blad callbacku.

### 7) `on_open`, `on_error`, `on_close`

Pomocnicze callbacki statusowe:

- `on_open`: potwierdza zestawienie polaczenia.
- `on_error`: raportuje bledy transportu.
- `on_close`: raportuje kod i powod zamkniecia sesji.

### 8) Blok `if __name__ == "__main__":`

To glowny runtime programu.

Kolejnosc:

1. `fetch_historical_data(hours=24)`
	 Najpierw backfill, zeby uzupelnic brakujace zdarzenia z ostatnich 24h.
2. `producer.flush()`
	 Wymusza zapis wszystkich rekordow z backfillu przed przejsciem na live.
3. Nieskonczona petla `while True`:
	 - tworzy `websocket.WebSocketApp(...)` z callbackami,
	 - uruchamia `run_forever(ping_interval=30)`,
	 - przy wyjatku czeka 5 sekund i probuje ponownie.

Efekt: proces jest samonaprawialny po chwilowych przerwach lacza.

## Co warto monitorowac w praktyce

- Czy Kafka przyjmuje rekordy (`kafka` kontener, logi brokera).
- Czy endpointy EMSC odpowiadaja (HTTP i WSS).
- Czy retry petli WebSocket nie wystepuje zbyt czesto.
- Czy klucz `event_id` jest dostepny dla wiekszosci rekordow.

## Powiazane dokumenty

- `docs/processing.md`
- `docs/infrastructure.md`
- `docs/kafka-python.md`