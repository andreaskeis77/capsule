# Analyse & Zusammenfassung: Verbesserungen an Ontologie und Codebasis (CapsuleWardrobeRAG)

Stand: 2026-01-25

Diese Notiz fasst die wichtigsten Verbesserungsmöglichkeiten zusammen, die sich aus der aktuellen Ontologie (Parts 01–09) und der vorhandenen Codebasis (`src/*.py`, SQLite-Schema, Dashboard/API, Ingestion) ableiten.  
Ziel ist **keine unmittelbare Umsetzung**, sondern eine **später belastbar umsetzbare Roadmap** mit klaren technischen Ansatzpunkten.

---

## 1. Executive Summary

### 1.1 Was bereits gut ist
- **Ontologie** ist strukturiert in klare Teile (Taxonomie, Item-Types, Attribute, Value-Sets, Regeln/Disambiguation, QA/Glossar).
- **Backend** (Flask + SQLite) ist bewusst minimalistisch und operativ, inkl. Image-Serving.
- **Ingestion** ist pragmatisch: Bilder/Text werden verarbeitet, Resultat wird gespeichert und Rohdaten werden archiviert.

### 1.2 Größte Hebel (später)
1) **Ontologie → Runtime-Enforcement**: Die Ontologie ist deutlich „mächtiger“ als das, was im Code aktuell erzwungen/validiert wird.  
2) **Datenmodell-Upgrade**: Das DB-Schema ist aktuell zu flach (nur wenige Textspalten), um Ontologie (Item-Type + Attribute) sauber abzubilden.  
3) **Ingestion-Härtung**: Validierung/Normalisierung (inkl. Rule-Engine) fehlt – das ist die Hauptquelle für inkonsistente Kategorien/Attribute.  
4) **API/Tooling für Visualisierung**: Für GPT/DALL·E (Flat-Lay) fehlen im Item-Detail stabile **direkt nutzbare Bild-URLs**.

---

## 2. Ontologie: Verbesserungen & Härtung

### 2.1 Versionierung & „Stabilitätsvertrag“
**Beobachtung:** In Part 01 ist eine Ontologie-Version angegeben (z. B. „0.9.0“).  
**Empfehlung:** Einen klaren „Stabilitätsvertrag“ ergänzen:
- **SemVer-Regeln**: Breaking Changes nur bei Major-Version.
- **Deprecated-IDs**: Offizielles Deprecation-Handling (z. B. `deprecated: true`, `replaced_by: ...`).
- **Changelog**: Minimaler CHANGELOG pro Release, damit Migrationen nachvollziehbar bleiben.

### 2.2 Legacy-/Alias-Mapping (kritisch für Bestandsdaten)
**Beobachtung:** In Bestandsdaten und älteren Runs tauchen Category-Strings auf, die **nicht** in der aktuellen Taxonomie liegen (z. B. „cat_blazer“ vs. tiefere, konsistente Hierarchie).  
**Empfehlung:**
- Eine Ontologie-Datei `legacy_mappings` oder `alias_map` einführen:
  - `cat_blazer -> cat_apparel_outerwear_..._blazer` (konkret nach eurer Hierarchie)
  - analog für `cat_jacket(s)`, `cat_top_tshirt(s)`, etc.
- Diese Map ist die Grundlage für:
  - **Backfill/Migration** der DB
  - **Abwärtskompatible Filter** im Dashboard
  - **Robuste GPT-Ausgaben**, falls Altdaten auftauchen

### 2.3 „Rule Engine“ operationalisieren (Part 08/09)
**Beobachtung:** Die Ontologie beschreibt eine **post_extraction_normalizer**-Logik (Regeln, Prioritäten, disambiguation), aber im Code wird diese Logik aktuell nicht umgesetzt.  
**Empfehlung:** Später eine konkrete Engine implementieren:
- Input: Roh-Extrakt (vom Vision/Text-Modell)
- Schritte:
  1. **Schema-Validation** (Pflichtfelder, Typen)
  2. **Value-Set Validation** (z. B. `vs_*` nur erlaubte Werte)
  3. **Regel-Apply** nach Priorität (Brand/Shop Normalization, Size-Disambiguation, Material-Fehlklassifikationen etc.)
  4. Output: Normalisierte Felder + optional Konfidenzen/Warnungen

**Nutzen:** Weniger Datenmüll, konsistente Filterbarkeit, reproduzierbares Verhalten.

