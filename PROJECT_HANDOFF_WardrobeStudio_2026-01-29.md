# Wardrobe Studio – Projekt-Handoff (Stand: 2026-01-29)

Dieses Dokument fasst **alle relevanten Aktivitäten, Entscheidungen und den aktuellen Systemzustand** zusammen, damit das Projekt in einem neuen Chat nahtlos fortgesetzt werden kann.

---

## 1) Ziel des Projekts

Transformation von einer Read-Only-Lösung (Dashboard) zu einem **vollständigen Wardrobe-Management-System (CRUD)**, steuerbar **direkt aus einem Custom GPT** über eine **lokale API**, die via **ngrok** erreichbar ist.

**Nutzer-Workflows (im Chat / via Custom GPT):**
- **Create**: Item anlegen inkl. Bild (Upload als Base64) + Metadaten
- **Update**: Metadaten partiell ändern (PATCH)
- **Delete**: Item löschen (DB + Dateisystem) mit Safety-Checks
- **Read**: Items listen, Details abfragen, Bilder-URLs liefern

---

## 2) Architektur (finaler Stand)

### Komponenten
1. **FastAPI (API v2)**  
   - Endpoints unter: `/api/v2/...`
   - Pydantic Models / Validierung
   - API-Key Auth per Header: `X-API-Key: <WARDROBE_API_KEY>`

2. **Legacy Flask Dashboard (UI)**  
   - UI wird **in FastAPI gemountet**, damit **eine einzige Domain/Port** reicht
   - Dashboard ist unter `/` erreichbar (Root)
   - Bilder werden unter `/images/...` serviert (Main Image URLs)

3. **ngrok (Hobby Account)**
   - Öffentliche Domain z.B.: `https://wardrobe.ngrok-app.com.ngrok.app`
   - Tunnelt lokalen Port **5002** nach außen
   - **ngrok Token/Authtoken** ist **nicht** der API-Key

---

## 3) Auth & Keys (wichtig)

### API-Key (Wardrobe API)
- Der Key ist ein **eigener Wardrobe-API-Key** (nicht ngrok).
- Muss in Requests als Header gesetzt werden:
  - `X-API-Key: <dein_key>`

### Häufiger Fehler (401 Unauthorized)
- Ursache: Header fehlte oder war falsch (z.B. versehentlich `WARDROBE_API_KEY=...` als Wert gesendet).
- Korrekt ist **nur der Key-String** ohne Prefix.

Beispiel (PowerShell):
```powershell
$apiKey="...dein_key..."
Invoke-RestMethod -Method Get -Uri "https://wardrobe.ngrok-app.com.ngrok.app/api/v2/items?user=karen" -Headers @{ "X-API-Key" = $apiKey }
```

---

## 4) API v2 – OpenAPI (Schema/Action-Definition)

Die Action/OpenAPI Definition wurde auf `apiKey` Security Scheme umgestellt:
- `components.securitySchemes.ApiKeyAuth`
- `in: header`
- `name: X-API-Key`
- global `security: - ApiKeyAuth: []`
- `/api/v2/health` ist **public** (security: [])

Wichtige OperationIds:
- `health`
- `listItems`
- `getItem`
- `createItem`
- `updateItem`
- `deleteItem`

Wichtige Felder in `ItemCreateRequest`:
- `image_main_base64`: Base64 (plain) oder DataURL `data:image/...;base64,...`
- `image_ext` optional
- Metadaten: `name`, `brand`, `category`, `color_primary`, etc.

---

## 5) CRUD Workflows – umgesetzt & getestet

### Create (mit Bild)
- Client (GPT/Python) konvertiert Bild → Base64
- Server: DB-Eintrag → ID → Ordner `user/slug_name_id` → schreibt `main.jpg`
- Transaktion: Bei Bildfehler → DB rollback

### Update (PATCH)
- Dynamisches partial update: nur gesendete Felder werden geändert

