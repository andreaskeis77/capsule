# Architecture Requirements Dossier (ARD)
## Capsule Studio / Capsule Wardrobe Project

Stand: 2026-03-26

## 1. Purpose and Scope

Dieses Dokument ist das verbindliche Architektur- und Betriebsdossier des Projekts **Capsule Studio / Capsule Wardrobe Project**.
Es definiert die aktuelle Zielarchitektur, die technischen und betrieblichen Anforderungen, die relevanten Infrastrukturkomponenten, die fachlichen Architekturbausteine sowie die Regeln zur Pflege und Validierung dieser Architektur.

Das ARD ist **verbindlich** zu nutzen:
- bei architekturwirksamen Änderungen,
- vor jedem Release,
- bei Änderungen an Infrastruktur, Sicherheit, Persistenz, API-Contracts, Ingestion, Ontologie oder Betriebsabläufen.

Änderungen am System gelten nur dann als vollständig, wenn **Code, Tests und Referenzdokumente** konsistent aktualisiert wurden.

## 2. System Mission

Capsule Studio ist ein lokal entwickeltes, operativ abgesichertes System zur:
1. Verwaltung eines realen Wardrobe-Bestands,
2. Analyse und Strukturierung von Kleidungsstücken auf Basis einer Ontologie,
3. Planung von Capsule Wardrobes,
4. kontrollierten Pflege des Bestands über API, Dashboard und unterstützende Automations-/Tooling-Flows.

Das System ist kein reines Demo-Projekt, sondern ein produktnahes, evolvierbares Engineering-System mit:
- API,
- Dashboard/UI,
- Ingestion,
- Recovery,
- Ontology Runtime,
- Run Registry,
- Handoff-/Snapshot-Fähigkeit,
- Security- und Quality-Gates.

## 3. Canonical Repositories and Ownership

### 3.1 Source Repository
- GitHub Repository: `https://github.com/andreaskeis77/capsule`

### 3.2 Source of Truth
Das Git-Repository ist die primäre technische Source of Truth.
Chats, Zwischenanalysen und operative Notizen sind Hilfsmittel, aber keine kanonische Architekturquelle.

## 4. System Context

### 4.1 Primary Internal Components
- **FastAPI API v2**
- **Flask Dashboard (legacy UI), in FastAPI gemountet**
- **SQLite** als operative Persistenz
- **Dateisystem** für Bildablage
- **Ontology Runtime**
- **Ingestion Pipeline**
- **Recovery / Quarantine / Trash Flows**
- **Run Registry**
- **Handoff / Snapshot Tooling**
- **Quality Gates / Secret Scan / Repo Metrics / Reports**

### 4.2 Primary External Components
- **GitHub**
- **Contabo VPS**
- **Cloudflare**
- **INWX**
- **ngrok**

## 5. Runtime and Deployment Architecture

### 5.1 Core Runtime Topology
Das System läuft als kombinierter Dienst mit:
- **FastAPI** als API-Schicht
- **Flask Dashboard** als UI-Schicht, in FastAPI gemountet
- gemeinsamer lokaler Runtime auf Port 5002

### 5.2 Public Exposure
Lokaler Betrieb kann über **ngrok** gezielt nach außen exponiert werden.
Die Public Exposure ist kontrolliert und nicht identisch mit der internen API-Key-Logik.

### 5.3 Current Infrastructure Inventory
- **Domain:** `capsule-studio.de`
- **Registrar:** INWX
- **DNS / Proxy / Security Layer:** Cloudflare
- **ngrok public domain:** `wardrobe.ngrok-app.com.ngrok.app`
- **Contabo VPS instance:** `vmd193069`
- **VPS OS:** Windows
- **Public IPv4:** `84.247.164.122`

### 5.4 Infrastructure Role Mapping
- `capsule-studio.de` ist die projektrelevante kanonische Domain.
- Cloudflare verarbeitet DNS und vorgelagerte Traffic-/Security-Funktionen.
- ngrok dient als kontrollierter Tunnel für öffentliche Entwicklungs-/Betriebszugriffe.
- Der Contabo-VPS ist die aktuelle serverseitige Zielumgebung.

## 6. Logical Architecture

### 6.1 Presentation Layer
- HTML Templates unter `templates/`
- Flask Dashboard für Übersicht, Detailansicht, Admin-Bearbeitung
- Filter- und Anzeige-Logik für Wardrobe-Bestände

### 6.2 Interface Layer
- FastAPI API v2 unter `/api/v2/...`
- Legacy `/api/v1/...` nur soweit betrieblich erforderlich
- klare Trennung zwischen UI-Zugriff und API-Contract

### 6.3 Application Layer
- CRUD-Operationen
- Ingestion-Orchestrierung
- Recovery / Repair Flows
- Review- und Nacharbeitslogik
- Handoff- und Snapshot-Orchestrierung

### 6.4 Domain Layer
- Wardrobe-Objekte
- Kategorien, Attribute, Context, Review-Zustände
- Ontologie-basierte Klassifikation und Normalisierung

### 6.5 Infrastructure Layer
- SQLite
- Dateisystem für Images
- Logging
- Run Registry
- Secret Scan / Repo Metrics / Quality Gates
- Batch-/PowerShell-Start- und Betriebslogik

## 7. Data and State Architecture

### 7.1 Primary Persistent Data
- `items`
- `runs`
- `run_events`