### 2.4 Item-Types stärker als „Contract“ nutzen (Part 03)
**Beobachtung:** Item-Types definieren pro Typ `required_attributes`/`optional_attributes`, aber das System speichert derzeit nur eine kleine Menge generischer Textfelder.  
**Empfehlung:**
- Item-Type als **zentrales Klassifikationsfeld** (`item_type_id`).
- Attribute nicht als zufällige Textfelder, sondern als strukturierte Attribute (siehe DB-Teil unten).
- Später: Validierung „Wenn item_type_id == X → required_attributes müssen vorhanden sein“.

### 2.5 Attribute-Design: „raw“ vs. „normalized“
**Problemklasse:** Viele Felder haben in der Praxis zwei Bedeutungen:
- (a) Normalisierte Codes/IDs (value-sets, Ontologie-IDs)
- (b) Rohtext aus Shop/Textdateien („Modern Fit“, „Peak-Lapel“, „Global Kent“)

**Empfehlung:** Für zentrale Felder konsequent trennen:
- `*_raw`: Originaltext
- `*_id` bzw. `*_norm`: normalisierte Ontologie/Value-Set-ID
- optional `*_confidence`, `*_source`

Beispiel:
- `fit_raw: "Modern Fit"`  
- `fit_type_id: "fit_regular"` (oder euer Value-Set)  
- `fit_confidence: 0.73`  
- `fit_source: "vision|text|rule"`

### 2.6 QA/Glossar (Part 09) als automatisierte Tests
**Beobachtung:** Part 09 listet typische Ambiguitäten (z. B. Größen-Interpretation, Leder vs. Kunstleder, Brand aus Marketplace).  
**Empfehlung:** Später ein „Conformance Test Pack“:
- Für jede Top-Ambiguität 1–3 Testfälle (Input → erwarteter normalisierter Output).
- Damit kann man Rule-Engine und Ingestion refactoren, ohne Funktionalität zu verlieren.

---

## 3. Codebasis: Verbesserungen & technische Schulden

### 3.1 Datenbank-Schema: vom „flach“ zum „ontologie-kompatibel“
**Ist-Zustand:** Tabelle `items` enthält primär Textspalten (`brand`, `category`, `fit`, `collar`, ...).  
**Schmerzpunkte:**
- Keine Trennung zwischen raw/norm.
- Kein Platz für `item_type_id` und strukturierte Attribute.
- Keine Versionierung/Migrations-Mechanik.

**Empfohlene Zielrichtung (später):**
- Minimaler Evolutionspfad ohne Full-ORM:
  - `items` erweitern um:
    - `item_type_id TEXT`
    - `category_id TEXT` (statt/zusätzlich zu `category`)
    - `attributes_json TEXT` (JSON) für beliebige Attribute aus Part 04–07
    - `raw_json TEXT` (optional) zur Speicherung des Roh-Extrakt-JSON
    - `ontology_version TEXT`
    - `ingestion_model TEXT`, `ingestion_timestamp`
- Alternativ (größerer Umbau): separate Tabellen `item_attributes`, `materials`, `sizes` etc.

### 3.2 Schema-Migrationen sauber machen
**Beobachtung:** Es existieren Helferskripte (`update_db_schema.py`), aber keine robuste Migration-Strategie.  
**Empfehlung:**
- Ein simples Migration-System (ohne Alembic):
  - Tabelle `schema_migrations(version TEXT PRIMARY KEY, applied_at TEXT)`
  - Migration-Skripte `migrations/0001_*.sql`, `0002_*.sql`, …
  - Idempotente Ausführung bei Start/Setup
- Vorteil: reproduzierbar und versioniert, auch auf anderen Rechnern.

### 3.3 Ingestion Pipeline: Validierung, Normalisierung, Medienrobustheit
**Beobachtungen (konkret):**
- `VALID_EXTENSIONS` erlaubt `.heic`, `.jfif`, aber es erfolgt **keine echte Konvertierung** – MIME wird nur „umgetaggt“. Das bricht bei echten HEIC-Dateien typischerweise.
- Modellname ist hart verdrahtet und kann in der Praxis zu Deploy-/API-Problemen führen.
- Ontologie-IDs werden nicht „whitelisted“ (kein Abgleich gegen erlaubte Kategorien/Value-Sets).

**Empfehlungen (später):**
- HEIC/JFIF robust machen:
  - HEIC → JPEG konvertieren (z. B. pillow-heif / ImageMagick / platform-specific)
  - JFIF sauber als JPEG behandeln
- Ergebnis-JSON validieren:
  - JSON-Schema (minimal) + Ontologie-Whitelists
  - Fallback-Strategie: bei ungültigen IDs → Parent-Kategorie oder `unknown`