### Delete
- Jail-Check: Pfad muss innerhalb `02_wardrobe_images` liegen
- Löscht Ordner + DB Row

### Tests
- `pytest` lief erfolgreich (mindestens Health + CRUD Tests)  
- Hinweis: Warnung zu `starlette.middleware.wsgi` (deprecated) wurde beseitigt/vermindert durch **a2wsgi**.

---

## 6) Ontology Validation (Soft Mode) – eingeführt

### Ziel
- Qualitäts- und Konsistenz-Checks für Felder wie `category`, `color_primary`, `material_main`, `fit`, `collar`
- Gleichzeitig **Farbenvielfalt** zulassen (Mode braucht freie Varianten)

### Implementierter Modus
- **enabled: true**
- **mode: soft**
- **allow_legacy: true**
- `thresholds`: fuzzy/suggest

### Endpoints
- `GET /api/v2/ontology` → Status + counts + Werte
- `GET /api/v2/ontology/suggest?field=<...>&value=<...>` → canonical/suggestions
- `GET /api/v2/ontology/categories` etc.

### Beispiel-Beobachtungen
- `dunkelblau` → matched_by `legacy`, confidence 1.0
- `petrol` → matched_by `lexicon`, canonical `blue`, meta family `blue`
- `galaxy teal` → matched_by `none` → soft-mode Handling: `color_variant="galaxy teal"`, `needs_review=1`

### Review Queue
- `GET /api/v2/items/review?user=karen&limit=...&offset=...`
- Dient zur Nacharbeit freier Werte (z.B. Farbe) ohne den Nutzer zu blockieren.

---

## 7) Wichtige Debug-/Diagnose-Learnings

### Website „weg“ / 404 auf `/`
- Ursache: FastAPI lief, aber Root `/` war nicht geroutet → 404
- Lösung: **Flask Dashboard via WSGI in FastAPI mounten** auf `/` (Root) und API unter `/api/v2` lassen

### 404 auf `/api/v2/health`
- Ursache: falsche App gestartet oder Prefix doppelt/anders gemountet
- Lösung: robuste Mount-Logik in `api_main.py` (Router vs App) + Debug-Route

### Port belegt (Errno 10048)
- Ursache: Server wurde zweimal gestartet (Port 5002 bereits LISTENING)
- Lösung: Batch prüft Port und startet nicht erneut (oder killt PID optional)

---

## 8) Logging in Datei (produkttauglich)

### Ziel
- Runtime Logs in `logs/wardrobe.log`
- Startup/Crash-Logs in `logs/server_startup.log`
- RotatingFileHandler (10MB x 10 Backups)
- request_id pro Request (Header `X-Request-ID` + ContextVar)

### Neue/angepasste Dateien
- `src/logging_config.py` (neu): setup_logging + request_id ContextVar
- `src/api_main.py`: nutzt setup_logging + request_id Middleware + exception handler
- `src/server_entry.py` (neu/angepasst): startet uvicorn mit `log_config=None`, `use_colors=False`
- `Wardrobe_Studio_Starten.bat`: stabiler Start inkl. Port-Check, Logging, ngrok, Browser öffnen

**Wichtig:** Batch muss Server als Modul starten:
```bat
"%PYTHON_EXE%" -m src.server_entry
```

---

## 9) Batch/Windows Fallstricke (gelöst)

### PowerShell Prompt `>>`
- `>>` ist in PowerShell **kein Prompt**, sondern Umleitung → führt zu Fehlern wenn kopiert
- Empfehlung: Einzeilige Befehle verwenden oder korrekt multiline mit Backticks

### Batch Syntax-Fehler durch Klammern/Zeilenumbrüche
- `cmd.exe` ist extrem empfindlich bei `(...)` Blöcken und `echo` Text mit `)`
- Lösung: **keine PowerShell MessageBox** in BAT, keine Klammern im echo in Blocks, Logging strikt über Files

### „Fenster öffnet und schließt sofort“
- Ursache: BAT beendet sich bei Fehlern → Ausgaben nicht sichtbar
- Lösung: `pause` bei Fehlern + Server output in `server_startup.log`

