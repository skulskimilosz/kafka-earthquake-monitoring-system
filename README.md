# Kafka Earthquake Monitoring System

Strumieniowy system przetwarzania danych sejsmicznych oparty o Apache Kafka i Spark Structured Streaming.

## Opis projektu

Projekt dostarcza pipeline danych, ktory integruje pobieranie zdarzen sejsmicznych, ich niezawodny transport i przetwarzanie do formatu analitycznego.
Rozwiazanie zostalo zaprojektowane jako podstawa aplikacji alertowej dla biura turystycznego, z dashboardem i warstwa prezentacji oparta o Streamlit.

## Kontekst portfolio

Repozytorium prezentuje podejscie do budowy systemu data engineering end-to-end:

- ingestion danych z API i WebSocket,
- transport i buforowanie zdarzen w Kafka,
- przetwarzanie strumieniowe w Spark Structured Streaming,
- zapis do warstwy analitycznej (Parquet) gotowej pod dashboard i system alertow.

## Cel biznesowy

Celem biznesowym projektu jest:

- pobiera dane o trzesieniach ziemi w czasie zblizonym do rzeczywistego,
- normalizacja i przygotowanie danych do analityki,
- utrzymanie stalego przeplywu danych do warstwy raportowej i wizualizacyjnej,
- dostarczenie podstaw pod system alertow o trzesieniach ziemi dla biura turystycznego,
- skracanie czasu od pojawienia sie zdarzenia do jego widocznosci w warstwie danych.

Docelowym zastosowaniem jest aplikacja alertowa wspierajaca biuro turystyczne w monitoringu operacyjnym i analizie trendow sejsmicznych.

## Architektura i przeplyw danych

1. Producer [src/ingestion/emsc_producer.py](src/ingestion/emsc_producer.py) pobiera dane historyczne (HTTP) i live (WebSocket) z EMSC.
2. Rekordy surowe sa publikowane do Kafka topic `earthquakes-raw`.
3. Processor [src/processing/spark_processor.py](src/processing/spark_processor.py) konsumuje dane z Kafka, parsuje JSON i wykonuje transformacje.
4. Wynik zapisywany jest do partycjonowanych plikow Parquet w katalogu danych projektowych.
5. Dane sa przygotowane pod warstwe frontendowa (planowany Streamlit).

## Zakres funkcjonalny (stan biezacy)

- Ingestion: backfill + live stream sa zaimplementowane.
- Kafka lokalnie: broker uruchamiany przez Docker Compose (KRaft).
- Processing: Spark Structured Streaming zapisuje dane do Parquet.
- Frontend: etap planowany (Streamlit).

## Wymagania techniczne

- Python 3.12+
- Java 17 (zalecane dla `pyspark==3.5.0`)
- Docker + Docker Compose

Uwaga: Java 21+ moze powodowac bledy Spark (`JAVA_GATEWAY_EXITED` / `UnsupportedOperationException: getSubject is not supported`).

## Dokumentacja

Pelna dokumentacja techniczna jest utrzymywana w katalogu [docs/README.md](docs/README.md).

- [docs/commands.md](docs/commands.md): komendy developerskie (jedyne zrodlo komend operacyjnych).
- [docs/kafka-python.md](docs/kafka-python.md): przeplyw danych end-to-end.
- [docs/infrastructure.md](docs/infrastructure.md): konfiguracja Kafka i Docker Compose.
- [docs/ingestion.md](docs/ingestion.md): szczegolowy opis warstwy ingestion.
- [docs/processing.md](docs/processing.md): szczegolowy opis warstwy przetwarzania Spark.

## Onboarding (dla osoby poczatkujacej)

1. Zapoznaj sie z [docs/commands.md](docs/commands.md), aby uruchomic i zatrzymac system lokalnie.
2. Przeczytaj [docs/kafka-python.md](docs/kafka-python.md), aby zrozumiec przeplyw danych.
3. Nastepnie przejdz do dokumentacji implementacyjnej: [docs/ingestion.md](docs/ingestion.md) i [docs/processing.md](docs/processing.md).

## Uruchomienie

Sekcja uruchomienia dla odbiorcy koncowego zostanie uzupelniona po wdrozeniu frontendu Streamlit.

Do prac developerskich obecnie wystarcza trzy kroki:

1. uruchomienie lokalnej Kafka,
2. uruchomienie producenta ingestion,
3. uruchomienie processora Spark.

Szczegolowe komendy znajduja sie w [docs/commands.md](docs/commands.md).
