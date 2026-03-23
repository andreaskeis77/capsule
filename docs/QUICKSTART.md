# Quickstart

## Voraussetzungen

- Windows PowerShell
- Python im lokalen `.venv`
- Repo lokal ausgecheckt
- `requirements.txt` und `requirements-dev.txt` installiert

## Setup

```powershell
cd C:\CapsuleWardrobeRAG
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Standard-Validierung

```powershell
python .\tools\run_quality_gates.py
```

## Standard-Tasks

```powershell
python .\tools\task_runner.py quality-gates
python .\tools\task_runner.py release-evidence --release-id v0.0.0-local
```

## Erst lesen bei Problemen

1. `docs/RUNBOOK.md`
2. `docs/DEVELOPER_WORKFLOW.md`
3. `docs/HANDOFF_GUIDE.md`