---

## 10) Aktueller Startprozess (empfohlen)

### Lokal starten (Debug / direkt)
```powershell
cd C:\CapsuleWardrobeRAG
.\.venv\Scripts\python.exe -m src.server_entry
```

### Produktionsstart über BAT
- `C:\CapsuleWardrobeRAG\Wardrobe_Studio_Starten.bat`
- Erwartung:
  - Server auf Port 5002
  - ngrok tunnel auf Domain
  - Browser öffnet `http://localhost:5002/?user=karen`
  - Logs schreiben nach `logs/wardrobe.log` und `logs/server_startup.log`

### Schnelltests
- Lokal: `http://localhost:5002/api/v2/health`
- Public: `https://wardrobe.ngrok-app.com.ngrok.app/api/v2/health`
- Dashboard: `http://localhost:5002/?user=karen` bzw. public Domain

---

## 11) Daten & Test-Einträge

- Während Tests wurden Items wie `TEST ...` angelegt.
- Diese sollten nach Tests ggf. gelöscht werden (DELETE `/api/v2/items/{id}`).
- Ein konkreter Test-Eintrag (`#CW-61 TEST galaxy teal`) wurde gelöscht (DELETE OK).

---

## 12) Custom GPT Instructions / Knowledge

### Ziel
- Custom GPT führt **iteratives Briefing** aus (User, Anlass, Tage, No-Gos)
- ruft Inventory/ItemDetails ab
- erzeugt strukturierte Capsule-Ausgabe + „Magic Link“ fürs Dashboard
- Optionale Visualisierung (Flat Lay) im Stil eines Referenzbildes

### Einschränkung
- GPT Instructions Limit 8000 Zeichen → große Teile in **Knowledge Markdown** ausgelagert

### Auth in Actions
- Action Definition nutzt ApiKey Header `X-API-Key`
- In GPT Action Settings muss API-Key gesetzt werden

---

## 13) Nächste Schritte (Roadmap: „robust, produktsreif“)

### A) Ontologie & Farben-Strategie
- Ausbau Color Lexicon (Synonyme, Familien, Übersetzungen)
- Soft Mode beibehalten: Nutzer nicht blockieren
- Review-Workflow (UI/Chat) für `needs_review=1` Items

### B) API Robustheit
- Einheitliches Error-Format (inkl. request_id)
- Striktere Tests: Auth, Ontology Errors, Rollback, Jail-Check, File IO Fehler
- Rate limits / Payload size checks für Base64 Uploads (DoS-Schutz)

### C) Operatives Setup
- PID-File / Single-instance management (verhindert Doppelstart verlässlich)
- Health Check beim Start in BAT (curl/Invoke-RestMethod) + klare Fehlermeldung
- Optional: JSON Logging, Masking sensibler Felder

---

## 14) „Wenn etwas kaputt ist“ – Troubleshooting Kurzliste

1. **Port belegt (10048)**:
   - `netstat -ano | findstr :5002`
   - PID killen oder BAT `FORCE_RESTART=1`

2. **Server startet nicht / BAT schließt**:
   - `logs/server_startup.log` prüfen

3. **API 401**:
   - Header `X-API-Key` prüfen (nur Keystring!)

4. **Website 404**:
   - prüfen: läuft `src.api_main:app`?
   - Root `/` gemountet? (`app.mount("/", WSGI(...))`)

---

## Appendix: Wichtige Pfade

- Project Root: `C:\CapsuleWardrobeRAG\`
- Logs:
  - `C:\CapsuleWardrobeRAG\logs\wardrobe.log`
  - `C:\CapsuleWardrobeRAG\logs\server_startup.log`
- Images (serverseitig): `...\02_wardrobe_images\...` (je nach Konvention im Projekt)
- API Port: `5002`
- Public Domain (ngrok): `wardrobe.ngrok-app.com.ngrok.app`
