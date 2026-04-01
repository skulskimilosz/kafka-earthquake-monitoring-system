# Infrastruktura i konfiguracja Kafka

Dokument opisuje konfiguracje z `docker-compose.yml` i jej znaczenie dla calego przeplywu danych.

## Cel aktualnej infrastruktury

- uruchomienie pojedynczego brokera Kafka lokalnie,
- praca w trybie KRaft (bez Zookeepera),
- utrzymanie trwalego storage przez wolumen Docker.

To minimalna, ale w pelni wystarczajaca konfiguracja developerska.

## Szczegolowa analiza `docker-compose.yml`

### Usługa `kafka`

- `image: bitnamilegacy/kafka:3.7.0`
	Wersja brokera zgodna z obecnym stackiem projektu.
- `container_name: kafka`
	Stala nazwa kontenera, latwiejsza diagnostyka i logowanie.
- `ports: "9092:9092"`
	Broker dostepny lokalnie pod `localhost:9092`.
- `volumes: kafka_data:/bitnami/kafka`
	Trwale dane logu Kafki pomiedzy restartami kontenera.

### Zmienne konfiguracji KRaft

- `KAFKA_CFG_NODE_ID=1`
	Identyfikator wezla brokera.
- `KAFKA_CFG_PROCESS_ROLES=controller,broker`
	Jeden proces pelni role kontrolera i brokera.
- `KAFKA_KRAFT_CLUSTER_ID=abcdefghijklmnopqrstuv`
	Id klastra KRaft.

### Konfiguracja kontrolera

- `KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093`
	Definicja quorum kontrolera; jeden voter na porcie 9093.
- `KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER`
	Nazwa listenera przypisanego do komunikacji kontrolera.

### Listenery i routing klientow

- `KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093`
	Broker slucha lokalnie na dwoch listenerach.
- `KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092`
	Adres zwracany klientom (producer/spark) do dalszej komunikacji.
- `KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT`
	Mapowanie nazw listenerow na protokoly.
- `KAFKA_CFG_INTER_BROKER_LISTENER_NAME=PLAINTEXT`
	Listener do komunikacji broker-broker (tu istotne glownie dla zgodnosci konfiguracji).
- `ALLOW_PLAINTEXT_LISTENER=yes`
	Jawne dopuszczenie ruchu plaintext w srodowisku developerskim.

## Konfiguracja logiczna projektu

- Topic surowych zdarzen: `earthquakes-raw`.
- Producer publikuje zdarzenia z kluczem (`id` lub `unid`).
- Spark czyta z tego samego topiku przez connector `spark-sql-kafka`.

## Operacje developerskie

Pelna lista komend operacyjnych dla autora jest utrzymywana w jednym miejscu:
`docs/commands.md`.

## Najczestsze problemy i ich sens

- Klient nie moze sie polaczyc z `localhost:9092`:
	zwykle problem z kontenerem lub `ADVERTISED_LISTENERS`.
- Spark widzi blad offsetow po resecie topicu:
	checkpoint przechowuje stare offsety i wymaga odswiezenia.
- Brak danych w Spark mimo pracy producenta:
	sprawdz, czy producer i Spark czytaja/pisza ten sam topic.