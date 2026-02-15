# CapsuleWardrobeRAG – Arbeitsstand sichern (Ontologie-Validierung / Soft-Normalisierung)

Stand: 2026-01-25 (aus diesem Chat)

Dieses Dokument fasst zusammen, **was wir technisch umgesetzt und geändert haben**, welche **Checks** bereits gelaufen sind und wie du den Stand **robust sichern** kannst (Code + Daten + Konfiguration).

---

## 1) Zielbild der Änderungen

Wir haben die API von einem „frei textigen“ Metadaten-Modell in Richtung **konsistenter Ontologie-Werte** weiterentwickelt – ohne den Nutzer mit Rückfragen zu überrollen.

Kernprinzip: **Soft-Validation**
- Wenn ein Wert eindeutig ist (Kanonwert, Synonym, Override, Fuzzy über Schwelle), wird er **automatisch normalisiert**.
- Wenn nicht eindeutig: **400** mit konkreten **Vorschlägen** (damit das GPT eine gezielte Rückfrage stellen kann).
- Bestehende DB-Werte werden **nicht kaputtgemacht**: **Legacy ist erlaubt** (kompatibel zum Bestand).

---

## 2) Laufende Konfiguration (Environment)

### 2.1 .env (neue/ergänzte Variablen)

```env
WARDROBE_ONTOLOGY_MODE=soft
WARDROBE_ONTOLOGY_ALLOW_LEGACY=1
WARDROBE_ONTOLOGY_FUZZY_THRESHOLD=0.92
WARDROBE_ONTOLOGY_SUGGEST_THRESHOLD=0.78
WARDROBE_ONTOLOGY_DIR=ontology
WARDROBE_ONTOLOGY_OVERRIDES_FILE=ontology/ontology_overrides.yaml
```

**Bedeutung:**
- `soft`: Auto-Normalisierung, sonst 400 + Suggestions.
- `ALLOW_LEGACY=1`: akzeptiert DB-Altwerte (verhindert Breaks).
- `*_THRESHOLD`: Steuerung der Fuzzy-Entscheidung und Vorschlagsliste.
- `*_DIR`: Verzeichnis deiner Ontologie-MDs (bei dir: `C:\CapsuleWardrobeRAG\ontology`).
- `OVERRIDES_FILE`: Erweiterungspunkt für Alltagssprache.

### 2.2 Ontologie-Dateien

Die Ontologie liegt bereits korrekt in `ontology/` (alle Teile 01–09). Der Loader nutzt aktiv diese vier Dateien:

- `ontology_part_02_taxonomy.md`
- `ontology_part_04_attributes_value_sets_core.md`
- `ontology_part_05_materials_sustainability_certifications.md`
- `ontology_part_06_fits_cuts_collars_sizes.md`

---

## 3) Code-Änderungen / neue Module

### 3.1 Neu: Ontologie-Runtime Loader + Normalizer
- **Datei:** `src/ontology_runtime.py`
- **Funktionen:**
  - YAML-Extraktion aus den MD-Dateien (auch ohne abschließenden Fence).
  - Index-Building für Kategorien, Value Sets (colors/fits/collars) und Materialien.
  - **Legacy-Load aus DB**: distinct values pro Feld (category, color_primary, …).
  - **Overrides** (konfigurierbar) werden **vor** Legacy angewendet.
  - Normalisierung liefert strukturierte Informationen (matched_by, confidence, suggestions).

### 3.2 Settings erweitert
- **Datei:** `src/settings.py`
- Neu: Ontologie-Settings + Pfad zur Overrides-Datei.

### 3.3 API-Middleware & Logging gehärtet
- **Datei:** `src/api_main.py`
- Ziel: robuste Logs + Request-ID:
  - `X-Request-ID` wird erzeugt oder übernommen.
  - einheitliche Fehlerantworten enthalten `request_id`.
  - Logging (rotating file) nach `04_user_data/logs/api.log`.

### 3.4 API v2 um Ontologie-Validierung ergänzt
- **Datei:** `src/api_v2.py`
- Neu/erweitert:
  - Ontologie wird beim Start geladen (wenn `mode != off`).
  - Normalisierung/Validierung wird in Create/Update/Validate angewendet.
  - **Debug-Endpunkte:**
    - `GET /api/v2/ontology` (liefert geladenes Set + thresholds + legacy)
    - `GET /api/v2/ontology/suggest?field=...&value=...` (Debug: canonical + Vorschläge)
  - `POST /api/v2/items/validate` liefert „dry-run“ inkl. Normalisierungsmetadaten.

### 3.5 Overrides-Datei (neu)
- **Datei:** `ontology/ontology_overrides.yaml`
- Zweck: Alltagssprache → Kanonwert, z. B.:
  - `dunkelblau` → `blue`
  - `hellblau` → `blue`
  - etc.

---

## 4) Verifikation / Tests (bereits erfolgt)

### 4.1 API Health
- `GET /api/v2/health` funktioniert (direkt im Browser getestet).

### 4.2 CRUD-Flows (bereits erfolgreich getestet)
- Item anlegen (Create) inkl. Bildspeicherung
- Item editieren (Update)
- Item löschen (Delete)
- Das lief über die GPT-Action und auch lokal via PowerShell.

