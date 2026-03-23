# ADR-0014: Test Architecture and Suite Layering

## Status
Accepted

## Context

Die Testsuite ist inhaltlich bereits stark, aber die gemeinsame Test-Infrastruktur war bislang dünn: ein minimales `conftest.py`, keine standardisierten Marker-Definitionen und keine zentrale Sicht auf Suite-Struktur und Marker-Nutzung.

## Decision

Wir führen in dieser Tranche ein:

1. gemeinsame Builder unter `tests/support/`
2. standardisierte pytest-Marker in `pytest.ini`
3. einen Test-Suite-Report unter `tools/test_suite_report.py`
4. neue Task-Runner-Entrypoints für geschichtete Testläufe

## Consequences

- bessere Wiederverwendung in Tests
- klarere Trennung von smoke/contract/integration
- schnellere Diagnose bei Testfehlern und CI-Laufzeiten
- keine Verhaltensänderung an Produktivcode, sondern Härtung der Testarchitektur
