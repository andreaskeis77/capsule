# Runbook – Start/Stop/Debug

## Quick Start (empfohlen)

0) Konfiguration anlegen (einmalig)
   - Kopiere `.env.example` → `.env`
   - Setze mindestens `WARDROBE_API_KEY` (wird für API-Auth, Admin-Save/Delete und GPT Actions benötigt)
   - Hinweis: `.env` ist absichtlich NICHT versioniert (Security Baseline)

1) venv aktivieren:
   - PowerShell: `.\.venv\Scripts\Activate.ps1`

2) Start via Batch:
   - `.\Wardrobe_Studio_Starten.bat`

URLs:
- Local Dashboard: `http://127.0.0.1:5002/?user=karen`
- Local Docs: `http://127.0.0.1:5002/docs`
- Health: `http://127.0.0.1:5002/healthz`
- API v2 health: `http://127.0.0.1:5002/api/v2/health`

ngrok (fixed domain):
- `https://wardrobe.ngrok-app.com.ngrok.app/?user=karen`
- `https://wardrobe.ngrok-app.com.ngrok.app/docs`

## Start ohne ngrok (PowerShell)
- In PowerShell Environment Variable setzen:
  - `$env:START_NGROK="0"`
  - `.\Wardrobe_Studio_Starten.bat`
- Zurücksetzen:
  - `Remove-Item Env:START_NGROK -ErrorAction SilentlyContinue`

## Manuell starten (Debug Mode)
- `python .\src\server_entry.py`
- Stop: `CTRL+C`

## Logs
Ordner: `logs/`
Wichtige Files:
- `startup.log` (Batch Ablauf)
- `server.out.log`, `server.err.log`
- `ngrok.out.log`, `ngrok.err.log`

Rotation: Batch rotiert in `*_YYYYMMDD-HHMMSS.log`

## Häufige Probleme

### Batch hängt bei "Warte auf Readiness."
Check:
- `http://127.0.0.1:5002/healthz`
- `logs/server.err.log` (Tail)

Ursachen:
- Port belegt
- Venv kaputt / dependencies fehlen
- Serverprozess nicht gestartet

### Port 5002 belegt
Optionen:
- Batch mit `FORCE_RESTART=1` starten
- oder manuell prüfen:
  - `Get-NetTCPConnection -State Listen -LocalPort 5002`

### Venv kaputt / Pakete fehlen
Rebuild:
1) `.venv` umbenennen/entfernen
2) `python -m venv .venv`
3) `.\.venv\Scripts\Activate.ps1`
4) `pip install -r requirements.txt`

## API Smoke Tests
PowerShell Script:
- `tools/Test-WardrobeApi.ps1` (manuell nutzbar)

Minimal:
- GET `/healthz` → 200, `{"status":"ok"}`
- GET `/api/v2/health` → 200

## Git Workflow (Minimum)
- vor Änderung: `git status`
- nach Änderung + Test:
  - `git add .`
  - `git commit -m "Message"`