# CUSTOM_GPT_REVIEW_DELTA_V5.md

## Neue Ergebnisse in v5

### 1. Hinweistext jetzt als konkrete Soll-Fassung
Es liegt jetzt eine minimalinvasive, builder-taugliche Soll-Version des Hinweistexts vor:
- klarer Karen-Default
- strukturierte Missing-Info-Logik
- saubere Trennung zwischen Planung und CRUD
- weniger Redundanz zur Knowledge-Datei

### 2. OpenAI-Abgleich aktualisiert
Für die Überarbeitung des Hinweistexts wurden aktuelle offizielle OpenAI-Quellen erneut gegengeprüft.

Maßgebliche Befunde:
- Instructions für Custom GPTs sollen klar segmentiert, schrittweise und möglichst positiv formuliert werden.
- GPTs mit Custom Actions bleiben ein eigener Sonderfall bei Modellunterstützung und sollen praktisch getestet werden.
- Der GPT-Builder umfasst Instructions, Knowledge, Capabilities/Actions, Test/Preview und Version History.
- Für öffentliche GPTs mit Actions ist eine gültige Privacy Policy URL erforderlich.

### 3. Konsequenz für dieses Projekt
Der Hinweistext darf jetzt als weitgehend stabil betrachtet werden, sobald:
- Knowledge synchronisiert ist
- Health/Auth entschieden ist
- Preview-Tests dokumentiert sind
