# HANDOFF MANIFEST – Wardrobe Studio

## Purpose
This document defines what a “handoff bundle” contains and how to reproduce the system state.

## Required Inputs
- Repo root: `C:\CapsuleWardrobeRAG`
- Python: 3.12 + `.venv`
- `.env` is required (secrets NOT included in handoff bundles)

## Generated Outputs (docs/_snapshot/)
Each handoff run produces:
- `handoff_summary.md` (entry point, status OK/FAILED)
- `sanity_check.txt` (proof of running server + HTTP checks)
- `runtime_state.md` (python, pip freeze, env presence only)
- `project_audit_dump.md` (filtered tree + text sources, secrets redacted)
- `data_snapshot.md` (DB + images + ontology file hashes)
- `ontology_runtime_dump.json` (resolved ontology inputs: overrides + color lexicon + parts index)
- `ontology_runtime_summary.md` (human-readable ontology summary)

## Security
- Secrets must not appear in snapshots.
- `.env` is treated as sensitive and is omitted by default by audit tools.
- The runtime state file reports only presence of env vars (SET/NOT_SET), never values.

## How to Run
1) Start server (in one terminal):
- `python -m src.server_entry` or `Wardrobe_Studio_Starten.bat`

2) Run handoff master (in another terminal):
- `python tools/handoff_make.py --base http://127.0.0.1:5002 --user karen --ids 112,101,110`

Optional:
- include ontology markdown text into the ontology runtime JSON:
  - `python tools/handoff_make.py --include-ontology-text`

## Definition of Done
- `handoff_summary.md` shows status `OK`
- sanity checks passed
- artifacts are written to `docs/_snapshot/latest/`