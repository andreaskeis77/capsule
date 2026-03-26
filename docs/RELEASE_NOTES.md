# Release Notes
## Capsule Studio / Capsule Wardrobe Project

---

## Release 1.0.0
Status: Baseline defined  
Stand: 2026-03-26

### Summary
Release 1.0.0 definiert den ersten dokumentierten, reproduzierbaren und architektonisch abgesicherten Baseline-Stand von Capsule Studio.

### Included Capabilities
- FastAPI API v2
- Flask Dashboard / Admin / Detailansichten
- Item CRUD
- Meta-Daten-Felder: `context`, `size`, `notes`, `needs_review`
- Legacy v1 Rückwärtskompatibilität für Inventory
- SQLite + Dateisystem Split
- Bildpfad- und Image-Rendering-Logik
- Ingestion mit:
  - dry-run
  - fake-ai
  - folder-signature fingerprint
  - idempotence
  - quarantine
  - pending/ok/failed ingest state
- Recovery Tooling für orphaned archive folders
- Run Registry
- Run Reports / KPIs
- Handoff-/Snapshot-Tooling
- Secret Redaction im Run Registry Kontext
- Secret Scanner
- UI-Filter für `context` und `needs_review`
- dokumentierte Infrastruktur-Basis
- dokumentiertes ARD / Manifest / Release Management

### Infrastructure Baseline
- GitHub: `https://github.com/andreaskeis77/capsule`
- Domain: `capsule-studio.de`
- Registrar: INWX
- DNS / Proxy: Cloudflare
- ngrok public domain: `wardrobe.ngrok-app.com.ngrok.app`
- VPS: Contabo `vmd193069`
- OS: Windows
- Public IP: `84.247.164.122`

### Internal Engineering / Ops Tooling in Scope
- `pytest`
- `ruff`
- `tools/secret_scan.py`
- `tools/handoff_make.py`
- `tools/handoff_make_run.py`
- `tools/runs_report.py`
- `src/ingest_wardrobe.py`
- `tools/ingest_recover.py`
- lokale Start-/Batch-/Smoke-Skripte

### Evidence Expectation
Für Release 1.0.0 müssen dokumentiert und nachvollziehbar sein:
- grüne Tests
- Secret Scan
- aktuelles ARD
- aktuelles Manifest
- aktuelles Release Management
- Handoff-/Snapshot-Fähigkeit

### Known Limitations / Open Topics
- UI/Look-and-feel noch verbesserbar
- Domain-/ngrok-/Cloudflare-Endzustand operativ weiter zu validieren
- Release Tags / GitHub Releases noch einzuführen
- ADR-Struktur initial anzulegen und fortzuschreiben

---

## Change Log Policy
Ab Release 1.0.0 werden alle weiteren Änderungen einem Zielrelease zugeordnet und in Tranchen dokumentiert.
