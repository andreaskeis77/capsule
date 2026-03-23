# Test Strategy

## Zielbild

Die Testsuite wird in klar benannte Schichten gegliedert, damit Fehler schneller lokalisierbar sind und lokale sowie CI-Läufe nachvollziehbar bleiben.

## Schichten

- `unit` – kleine, isolierte Tests für pure Helfer und modulare Logik
- `smoke` – schnelle Vertrauensprüfungen für kritische Einstiegspunkte
- `contract` – Kompatibilitäts- und Interface-Tests
- `integration` – breitere Mehrmodul-Tests mit Dateisystem, Prozessen oder mehreren Schichten
- `ops` – Tooling, Handoff, Audit, Reports, Release- und Gate-Logik
- `docs` – Navigations- und Doku-Verträge

## Standardbefehle

```powershell
python .\tools\task_runner.py test
python .\tools\task_runner.py test-smoke
python .\tools\task_runner.py test-contract
python .\tools\task_runner.py test-integration
python .\tools\task_runner.py test-report
```

## Gemeinsame Test-Helfer

Die gemeinsame Infrastruktur liegt unter `tests/support/` und in `tests/conftest.py`.
Das Ziel ist, Run- und Report-Artefakte zentral zu bauen, statt in vielen Tests eigene kleine JSON-/Pfad-Helfer zu duplizieren.