- Rule-Engine integrieren (siehe Ontologie 2.3)
- Logging erweitern: pro Item eine „Ingestion Report Card“ (Warnungen, Normalisierungen, Confidence).

### 3.4 API / Dashboard: Daten & Bilder konsistent ausliefern
**Beobachtungen:**
- Das Dashboard kennt `all_images` (aus Ordnerlisting), aber **die API** (`/api/v1/item/<built-in function id>`) liefert nur DB-Spalten.
- Magic-Link Filter `?ids=...` kann bei `ids` ohne valide Zahlen zu SQL `IN ()` führen (Syntaxfehler) und sollte „sicher degradieren“.

**Empfehlungen (später):**
- `getItemDetail` erweitert um:
  - `main_image_url` (z. B. `/images/<image_path>/main.jpg` wenn vorhanden)
  - `image_urls` (Liste)
  - optional `thumbnail_url`
- Robustheit: bei leerer validierter `id_list` → Fallback auf User-Query oder leere Ergebnisliste ohne SQL-Fehler.
- API-Contract dokumentieren:
  - Felder, Typen, optionale Felder, Backward compatibility.

### 3.5 Konsistenz der User-IDs (Profile vs DB/API)
**Beobachtung:** Profile verwenden teils `karen_01`, DB/API arbeiten mit `karen`.  
**Empfehlung:** Später eine eindeutige Identitätsschicht:
- `user_id` (stabil, z. B. `karen`)
- `profile_id` oder `profile_version`
- Niemals zwei Konzepte unter „user_id“ mischen.

### 3.6 Tooling & Quality Gates
Empfohlene spätere Engineering-Standards:
- `ruff` + `black` + `mypy` (oder pyright)
- `pytest` (Unit + kleine Integration gegen Test-DB)
- Pre-commit hooks
- Minimaler CI-Workflow (GitHub Actions), der Lint + Tests ausführt

---

## 4. Empfohlene Roadmap (später, in sinnvollen Stufen)

### Stufe A — „Harte Kanten glätten“ (Low Effort, High Impact)
- API: Bild-URLs in Item-Detail
- Magic-Link: `ids`-Filter robust
- Ingestion: HEIC-Konvertierung/Handling
- `check_db.py`: Feldnamen an DB-Schema anpassen (z. B. `model_name` entfernen/ersetzen)

### Stufe B — Ontologie Enforcement (Qualität & Konsistenz)
- Ontologie in maschinenlesbares Format bringen (YAML/JSON als Artefakt)
- Whitelisting/Validation in Ingestion
- Legacy-Mapping implementieren + DB Backfill

### Stufe C — Datenmodell-Evolution
- `item_type_id`, `category_id`, `attributes_json`, `raw_json`, `ontology_version`
- Migration-System einführen

### Stufe D — Regel-Engine & Conformance Tests
- Rule Engine gemäß Part 08
- Testpack gemäß Part 09
- Konfidenzen/Warnings in DB + UI sichtbar machen

---

## 5. Konkrete „Issue-Liste“ (als späterer Backlog)

### Ontologie
- [ ] Legacy/Alias-Mapping ergänzen (Category/Fit/Collar-Altwerte)
- [ ] Deprecation-Mechanik + Changelog
- [ ] Machine-readable Exports + Loader
- [ ] Conformance Testfälle aus Part 09 ableiten

### Backend/API
- [ ] `/api/v1/item/<built-in function id>`: `main_image_url`, `image_urls` ergänzen
- [ ] `?ids=`: Empty-ID-List sauber behandeln
- [ ] Optional: `/api/v1/inventory` Filter-Parameter (category, color_family, item_type_id)

### Ingestion
- [ ] HEIC/JFIF robust konvertieren
- [ ] Ontologie-Validation + Value-Set Whitelists
- [ ] Rule-Engine Schritt nach Extraktion
- [ ] Ingestion Report (Warnings/Confidence)

### Datenbank
- [ ] Schema-Versionierung + Migrationen
- [ ] Strukturierte Attribute via JSON-Spalte oder relationale Tabellen
- [ ] Roh-Extrakt persistieren (`raw_json`)

---

## 6. Anhang: Hinweis zur GPT-Konfiguration (Instructions + OpenAPI)
Die aktuelle GPT-Instructions-Struktur (Briefing → API → Output → optional Visualisierung) ist gut.  
Für die spätere Visualisierung ist jedoch entscheidend, dass die API pro Item **direkt nutzbare Bild-URLs** liefert; `image_path` allein reicht für ein GPT nicht zuverlässig aus.

---

*Dokument erstellt als technische Sicherungsnotiz für spätere Umsetzungsschritte.*
