# Runbook – Start/Stop/Debug

## Quick Start (empfohlen)

0) Konfiguration anlegen (einmalig)
- Kopiere `.env.example` → `.env`
- Setze mindestens `WARDROBE_API_KEY`
- `.env` bleibt absichtlich unversioniert

1) venv aktivieren
- PowerShell: `\.venv\Scripts\Activate.ps1`

2) Start via Batch
- `\.\Wardrobe_Studio_Starten.bat`

URLs:
- Local Dashboard: `http://127.0.0.1:5002/?user=karen`
- Local Docs: `http://127.0.0.1:5002/docs`
- Health: `http://127.0.0.1:5002/healthz`
- API v2 health: `http://127.0.0.1:5002/api/v2/health`

ngrok (fixed domain):
- `https://wardrobe.ngrok-app.com.ngrok.app/?user=karen`
- `https://wardrobe.ngrok-app.com.ngrok.app/docs`

## Start ohne ngrok (PowerShell)

- `$env:START_NGROK="0"`
- `\.\Wardrobe_Studio_Starten.bat`

Zurücksetzen:
- `Remove-Item Env:START_NGROK -ErrorAction SilentlyContinue`

## Manuell starten (Debug Mode)

- `python .\src\server_entry.py`
- Stop: `CTRL+C`

## Logs

Ordner: `logs/`

Wichtige Dateien:
- `startup.log`
- `server.out.log`
- `server.err.log`
- `ngrok.out.log`
- `ngrok.err.log`

Rotation:
- Batch rotiert in `*_YYYYMMDD-HHMMSS.log`

## Häufige Probleme

### Batch hängt bei „Warte auf Readiness.“

Prüfen:
- `http://127.0.0.1:5002/healthz`
- `logs/server.err.log`

Mögliche Ursachen:
- Port belegt
- venv kaputt / Dependencies fehlen
- Serverprozess nicht gestartet

### Port 5002 belegt

Optionen:
- Batch mit `FORCE_RESTART=1` starten
- oder manuell prüfen:
  - `Get-NetTCPConnection -State Listen -LocalPort 5002`

### venv kaputt / Pakete fehlen

Rebuild:
1. `.venv` umbenennen/entfernen
2. `python -m venv .venv`
3. `\.\.venv\Scripts\Activate.ps1`
4. `pip install -r requirements.txt`

## Quality Gates (Tranche A)

Zusätzliche Dev-Tools installieren:
- `pip install -r requirements-dev.txt`

Voller lokaler Gate-Lauf inkl. temporärem Serverstart:
- `\.\tools\run_quality_gates.ps1`

Gegen bereits laufenden lokalen Server:
- `\.\tools\run_quality_gates.ps1 -ReuseServer -BaseUrl http://127.0.0.1:5002`

Nur statische Gates ohne Live-Smoke:
- `\.\tools\run_quality_gates.ps1 -SkipLiveSmoke`

Python-Direktaufruf:
- `python .\tools\run_quality_gates.py --start-server --port 5012 --user karen --ids 112,101,110`

Ergebnisartefakte:
- `docs/_ops/quality_gates/run_<timestamp>/summary.md`
- `docs/_ops/quality_gates/run_<timestamp>/summary.json`
- Schritt-Logs `step_*.log`
- optional `server.out.log` / `server.err.log`

## API Smoke Tests (bestehend)

PowerShell Script:
- `tools/Test-WardrobeApi.ps1`

Minimal:
- GET `/healthz` → 200
- GET `/api/v2/health` → 200

## Git Hook (optional, lokal)

Installieren:
- `\.\tools\install_git_hooks.ps1`

Wirkung:
- Secret-Scan auf staged Dateien
- `ruff`-Critical-Check auf gestagte Python-Dateien

## Git Workflow (Minimum)

Vor Änderung:
- `git status`

Nach Änderung + bestandenem Gate:
- `git add .`
- `git commit -m "..."`

Empfehlung:
- Vor Push mindestens einmal `\.\tools\run_quality_gates.ps1`
