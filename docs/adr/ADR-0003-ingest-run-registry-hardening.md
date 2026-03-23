# ADR-0003 – Ingest / Run Registry Hardening

## Kontext
Nach Tranche A (Quality Gates) und Tranche B (API-v2-Entkopplung) bleiben `src/ingest_item_runner.py` und `src/run_registry.py` strukturelle Hotspots. Der Metrics-Report nennt beide Dateien explizit als hohe Churn-/Maintainability-Risiken, und das Engineering Manifest fordert für kritische Pfade strukturierte Observability, Run Registry, Negativtests und objektive Reliability-KPIs. fileciteturn7file7 fileciteturn7file5

## Entscheidung
Tranche C zerlegt die Verantwortung in drei klarere Bausteine, ohne das äußere Verhalten zu ändern:

1. `src/run_registry_redaction.py`
   - Secret-Redaction + JSON-Serialisierung
2. `src/run_registry_metrics.py`
   - KPI-Berechnung aus Run-Listen
3. `src/ingest_run_outcome.py`
   - deterministische Abschlussentscheidung für Ingest-Runs

`src/run_registry.py` bleibt die kompatible Fassade. `src/ingest_item_runner.py` bleibt der Orchestrator, delegiert aber Abschlusslogik an `src/ingest_run_outcome.py`.

## Warum das zur Architektur passt
Das Engineering Manifest fordert Separation of Concerns, kleine stabile Schnittstellen, strukturierte Logs/Run Registry und Regressionstests bei Bugfixes bzw. harten Refactorings. Genau das wird hier umgesetzt. fileciteturn7file14 fileciteturn7file12 fileciteturn7file3

## Konsequenzen
Positiv:
- klarere Verantwortlichkeiten
- geringeres Refactor-Risiko in kritischen Operativpfaden
- zusätzliche Regressionstests für Transient/Permanent-Klassifikation und Ingest-Abschlusslogik

Negativ:
- mehr Dateien im selben Themenbereich
- Shim-/Reexport-Disziplin muss erhalten bleiben

## Rollback
Rollback ist einfach: komplette Tranche-C-Dateien zurücknehmen und auf die vorige Einzeldatei-Version von `run_registry.py` / `ingest_item_runner.py` gehen.
