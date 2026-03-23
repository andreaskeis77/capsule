# ADR-0001 – Tranche A Quality Gates

- Status: accepted
- Date: 2026-03-22

## Kontext

Das Repository ist strukturell bereits gut aufgestellt, aber die wichtigsten Schutzmechanismen gegen Change-Failures
waren bislang nicht automatisch erzwungen. Gleichzeitig fordern Working Agreement und Engineering Manifest
reproduzierbare Änderungen, Quality Gates, Security Hygiene, dokumentierte Entscheidungen und Beweise via Tests
statt textlicher Behauptungen.

Aktueller Kontext:
- Primäre Entwicklungsumgebung ist Windows + PowerShell.
- Der kritische Runtime-Pfad ist lokaler Start via `src.server_entry` bzw. `Wardrobe_Studio_Starten.bat`.
- Das Repo enthält bereits Tests, Secret-Scan und Sanity-Check, aber diese laufen noch nicht als gebündeltes Gate.

## Entscheidung

Tranche A führt einen harten, aber bewusst begrenzten Gate-Rahmen ein:

1. **CI auf GitHub Actions**
   - Workflow auf `push` nach `main` und auf `pull_request`
   - Runner: `windows-latest`
   - Python: `3.12`

2. **Gebündelter Gate-Runner**
   - Neues Tool `tools/run_quality_gates.py`
   - Ein gemeinsamer Einstiegspunkt für:
     - `compileall`
     - `ruff` nur auf kritische Fehlerklassen (`E9,F63,F7,F82`)
     - `pytest -q`
     - `tools/secret_scan.py --mode tracked`
     - Live-Smoke gegen gestarteten Server via `tools/project_sanity_check.py`

3. **Lokaler Operator-Wrapper**
   - `tools/run_quality_gates.ps1` als PowerShell-Einstieg für Windows
   - Ausgabe inkl. Run-Artefakten unter `docs/_ops/quality_gates/run_<timestamp>/`

4. **Optionaler lokaler Commit-Schutz**
   - Git Hook `tools/hooks/pre-commit`
   - Installierbar via `tools/install_git_hooks.ps1`

## Warum diese Form

- **Großer Hebel, kleiner Contract-Eingriff**:
  Die Tranche schafft sofort automatische Rückmeldung, ohne bestehende App- oder DB-Verträge umzubauen.
- **Windows-first statt Cross-Platform sofort**:
  Das reduziert Einführungsrisiko und entspricht der tatsächlichen Hauptlaufzeit.
- **Kritische Ruff-Regeln statt Voll-Lint**:
  Ziel ist Robustheit, nicht kosmetische Umformatierung. Format- und Stilvereinheitlichung folgt später.
- **Live-Smoke als eigener Gate-Baustein**:
  Tests allein beweisen nicht, dass der Server sauber startet und die wichtigsten Routen erreichbar sind.

## Verworfen

### A) Sofort Black + voller Ruff-Style-Gate
Verworfen, weil das Repo damit voraussichtlich an vielen rein stilistischen Punkten brechen würde.
Das wäre für Tranche A zu viel Churn bei zu wenig operativem Mehrwert.

### B) Sofort Linux + Windows Matrix
Verworfen für Tranche A. Cross-Platform-Härtung ist sinnvoll, aber nicht der erste Engpass.
Erst muss der Gate-Mechanismus selbst verlässlich laufen.

### C) Nur lokale Skripte ohne CI
Verworfen, weil damit weiterhin Personen-Disziplin statt automatischer Absicherung dominiert.

## Konsequenzen

Positiv:
- Jeder Change bekommt sofort maschinenlesbares Feedback.
- Fehler lassen sich auf Schritt-Ebene zuordnen.
- Logs und Zusammenfassungen werden als prüfbare Artefakte geschrieben.
- Secret-Hygiene wird Teil des Standardpfads.

Negativ / Kosten:
- Erste Pipeline-Läufe können bestehende Schwächen sichtbar machen.
- `ruff` wird als Dev-Dependency eingeführt.
- Das Team muss akzeptieren, dass fehlerhafte Änderungen früher stoppen.

## Rollback

Minimaler Rollback:
- Git-Hook nicht installieren oder wieder entfernen
- Workflow-Datei deaktivieren/löschen
- Lokale Gate-Runner-Dateien entfernen

Technischer Rollback ist damit einfach; der eigentliche Verlust wäre dann jedoch wieder fehlende automatische Absicherung.