### 7.2 File-Based State
- Bildordner
- Trash / Quarantine
- Snapshot-/Handoff-Artefakte
- Metrics-/Ops-Artefakte

### 7.3 State Principles
- Metadaten liegen primär in SQLite.
- Bilder liegen primär im Dateisystem.
- Persistenz und Filesystem bilden gemeinsam den operativen Systemzustand.
- Ingestion- und Recovery-Logik müssen beide Ebenen konsistent halten.

## 8. Ontology as a First-Class Architectural Component

Die Ontologie ist kein bloßer Wissensanhang, sondern ein **verbindlicher fachlicher Architekturbaustein**.

### 8.1 Rolle der Ontologie
Die Ontologie definiert:
- Taxonomie / Kategorien
- Item Types
- Attribute
- Value Sets
- Regeln und Disambiguation
- QA-/Glossar-Wissen für Nacharbeit und Konsistenz

### 8.2 Architectural Role
Die Ontologie dient als:
- Referenzmodell für Klassifikation
- Normalisierungsbasis
- Validierungsrahmen
- Treiber für Review-/Nacharbeitsprozesse
- Grundlage für spätere Runtime-Enforcement-Mechanismen

### 8.3 Runtime Expectations
Die Architektur sieht vor:
- Soft Validation als aktueller Betriebsmodus
- Legacy-/Alias-Mapping für Bestandsdaten
- perspektivisch stärkere Runtime-Enforcement-Logik
- dokumentierte Ontologie-Versionen und Migrationsverträglichkeit

### 8.4 Design Implication
Architekturänderungen an Kategorien, Item Types, Wertemengen, Regel-Engine oder Mapping-Strategie sind **architekturwirksam** und müssen im ARD und ggf. per ADR dokumentiert werden.

## 9. Security Architecture

### 9.1 Principles
- No secrets in repo
- No secrets in logs
- API key handling is explicit
- Secret scanning is mandatory
- Run Registry data must be redacted where applicable

### 9.2 Current Security Baseline
- `.env` is not tracked
- `.env.example` exists
- secret scanner exists
- run registry redacts sensitive values
- public exposure is separated from API-key semantics

### 9.3 Security-Relevant Changes
Änderungen an Auth, Secrets, Logging, Exposure, Proxying, Domain Routing, DNS, Run Registry Redaction oder Upload-/Ingestion-Schutzmechanismen sind ARD-pflichtig.

## 10. Operational Architecture

### 10.1 Run Registry
Das Projekt nutzt Run Registry und Event-Tracking zur Nachvollziehbarkeit von:
- Ingestion
- Recovery
- Handoff
- Reports
- Tooling-Runs

### 10.2 Handoff and Snapshot Discipline
Handoffs und Snapshots sind integraler Bestandteil der Projektkontinuität.
Sie sind kein optionales Add-on, sondern Teil der Betriebs- und Übergabearchitektur.

### 10.3 Tooling Class
Zum operativen System gehören auch:
- Secret Scan
- Repo Metrics
- Handoff Tools
- Reports
- Test-/Smoke-Skripte
- Recovery- und Ingest-Werkzeuge

## 11. Architectural Decisions

Die Architekturentscheidungen dieses Projekts werden in zwei Ebenen dokumentiert:
1. **Dieses ARD** für die kanonische Zielarchitektur
2. **ADRs unter `docs/adr/`** für einzelne Designentscheidungen und Trade-offs

Mindestens folgende Entscheidungen sind dokumentationspflichtig:
- FastAPI + Flask co-hosting
- SQLite + filesystem split
- Ontology runtime model
- ngrok / Cloudflare / domain exposure
- run registry and handoff strategy
- ingestion idempotence and recovery model

## 12. Non-Functional Requirements

### 12.1 Robustness
Das System muss gegenüber partiellen Fehlern, Restart-Situationen und operativen Drift-Szenarien robust sein.

### 12.2 Recoverability
Fehlerhafte oder unvollständige Zustände müssen erkennbar und kontrolliert korrigierbar sein.

### 12.3 Traceability
Wesentliche Läufe, Änderungen und Betriebszustände müssen nachvollziehbar sein.

### 12.4 Testability
Alle kritischen Pfade müssen testbar sein; Regressionen sind zu verhindern.

### 12.5 Maintainability
Code, Tooling und Dokumentation müssen so strukturiert sein, dass das Projekt über längere Zeit und über Chat-Grenzen hinaus weiterentwickelbar bleibt.

### 12.6 Documentation Integrity
Architekturwissen darf nicht nur in Chats oder implizitem Entwicklerwissen vorliegen.

## 13. Validation and Maintenance Rules

### 13.1 Validation Triggers
Das ARD ist zu validieren und ggf. zu aktualisieren bei:
- Architekturänderungen
- Infrastrukturänderungen
- Release-Vorbereitung
- Security-relevanten Änderungen
- Persistenz-/Schemaänderungen
- API-Contract-Änderungen
- Änderungen an Ontologie, Ingestion, Recovery oder Exposure-Modell

### 13.2 Completion Rule
Eine architekturwirksame Änderung ist erst vollständig, wenn:
- Code angepasst ist
- Tests angepasst sind
- ARD und ggf. ADR/Release-Dokumente angepasst sind

### 13.3 Ownership
Das ARD ist ein aktives Steuerungsdokument und kein Archiv.
