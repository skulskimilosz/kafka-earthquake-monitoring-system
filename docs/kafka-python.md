# Przeplyw danych i Kafka w projekcie

Ten dokument opisuje caly przeplyw danych od EMSC do warstwy Parquet oraz role Kafki.

## End-to-end: od zrodla do warstwy danych

1. EMSC HTTP API (backfill)
    Producer pobiera historie zdarzen z ostatnich 24 godzin.
2. EMSC WebSocket (live)
    Producer odbiera nowe zdarzenia na biezaco.
3. Kafka topic `earthquakes-raw`
    Kazde zdarzenie trafia jako JSON (wartosc) + klucz (`id`/`unid`).
4. Spark Structured Streaming
    Odczyt z Kafki, parsowanie JSON i transformacje.
5. Parquet `data/processed_events`
    Dane analityczne partycjonowane po `year/month/day`.
6. Checkpoint `checkpoints/spark_earthquakes`
    Stan streamingu i offsetow dla restartow.

## Co Kafka daje w tej architekturze

- Rozsprzezenie miedzy ingestion i processing.
- Buforowanie, gdy Spark chwilowo nie konsumuje.
- Trwalosc i porzadek offsetow dla przetwarzania strumieniowego.
- Mozliwosc podpiecia kolejnych konsumentow (np. alerting, ML, frontend API).

## Jak producer publikuje rekord

W `emsc_producer.py`:

- `topic`: `earthquakes-raw`
- `key`: `event.id` lub `event.properties.unid`
- `value`: caly event JSON
- `acks='all'`: bezpieczniejsze potwierdzenia zapisu

Dlaczego klucz jest przydatny:

- stabilizuje przypisanie do partycji,
- upraszcza deduplikacje downstream.

## Jak Spark konsumuje rekord

W `spark_processor.py`:

- source: `.format("kafka")`
- bootstrap: `localhost:9092`
- subscribe: `earthquakes-raw`
- start offset: `earliest`

Spark czyta `value` jako bajty, konwertuje na `STRING`, potem `from_json(...)` na schema DataFrame.

## Transformacje i model danych

Spark wyciaga `data.properties.*`, czyli m.in.:

- `mag`
- `flynn_region` (zmieniane na `place`)
- `time` (konwersja do `timestamp`)
- `lon`, `lat`
- `unid`

Nastepnie dokladane sa kolumny partycjonujace:

- `year`
- `month`
- `day`

## Zapis i semantyka restartu

Zapytanie streamingu:

- zapis do Parquet,
- `outputMode("append")`,
- `checkpointLocation` ustawione.

Przy restarcie Spark korzysta z checkpointu i kontynuuje od zapamietanych offsetow.
Jesli topic zostanie zresetowany/rekreowany, checkpoint moze byc niespojny z Kafka i wymagac odswiezenia.

## Diagram logiczny

```text
EMSC HTTP (backfill) -----\
                                    >---- emsc_producer.py ----> Kafka: earthquakes-raw ----> spark_processor.py ----> Parquet
EMSC WebSocket (live) ----/                                  |                                   |
                                                                                    +-- klucz: id/unid                 +-- checkpoint offsetow
```

