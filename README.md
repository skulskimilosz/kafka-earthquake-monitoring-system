# Kafka Earthquake Monitoring System

System do monitorowania trzesien ziemi oparty o Apache Kafka.

## Aktualny stan projektu

- Ingestion: dziala producent EMSC z backfillem HTTP i strumieniem WebSocket.
- Kafka: lokalny broker uruchamiany przez Docker Compose (KRaft, bez Zookeepera).
- Dashboard i processing: katalogi przygotowane pod kolejne etapy rozwoju.

## Struktura repozytorium

```text
.
├── docker-compose.yml
├── requirements.txt
├── docs/
│   ├── infrastructure.md
│   └── ingestion.md
└── src/
	├── dashboard/
	├── ingestion/
	│   ├── emsc_producer.py
	│   └── producer_test.py
	└── processing/
```

## Wymagania

- Python 3.12+
- Docker + Docker Compose

## Szybki start

1. Zainstaluj zaleznosci Pythona:

```bash
pip install -r requirements.txt
```

2. Uruchom Kafka:

```bash
docker compose up -d
```

3. Uruchom producent danych EMSC:

```bash
python src/ingestion/emsc_producer.py
```

## Konfiguracja ingestora

`src/ingestion/emsc_producer.py` obsluguje:

- `KAFKA_BROKER` (domyslnie `localhost:9092`)
- `KAFKA_TOPIC` (domyslnie `earthquakes-raw`)

Przyklad uruchomienia z wlasna konfiguracja:

```bash
KAFKA_BROKER=localhost:9092 KAFKA_TOPIC=earthquakes-raw python src/ingestion/emsc_producer.py
```

## Dokumentacja szczegolowa

- Ingestion: `docs/ingestion.md`
- Infrastruktura Kafka: `docs/infrastructure.md`
