# Infrastruktura

Dokument opisuje aktualny plik `docker-compose.yml` i sposob uruchamiania lokalnego brokera Kafka.

## Cel pliku docker-compose.yml

- uruchamia pojedynczy broker Kafka lokalnie,
- korzysta z trybu KRaft (bez Zookeepera),
- utrzymuje dane w trwalym wolumenie `kafka_data`.

## Aktualna konfiguracja Compose

### Usluga `kafka`

- obraz: `bitnamilegacy/kafka:3.7.0`
- nazwa kontenera: `kafka`
- port: `9092:9092`
- wolumen danych: `kafka_data:/bitnami/kafka`

### Najwazniejsze zmienne srodowiskowe

Tozsamosc i role:

- `KAFKA_CFG_NODE_ID=1`
- `KAFKA_CFG_PROCESS_ROLES=controller,broker`
- `KAFKA_KRAFT_CLUSTER_ID=abcdefghijklmnopqrstuv`

Kontroler KRaft:

- `KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093`
- `KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER`

Listenery i siec:

- `KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093`
- `KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092`
- `KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT`
- `KAFKA_CFG_INTER_BROKER_LISTENER_NAME=PLAINTEXT`
- `ALLOW_PLAINTEXT_LISTENER=yes`

## Dlaczego advertised listeners sa krytyczne

Klient Kafka laczy sie na adres podany przez brokera w `KAFKA_CFG_ADVERTISED_LISTENERS`.
W tym projekcie producer Python uruchamiany lokalnie oczekuje `localhost:9092`.

## Operacje dzienne

Uruchomienie brokera:

```bash
docker compose up -d
```

Status uslug:

```bash
docker compose ps
```

Podglad logow brokera:

```bash
docker compose logs -f kafka
```

Zatrzymanie kontenerow:

```bash
docker compose down
```

Pelne czyszczenie razem z danymi Kafka:

```bash
docker compose down -v
```

## Szybka diagnostyka

1. Upewnij sie, ze kontener `kafka` jest w stanie `running`.
2. Sprawdz logi i potwierdz, ze broker nasluchuje na porcie 9092.
3. Zweryfikuj, czy producer ma zgodne `KAFKA_BROKER` (domyslnie `localhost:9092`).