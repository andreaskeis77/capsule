# Chat Handoff – Wardrobe Studio (Copy/Paste)

## Projektziel
Wardrobe Studio: Lokales Wardrobe-Management (FastAPI API v2 + Flask Dashboard) mit Ontologie, DB, Bildern und optionalem Zugriff via ngrok. Fokus: Executive/Private Kategorisierung + saubere UI zur Sichtung.

## Arbeitsregeln (wichtig)
- Ein Schritt pro Anweisung → Output posten → erst dann nächster Schritt
- Bei Dateiänderungen: komplette Datei liefern
- Nach Änderung: Smoke-Test + Git Commit
- Skeptisch/prüfend arbeiten (Logs/HTTP Status)

## Umgebung
- Windows / PowerShell
- Repo: `C:\CapsuleWardrobeRAG`
- Python: `.venv`
- Git: aktiv, requirements.txt versioniert
- Start: `Wardrobe_Studio_Starten.bat`
- Port: 5002
- Local Dashboard: `http://127.0.0.1:5002/?user=karen`
- Health: `http://127.0.0.1:5002/healthz`
- API v2: `http://127.0.0.1:5002/api/v2/health`
- ngrok fixed: `https://wardrobe.ngrok-app.com.ngrok.app`

## Architektur-Quick Map
- Start: `src/server_entry.py`
- ASGI App: `src/api_main.py` (mountet API v2 + Flask)
- API v2: `src/api_v2.py`
- Dashboard: `src/web_dashboard.py`
- Templates: `templates/index.html`, `templates/item_detail.html`
- Ontologie: `ontology/*.md` + `ontology_overrides.yaml` + `color_lexicon.yaml` (Runtime: `src/ontology_runtime.py`)
- Tools: `tools/Test-WardrobeApi.ps1`
- Logs: `logs/` (startup/server/ngrok out+err)

## Aktueller Status
- Server + Dashboard + ngrok funktionieren stabil (nach venv rebuild).
- Batch Start funktioniert wieder.
- requirements.txt im Repo.

## Nächste Schritte (typisch)
1) UI verbessern: Filter nach Oberkategorien (Hosen, Röcke, Schuhe, Taschen, Blusen, Kleider etc.)
2) UI: Grid mit kleinen Thumbnails + Klick → Modal/Lightbox + “Details” Seite
3) Batch optional kosmetisch/encoding (Umlaut "Ö" in Logs)
4) Snapshot-Tool (optional): tools/handoff_snapshot.ps1 erzeugt docs/_snapshot/latest.md
