# HANDOFF RUNTIME STATE – Template

Fill/verify this when doing major releases or when the environment changes.

## Environment
- OS: Windows (PowerShell 5.1)
- Repo: `C:\CapsuleWardrobeRAG`
- Python: 3.12
- venv: `.venv`

## Start Commands
- Recommended: `Wardrobe_Studio_Starten.bat`
- Manual: `python -m src.server_entry`

## URLs
- Dashboard: `http://127.0.0.1:5002/?user=karen`
- Health: `http://127.0.0.1:5002/healthz`
- API v2 health: `http://127.0.0.1:5002/api/v2/health`

## Admin
- Admin mode: `/?user=karen&mode=admin`
- Default restriction: local only (127.0.0.1)

## Secrets
- `.env` required locally; never copy into handoff bundles.