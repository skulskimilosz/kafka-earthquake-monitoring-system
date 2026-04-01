# Komendy Bash dla autora

Ten plik zbiera w jednym miejscu komendy developerskie do codziennej pracy.

## 1) Kafka (Docker Compose)

Start brokera:

```bash
docker compose up -d
```

Status kontenerow:

```bash
docker compose ps
```

Logi Kafki na zywo:

```bash
docker compose logs -f kafka
```

Zatrzymanie kontenerow:

```bash
docker compose down
```

Zatrzymanie + usuniecie danych Kafki (reset lokalnego stanu):

```bash
docker compose down -v
```

## 2) Producer EMSC (`emsc_producer.py`)

Uruchomienie (domyslna konfiguracja):

```bash
python src/ingestion/emsc_producer.py
```

Uruchomienie z konfiguracja ENV:

```bash
KAFKA_BROKER=localhost:9092 KAFKA_TOPIC=earthquakes-raw python src/ingestion/emsc_producer.py
```

Zatrzymanie producenta (gdy dziala w tle lub w innym terminalu):

```bash
pkill -f "python src/ingestion/emsc_producer.py"
```

## 3) Consumer/Processor Spark (`spark_processor.py`)

Uruchomienie processora:

```bash
python src/processing/spark_processor.py
```

Zatrzymanie processora (gdy dziala w tle lub w innym terminalu):

```bash
pkill -f "python src/processing/spark_processor.py"
```

## 4) Diagnostyka streamingu Spark

Podglad katalogu danych wyjsciowych:

```bash
find data/processed_events -maxdepth 4 -type d | sort
```

Podglad checkpointow:

```bash
find checkpoints/spark_earthquakes -maxdepth 3 -type f | sort
```

Reset checkpointu Spark (uwaga: utrata stanu offsetow):

```bash
rm -rf checkpoints/spark_earthquakes
```

## 5) Typowa sekwencja start/stop

Start:

1. `docker compose up -d`
2. `python src/ingestion/emsc_producer.py`
3. `python src/processing/spark_processor.py`

Stop:

1. `pkill -f "python src/processing/spark_processor.py"`
2. `pkill -f "python src/ingestion/emsc_producer.py"`
3. `docker compose down`