# Dokumentacja projektu

To jest centralny punkt dokumentacji projektu.
Wszystkie opisy architektury, kodu i przeplywu danych sa utrzymywane w katalogu `docs/`.

Dokumentacja jest zorganizowana tak, aby jednoczesnie wspierac:

- szybkie wdrozenie osoby nowej do projektu,
- poglebiona analize implementacji dla autora i zespolu technicznego.

## Czy to jest przytlaczajace?

Dla osoby poczatkujacej: tak, moze byc.
Dlatego dokumentacja jest podzielona na 2 sciezki czytania: szybka (zrozumienie systemu) i poglebiona (zrozumienie implementacji).

## Sciezka dla poczatkujacego (15-25 min)

1. `../README.md`
   Cel projektu, kontekst biznesowy i co system robi end-to-end.
2. `commands.md`
   Jak uruchomic, zatrzymac i diagnozowac system lokalnie.
3. `kafka-python.md`
   Przeplyw danych od EMSC do Parquet, bez wchodzenia w szczegoly kodu.

Po tej sciezce osoba zielona powinna rozumiec caly proces i zaleznosci miedzy komponentami.

## Sciezka poglebiona dla autora (30-60 min)

1. `infrastructure.md`
   Szczegoly konfiguracji brokera Kafka (Docker Compose, KRaft).
2. `ingestion.md`
   Dokladny opis `src/ingestion/emsc_producer.py`.
3. `processing.md`
   Dokladny opis `src/processing/spark_processor.py`.

## Pelna lista dokumentow

1. `commands.md`
2. `kafka-python.md`
3. `infrastructure.md`
4. `ingestion.md`
5. `processing.md`

## Dla kogo jest ta dokumentacja

- Dla autora: szczegolowe wyjasnienie logiki i odpowiedzialnosci kazdego etapu pipeline'u.
- Dla odbiorcy projektu: opis procesu, komponentow i zaleznosci potrzebnych do zrozumienia systemu.

## Zakres dokumentacji

- Komendy operacyjne Bash dla codziennej pracy autora.
- Architektura strumieniowa EMSC -> Kafka -> Spark -> Parquet.
- Konfiguracja Kafki i uzasadnienie parametrow.
- Transformacje danych oraz sposob partycjonowania.
- Zachowanie systemu przy restarcie (checkpointy i offsety).