# Processing: `spark_processor.py` krok po kroku

Ten dokument opisuje szczegolowo `src/processing/spark_processor.py`.
Jest przeznaczony glownie dla autora projektu, aby latwo przechodzic przez logike transformacji linia po linii.

## Rola pliku w architekturze

`spark_processor.py` jest warstwa przetwarzania strumieniowego.

1. Czyta surowe rekordy JSON z Kafki.
2. Parsuje je do schematu Spark SQL.
3. Normalizuje i wzbogaca dane o pola partycjonujace.
4. Zapisuje dane do Parquet.
5. Utrzymuje checkpoint offsetow dla restartow.

## Szczegolowa analiza kodu

### 1) Importy Spark

- `SparkSession`: konfiguracja i start sesji.
- `col`, `from_json`, `to_timestamp`, `year`, `month`, `dayofmonth`:
  funkcje transformacji kolumn.
- `StructType`, `StructField`, `StringType`, `DoubleType`:
  definicja schematu danych przy parsowaniu JSON.

### 2) `json_schema`

Zdefiniowany jest schemat odpowiadajacy rekordowi wysylanemu przez producenta.

Pola:

- `id` (String)
- `properties` (obiekt):
  - `mag` (Double)
  - `flynn_region` (String)
  - `time` (String)
  - `lon` (Double)
  - `lat` (Double)
  - `unid` (String)

Dlaczego schema jest jawna:

- przyspiesza i stabilizuje parsowanie,
- pozwala wykryc niespojne rekordy,
- upraszcza dalsze transformacje.

### 3) Tworzenie sesji Spark

`SparkSession.builder` ustawia:

- `appName("EMSC-Spark-Streaming")`
- `spark.jars.packages = org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0`

Druga opcja dolacza connector Kafka dla Spark 3.5.0.

`spark.sparkContext.setLogLevel("WARN")` ogranicza szum logow.

### 4) Odczyt streamu z Kafki

`df = spark.readStream.format("kafka") ... .load()`

Najwazniejsze opcje:

- `kafka.bootstrap.servers = localhost:9092`
- `subscribe = earthquakes-raw`
- `startingOffsets = earliest`

Znaczenie `earliest`:

- przy pierwszym starcie procesor czyta od najstarszych dostepnych rekordow,
- przy kolejnych restartach checkpoint ma priorytet nad tym ustawieniem.

### 5) Transformacja `processed_df`

Kroki transformacji:

1. `selectExpr("CAST(value AS STRING)")`
   Konwersja bajtow Kafka value do tekstu JSON.
2. `from_json(col("value"), json_schema).alias("data")`
   Parsowanie JSON do struktury zgodnej ze schema.
3. `select("data.properties.*")`
   Wejscie bezposrednio do `properties`.
4. `withColumnRenamed("flynn_region", "place")`
   Ujednolicenie nazwy pola lokalizacji.
5. `withColumn("timestamp", to_timestamp(col("time")))`
   Zamiana tekstu czasu na typ timestamp Spark.
6. Dodanie kolumn partycji:
   - `year(timestamp)`
   - `month(timestamp)`
   - `dayofmonth(timestamp)`

Efekt: DataFrame gotowy do zapisu analitycznego.

### 6) Glowne zapytanie zapisu

`query = processed_df.writeStream ... .start()`

Parametry:

- `format("parquet")`
- `path = data/processed_events`
- `checkpointLocation = checkpoints/spark_earthquakes`
- `partitionBy("year", "month", "day")`
- `outputMode("append")`

Znaczenie:

- Parquet daje wydajny format kolumnowy pod analityke.
- Partycje po dacie upraszczaja filtrowanie i skanowanie danych.
- Checkpoint zapisuje postep streamingu (offsety + metadata).

### 7) Debug query do konsoli

Drugie zapytanie (`debug_query`) jest tylko pomocnicze i domyslnie wylaczone.
Mozna je wlaczyc przez ustawienie `ENABLE_CONSOLE_DEBUG = True`.

- `format("console")`
- `truncate = false`

To ulatwia szybkie sprawdzenie, czy transformacje daja oczekiwany wynik, ale nie jest czescia docelowej architektury.

Docelowo warstwa prezentacji ma byc obsluzona przez Streamlit, wiec terminalowy debug pozostaje tylko opcja pomocnicza.

### 8) `query.awaitTermination()`

Proces przechodzi w tryb stalego dzialania i slucha nowych rekordow.
Skrypt konczy sie dopiero po zatrzymaniu procesu.

## Jak czytac output pipeline'u

Po zapisach pojawiaja sie katalogi:

- `data/processed_events/year=YYYY/month=M/day=D/...parquet`

To finalna warstwa danych dla dashboardu i analiz.

## Ryzyka i uwagi eksploatacyjne

- Usuniecie/reset topicu Kafka przy starym checkpoint moze powodowac bledy offsetow.
- Zmiana schematu eventu EMSC wymaga aktualizacji `json_schema`.
- Java 17 jest zalecana dla stabilnosci `pyspark==3.5.0`.

## Powiazane dokumenty

- `docs/ingestion.md`
- `docs/infrastructure.md`
- `docs/kafka-python.md`