# ADR-0019 – Project Documentation, Handoff, and Deployment Target State

## Status
Accepted

## Kontext

Das Repo wurde technisch stark gehärtet, aber zentrale Projektfragen mussten explizit dokumentiert werden:

- was ist der aktuelle fachliche und technische Stand?
- wie sieht der echte Zielbetrieb aus?
- wie sollen Handoffs zwischen Chats / Arbeitsblöcken erfolgen?
- wie wird das projektagnostische Engineering Manifest auf Capsule konkret angewendet?

Zusätzlich ist für Capsule eine wichtige Produkt- und Betriebsentscheidung relevant:
Karen soll langfristig keinen lokalen Server mehr auf ihrem Laptop betreiben.

## Entscheidung

Es werden folgende Dokumente als kanonische Projektsteuerungsdokumente etabliert bzw. aktualisiert:

- `docs/PROJECT_STATE.md`
- `docs/RUNBOOK.md`
- `docs/HANDOFF_MANIFEST.md`
- `docs/CHAT_HANDOFF_TEMPLATE.md`
- `docs/ENGINEERING_MANIFEST_CAPSULE_ADDENDUM.md`
- `docs/DEPLOYMENT_TARGET_STATE.md`
- `docs/VPS_DEPLOYMENT_RUNBOOK.md`
- `docs/DOCUMENTATION_ROADMAP.md`

Zusätzlich wird der Zielzustand explizit festgelegt:

- zentraler Betrieb auf Windows-VPS
- ngrok kurzfristig auf dem VPS
- Karen als Nutzerin, nicht als lokale Host-Instanz
- ein kanonisches Backend für Custom GPT und Website
- OpenAI-Integration für Website-Use-Cases serverseitig

## Konsequenzen

### Positiv
- bessere Übergabefähigkeit
- klarer Betriebsmodus
- weniger Architekturdrift
- bessere Grundlage für echten VPS-Rollout

### Negativ / Aufwand
- Doku muss künftig aktiv gepflegt werden
- VPS-Deployment und Zielbetrieb müssen nach Realumsetzung erneut dokumentiert und präzisiert werden

## Alternativen

### A – nur bestehende Doku minimal pflegen
Verworfen, weil Projektstand und Zielarchitektur dann weiter implizit bleiben.

### B – Engineering Manifest komplett überschreiben
Verworfen. Besser ist ein projektbezogenes Addendum zum allgemeinen Manifest.

### C – Karen weiter lokal hosten lassen
Verworfen als Zielzustand, weil der Betriebsaufwand und die Fragilität zu hoch sind.
