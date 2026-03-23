# ENGINEERING_MANIFEST_CAPSULE_ADDENDUM

## 1. Zweck

Dieses Dokument ergänzt `docs/ENGINEERING_MANIFEST_v2.0.md` projektbezogen für Capsule.  
Das Basis-Manifest bleibt gültig; dieses Addendum präzisiert die Default-Regeln für dieses konkrete System.

## 2. Projektbezogene Leitplanken

### 2.1 Karen ist Nutzerin, nicht Host

Der Zielzustand ist ausdrücklich:

- **kein lokaler Capsule-Server auf Karens Laptop**
- zentraler Betrieb auf Windows-VPS
- Nutzung über Custom GPT und/oder Website

Abweichungen davon sind nur Übergangszustände.

### 2.2 Ein kanonisches Backend

Capsule hat genau ein kanonisches Backend für fachliche Wahrheit.

Daraus folgen:

- keine divergierenden Business-Regeln zwischen Website und GPT-Pfad
- keine zweite Schattenlogik im Client
- gemeinsame Daten-, API- und Run-Registry-Grundlage

### 2.3 OpenAI Keys nur serverseitig

Wenn Capsule die OpenAI API nutzt, dann nur serverseitig.

Verboten sind:

- Browser-seitige dauerhafte API-Key-Nutzung
- API-Keys in Chat-Handoffs
- API-Keys in Doku oder Logs

### 2.4 Windows-Parität bis zum stabilen VPS-Zielzustand

Da Entwicklung und kurzfristiger Zielbetrieb auf Windows laufen, gilt bis auf Weiteres:

- Windows-kompatible Pfade und Startbefehle priorisieren
- lokale und VPS-nahe Startpfade möglichst ähnlich halten
- keine unnötige Linux-only-Komplexität einführen, solange der reale Zielbetrieb Windows ist

### 2.5 Docs sind Meilensteinpflicht

Nach jedem relevanten Meilenstein müssen mindestens geprüft und bei Bedarf aktualisiert werden:

- `docs/PROJECT_STATE.md`
- `docs/RUNBOOK.md`
- `docs/HANDOFF_MANIFEST.md`
- `docs/CHAT_HANDOFF_TEMPLATE.md`
- relevante ADRs

### 2.6 Generierte Ops-Artefakte bleiben aus Git draußen

Lokale Betriebs-/Inventur-/Quality-Gate-Artefakte sind wertvoll, aber nicht standardmäßig Teil des Repo-Kerns.

Sie bleiben lokal bzw. ignoriert, insbesondere:

- `docs/_ops/`
- `docs/_archive/`
- `docs/_notebooklm/`

## 3. Projektbezogene Prioritätenreihenfolge

Bei Zielkonflikten gilt für Capsule standardmäßig:

1. Datenintegrität
2. Konsistenz zwischen GPT, Website und Backend
3. reproduzierbarer Betrieb
4. Handoff-/Weiterarbeitsfähigkeit
5. Bedienkomfort
6. spätere Optimierungen

## 4. Aktuelle nächste Schwerpunktfelder

Die nächsten priorisierten Arbeitsfelder sind:

1. Projektdokumentation / Handoff / Manifest auf A–R-Stand konsolidieren
2. Deployment des aktuellen Stands auf den Windows-VPS
3. stabiler öffentlicher Zugriff ohne Karen-Laptop als Host
4. Entscheidung und Umsetzung des endgültigen Betriebsmodells:
   - GPT-only
   - Website-only
   - Hybrid
