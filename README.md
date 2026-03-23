# Capsule

Capsule ist ein lokal entwickeltes Wardrobe-/Ontology-/Ingest-System mit klar getrennten Schichten für API, Dashboard, Ontology-Runtime, Persistenz, Quality Gates und operatives Tooling.

## Einstieg

Für den schnellsten Einstieg nutze diese Dokumente in genau dieser Reihenfolge:

1. `docs/QUICKSTART.md`
2. `docs/ARCHITECTURE.md`
3. `docs/DEVELOPER_WORKFLOW.md`
4. `docs/RUNBOOK.md`
5. `docs/HANDOFF_GUIDE.md`

## Standardbefehle

Windows-first:

```powershell
.\.venv\Scripts\Activate.ps1
python .\tools\task_runner.py quality-gates
```

Alternativ:

```powershell
.\capsule.cmd quality-gates
```

## Kernbereiche

- `src/` – Anwendungscode
- `tests/` – Regressionen und Vertrags-Tests
- `tools/` – operative Helfer, Handoff, Audit, Reports, Gates
- `docs/` – Architektur, Workflow, Runbook, Release- und Handoff-Dokumente
- `.github/` – CI-/Governance-Verträge und Workflows

## Qualitätsstandard

Änderungen gelten erst als belastbar, wenn die Quality Gates grün sind:

- `compileall`
- `ruff_critical`
- `pytest`
- `secret_scan_tracked`
- `live_smoke`

## Navigation

Die Dokumentations-Navigation ist zentral in `docs/INDEX.md` definiert.