### 4.3 Ontologie geladen (bestätigt)
PowerShell-Aufruf:
- `GET https://wardrobe.ngrok-app.com.ngrok.app/api/v2/ontology` mit `X-API-Key`

Ergebnis:
- `enabled: True`
- `mode: soft`
- `allow_legacy: True`
- `categories_count: 41`
- Value Sets (colors/fits/collars/materials) vorhanden

### 4.4 Erkenntnis: „legacy“-Werte dominieren ohne Overrides
Beispiel:
- `dunkelblau` wurde als `legacy` erkannt und als canonical zurückgegeben.
- Das ist beabsichtigt, um Bestand nicht zu brechen.

**Verbesserung:**
- Overridemechanismus eingeführt → `dunkelblau` kann auf `blue` normalisiert werden, ohne Bestandswerte „hart“ zu migrieren.

---

## 5) Empfohlene Sicherungsstrategie (produkttauglich)

### 5.1 Quellcode: Git (empfohlen)
Wenn du noch kein Git verwendest, ist das der wichtigste Schritt.

1) Repo initialisieren (falls nicht vorhanden):
```powershell
git init
```

2) `.gitignore` sicherstellen:
- `.env` **nie** committen
- `03_database/` und `02_wardrobe_images/` je nach Wunsch:
  - Entweder komplett ignorieren (und separat sichern)
  - oder **nur** per Release/Backup-Mechanismus versionieren

3) Commit-Logik:
- ein Commit für „Ontology soft validation + debug endpoints“
- Tag setzen:
```powershell
git add .
git commit -m "Ontology: soft validation + overrides + debug endpoints"
git tag v2.2.0-ontology-soft
```

### 5.2 Konfiguration: .env.example anlegen
Empfehlung: eine Datei `env.example` (ohne echte Secrets) hinzufügen, damit Setup reproduzierbar ist:
- `WARDROBE_API_KEY=__SET_ME__`
- `WARDROBE_ONTOLOGY_*` etc.

### 5.3 Daten: DB + Images separat sichern
Mindestens wöchentlich/bei größeren Änderungen:

- Datenbank:
  - `03_database/wardrobe.db` (oder dein konfigurierter Pfad)
- Bilder:
  - kompletter Ordner `02_wardrobe_images/`

**Schnellbackup als Zip (Windows):**
- Rechtsklick → „Senden an → ZIP“
oder PowerShell (optional):
```powershell
Compress-Archive -Path .\03_database\wardrobe.db, .\02_wardrobe_images\ -DestinationPath .\backup_wardrobe_$(Get-Date -Format yyyyMMdd_HHmm).zip
```

### 5.4 Betriebslogs sichern (für Debug)
- `04_user_data/logs/api.log` (rotating)
- bei Incidents: Log + request_id aus API-Error speichern.

### 5.5 Ngrok / API-Key
- API-Key bleibt **lokal** in `.env`.
- GPT-Action Header: `X-API-Key: <dein key>` (kein “ngrok dashboard key” nötig).
- Ngrok Token ist für den Tunnel – der API-Key ist für deinen API-Schutz.

---

## 6) Wie geht es inhaltlich weiter (Empfehlung)

### 6.1 Nächste technische Schritte (nach Priorität)
1) **Bestandsdaten-Migration (optional, aber empfehlenswert)**  
   Ein Script oder Admin-Endpoint:
   - Dry-run Modus (nur Report)
   - dann selektive Normalisierung (z. B. `dunkelblau -> blue`)
   - Audit-Log pro Änderung

2) **Erweiterte Synonyme / Overrides**  
   In `ontology_overrides.yaml` wachsen lassen, iterativ nach echten Nutzerinputs.

3) **OpenAPI / Action Schema**  
   Falls du neue Endpunkte (ontology/suggest) im GPT nutzen willst, Schema entsprechend erweitern.

4) **Testabdeckung ausbauen**  
   - Tests speziell für Ontology Soft/Strict Behavior.
   - Tests für Override-Priorität vs. Legacy.

---

## 7) Weiterarbeiten: gleicher Chat oder neuer Chat?

**Empfehlung:** Im selben Chat weiterarbeiten, solange wir in dieser Implementationslinie bleiben (Ontologie/Validierung/Robustheit).  
Gründe:
- weniger Kontextverlust (API-Key-Header-Themen, Endpunkte, Designentscheidungen)
- schnelleres Debugging

**Neuen Chat** empfehle ich erst, wenn:
- wir ein neues großes Thema starten (z. B. “Capsule Generator + Visualisierung Pipeline”),
- oder du einen “Clean Room” für ein Refactor/Release-Plan brauchst.

Wenn du dennoch einen neuen Chat möchtest: Lege dieses Dokument + dein aktuelles OpenAPI-Schema als Startkontext hinein, dann ist der Übergang sauber.

---

## 8) Kurzer Status-Check (Definition of Done für diese Phase)

Erfüllt:
- CRUD stabil (Create/Update/Delete)
- API-Key Auth funktioniert (X-API-Key)
- Ontologie geladen & sichtbar über `/api/v2/ontology`
- Suggest/Debug Endpoint vorhanden
- Legacy-Modus verhindert Breaking Changes

Offen / optional:
- Migration der Bestandswerte (kontrolliert, mit Dry-run)
- Synonym-/Override-Ausbau
- zusätzliche Tests für Ontologie-Modi

---
