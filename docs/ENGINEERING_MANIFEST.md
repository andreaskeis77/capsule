# Engineering Manifest
## Capsule Studio / Capsule Wardrobe Project

Stand: 2026-03-26

## 1. Purpose

Dieses Manifest ist der verbindliche Arbeitsvertrag des Projekts.
Es konkretisiert die allgemeinen Engineering-Prinzipien für Capsule Studio und macht sie für dieses Repository, seine Architektur, seine Tooling-Landschaft und seinen Release-Prozess verbindlich.

Das Manifest steuert:
- wie Änderungen geplant werden
- wie sie getestet und dokumentiert werden
- welche Nachweise vor Commit und Release erforderlich sind
- wie ARD, Releases, Handoffs und Architekturentscheidungen gepflegt werden

## 2. Source of Truth
- Das Git-Repository ist die technische Source of Truth.
- Architekturwissen darf nicht exklusiv in Chats liegen.
- Dokumente in `docs/` sind verbindliche Projektartefakte.
- Das ARD ist das kanonische Architekturreferenzdokument.
- Release-Dokumente sind die kanonische Änderungs- und Scope-Referenz.

## 3. Engineering Principles
1. Correctness vor Cleverness
2. Kleine, klar abgegrenzte Tranchen statt unkontrollierter Umbauten
3. Reproduzierbarkeit vor implizitem Wissen
4. Observability ist Pflicht
5. Security und Secret Hygiene by default
6. Fail-Fast oder geplante Graceful Degradation
7. Zero-Trust gegenüber KI-Output
8. Architekturentscheidungen müssen explizit dokumentiert werden
9. Doku ist Teil des Deliverables
10. Handoff-Fähigkeit ist Teil der Projektqualität

## 4. Tranche Model

Jede Änderung wird als **Tranche** geplant und umgesetzt.

### 4.1 Jede Tranche muss dokumentieren
- Ziel
- Scope
- betroffene Komponenten/Dateien
- Risiken
- Teststrategie
- Dokumentationsauswirkung
- Ziel-Release

### 4.2 Jede Tranche muss klein genug sein, dass sie
- nachvollziehbar reviewbar ist
- testbar ist
- bei Problemen eingrenzbar ist
- ohne unnötigen Seiteneffekt zurückgenommen werden kann

### 4.3 Große Sammelrefactorings ohne klaren Zwischenzustand sind unzulässig.

## 5. Testing and Evidence Rules

### 5.1 Grundregel
Änderungen gelten erst als belastbar, wenn die relevanten Tests und Evidence-Schritte erfolgreich waren.

### 5.2 Pflichtnachweise
Je nach Scope gehören dazu mindestens:
- `pytest`
- Secret Scan
- relevante Tool-/Smoke-/API-Checks
- Dokumentationsabgleich
- ggf. Handoff-/Snapshot-Update

### 5.3 Regression Rule
Jeder Bugfix muss mindestens einen Regressionstest mitbringen.

### 5.4 Critical Paths
Für kritische Pfade gelten erhöhte Anforderungen:
- API Contracts
- Persistenz / Schema
- Ingestion
- Recovery
- Auth / Secret Handling
- Run Registry / Handoff

## 6. Documentation Rules

### 6.1 Dokumentationspflicht
Wenn geändert werden:
- Architektur
- Infrastruktur
- Betriebsabläufe
- Auth/Security
- Persistenzmodell
- API Contracts
- Ontologie / Runtime-Enforcement
- Release Scope
- Tooling / operative Nachweise

dann müssen die entsprechenden Dokumente aktualisiert werden.

### 6.2 Pflichtdokumente
- `docs/ARCHITECTURE_REQUIREMENTS_DOSSIER.md`
- `docs/ENGINEERING_MANIFEST.md`
- `docs/RELEASE_MANAGEMENT.md`
- `docs/RELEASE_NOTES.md`
- relevante ADRs
- relevante Runbooks / Handoffs / Snapshot-Referenzen

### 6.3 Unvollständige Änderungen
Eine Änderung ohne konsistente Aktualisierung von Code, Tests und Referenzdokumenten gilt als unvollständig.

## 7. ARD Governance

### 7.1 Verpflichtende Nutzung
Das ARD ist verpflichtend zu nutzen:
- vor Architekturentscheidungen
- bei architekturwirksamen Änderungen
- bei Release-Vorbereitung
- bei Infrastrukturänderungen

### 7.2 Pflicht zur Validierung
Das ARD ist regelmäßig zu validieren und zu erweitern.

### 7.3 ARD Trigger
Das ARD ist zu aktualisieren bei Änderungen an:
- Laufzeitarchitektur
- Infrastruktur
- DNS / Domains / Tunnel / Proxying
- Persistenz / Dateisystem-Logik
- API/Contract
- Ontologie / Item Type / Mapping / Validation
- Ingestion / Recovery / Handoff / Run Registry

## 8. Release Governance

### 8.1 Releases sind Pflichtartefakte
Releases werden nicht implizit angenommen, sondern explizit definiert und dokumentiert.

### 8.2 Jede Änderung gehört zu einem Zielrelease
Jede Tranche ist einem Zielrelease zuzuordnen.

### 8.3 Release 1.0
Der aktuelle dokumentierte Funktionsumfang wird als **Release 1.0.0 Baseline** definiert.

### 8.4 Release-Dokumente
Release-Scope, Change-Umfang, Testnachweise, bekannte Einschränkungen und interne Tooling-Artefakte werden in den Release-Dokumenten gepflegt.

## 9. Tooling and Operational Knowledge Retention

### 9.1 Operatives Wissen darf nicht verloren gehen
Interne Werkzeuge und Nachweislogiken müssen dokumentiert werden, auch wenn sie nicht für Endnutzer bestimmt sind.

### 9.2 Dazu gehören insbesondere
- Test-Skripte
- Secret Scan
- Handoff-Werkzeuge
- Run Reports
- Repo Metrics
- Recovery-Tools
- Ingest-Tools
- Start-/Batch-/Ops-Skripte

## 10. Handoff and Snapshot Discipline

### 10.1 Handoffs
Handoffs sind verpflichtend bei:
- Session-Abbruch an relevanten Stellen
- Übergabe in neuen Chat
- Release-/Meilensteinpunkten
- Architektur-/Betriebsänderungen

### 10.2 Snapshot Discipline
Snapshots/Handoff-Artefakte sind Teil der Engineering-Kontinuität.
Sie ersetzen jedoch nicht die kanonische Dokumentation in `docs/`.

## 11. Definition of Done
Eine Tranche gilt als abgeschlossen, wenn:
- der Scope umgesetzt ist
- die relevanten Tests grün sind
- keine offenen bekannten Brüche im Scope verbleiben
- Dokumentation aktualisiert ist
- Zielrelease zugeordnet ist
- bei Bedarf Handoff/Snapshot erstellt wurde

## 12. Project-Specific Working Rule

Für Capsule Studio gilt zusätzlich ausdrücklich:

> Architektur, Betriebsmodell, Security-relevante Änderungen, Infrastrukturänderungen, API-Contract-Änderungen und Release-relevante Änderungen sind erst dann vollständig, wenn Code, Tests und die zugehörigen Referenzdokumente konsistent aktualisiert wurden.

> Das ARD ist verpflichtend zu nutzen, regelmäßig zu validieren und bei jeder architekturwirksamen Änderung zu erweitern.
