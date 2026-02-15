# Working Agreement (Andreas ↔ ChatGPT)

## Ziel
Wir arbeiten am Projekt "CapsuleWardrobeRAG / Wardrobe Studio" (FastAPI + Flask Dashboard + Ontologie + DB + ngrok).
Priorität: Stabilität, Reproduzierbarkeit, saubere Versionskontrolle, nachvollziehbare Schritte.

## Arbeitsmodus (verbindlich)
1. **Ein Schritt pro Anweisung**
   - Du führst den Schritt aus und postest Output/Logs.
   - Ich prüfe den Output und gebe dann den nächsten Schritt.
2. **Keine parallelen Aufgaben / keine “Batch von Anweisungen”**
   - Wenn mehrere Dinge nötig sind: Ich nummeriere sie, aber du machst immer nur den nächsten Schritt.
3. **Vollständige Datei bei Code-Änderungen**
   - Wenn eine Datei geändert werden soll, liefere ich **immer den kompletten Inhalt** der Datei (keine Diff-Schnipsel).
4. **Checks nach jeder Änderung**
   - Minimaler Smoke-Test (z.B. Start, /healthz, /api/v2/health, Dashboard).
   - Danach Git-Commit mit klarer Message.
5. **Skeptisch arbeiten**
   - Keine Annahmen ohne Nachweis (Logs, `tree`, `git status`, HTTP status codes).
   - Bei Unsicherheit: erst messen/prüfen, dann ändern.

## Umgebung / Grundannahmen
- OS: Windows (PowerShell), Arbeitsverzeichnis: `C:\CapsuleWardrobeRAG`
- Python via `.venv`
- Git ist aktiv (lokales Repo)
- Start via `Wardrobe_Studio_Starten.bat` oder manuell `python .\src\server_entry.py`
- Port: `5002`
- Local: `http://127.0.0.1:5002/?user=karen`
- Health: `http://127.0.0.1:5002/healthz`
- API v2: `http://127.0.0.1:5002/api/v2/health`
- ngrok fixed domain: `https://wardrobe.ngrok-app.com.ngrok.app`

## Definition of Done (für ein Feature)
- Implementiert
- Lokal getestet (Browser + Healthchecks)
- Logs sauber (keine Exceptions beim Start)
- Commit vorhanden
- (Optional) Snapshot aktualisiert
