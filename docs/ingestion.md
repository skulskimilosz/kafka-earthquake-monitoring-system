# Ingestion

Ten dokument opisuje aktualny stan warstwy pobierania danych sejsmicznych.

## Pliki

- `src/ingestion/emsc_producer.py` - glowny producer do Kafka.
- `src/ingestion/producer_test.py` - narzedzie diagnostyczne do testu polaczenia WebSocket.

## Notatka o emsc_producer.py

`emsc_producer.py` realizuje dwa etapy ingestion:

1. Backfill historyczny (HTTP)
2. Strumien live (WebSocket)

### 1) Backfill historyczny

Funkcja `fetch_historical_data(hours=24)` pobiera zdarzenia z EMSC FDSNWS:

- endpoint: `https://www.seismicportal.eu/fdsnws/event/1/query?format=json`
- okno czasowe: ostatnie `hours` godzin (domyslnie 24)
- timeout zapytania HTTP: 15 sekund
- obsluga bledow: RequestException, niepoprawny JSON, bledy krytyczne

Kazde zdarzenie z `features` trafia do `send_to_kafka(...)`.

### 2) Strumien live

Producer laczy sie z:

- `wss://www.seismicportal.eu/standing_order/websocket`

Przeplyw:

- `on_message` parsuje ramke JSON
- jezeli ramka ma klucz `data`, event jest wysylany do Kafka
- obslugiwane sa bledy parsowania i bledy callbacku
- `run_forever(ping_interval=30)` utrzymuje heartbeat

### Kafka i serializacja

Producer Kafka jest inicjalizowany z:

- `acks='all'`
- `value_serializer`: JSON -> UTF-8
- `key_serializer`: bezpieczne `str(key).encode('utf-8')`

Klucz wiadomosci:

- preferowane `event.id`
- fallback do `event.properties.unid`

Wysylka uzywa `future.add_errback(...)` do logowania bledow dostarczenia.

### Konfiguracja przez zmienne srodowiskowe

- `KAFKA_BROKER` (domyslnie `localhost:9092`)
- `KAFKA_TOPIC` (domyslnie `earthquakes-raw`)

Przyklad:

```bash
KAFKA_BROKER=localhost:9092 KAFKA_TOPIC=earthquakes-raw python src/ingestion/emsc_producer.py
```

## Notatka o producer_test.py

`producer_test.py` sluzy do szybkiego potwierdzenia, ze:

- polaczenie WSS z EMSC dziala,
- przychodza ramki JSON,
- mozna odczytac podstawowe pola (magnituda i lokalizacja).

Skrypt:

- wlacza `websocket.enableTrace(True)` dla diagnostyki handshake,
- loguje `on_error` i `on_close`,
- nie publikuje do Kafka (to tylko test lacza i formatu danych).

## Typowy scenariusz uruchomienia

1. Uruchom Kafka:

```bash
docker compose up -d
```

2. Przetestuj lacze EMSC (opcjonalnie):

```bash
python src/ingestion/producer_test.py
```

3. Uruchom glowny producer:

```bash
python src/ingestion/emsc_producer.py
```