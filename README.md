# Capsule

Capsule ist ein lokal entwickeltes Wardrobe-, Ontology- und Ingest-System mit klar getrennten Schichten für API, Dashboard, Ontology Runtime, Persistenz, Quality Gates und operatives Tooling.

Das Projekt ist kein reines Demo-Repository, sondern ein strukturiertes Engineering-System mit:
- produktnaher Runtime,
- dokumentierter Architektur,
- operativem Tooling,
- Handoff-/Snapshot-Fähigkeit,
- Security- und Quality-Gates,
- reproduzierbaren Betriebs- und Recovery-Pfaden.

---

## Aktueller Stand

Capsule läuft aktuell in einem stabilisierten Betriebsmodell mit:

- lokaler API auf dem VPS,
- öffentlicher Web-Erreichbarkeit über Cloudflare Tunnel,
- separater öffentlicher API-Subdomain für Custom-GPT-Actions,
- Admin-Zugang zum VPS über Tailscale statt öffentliches RDP,
- aktiver Windows-Firewall,
- dokumentierten Runbooks für VPS, Access und Cloudflare.

Der aktuelle stabile Produktstand ist als Baseline-Kandidat für `v0.1.0` zu verstehen.

---

## Kanonische Kern-Dokumente

Für den Einstieg und den aktuellen Betriebsstand sind diese Dokumente maßgeblich:

1. `docs/ARCHITECTURE_REQUIREMENTS_DOSSIER.md`
2. `docs/ENGINEERING_MANIFEST.md`
3. `docs/RELEASE_MANAGEMENT.md`
4. `docs/RELEASE_NOTES.md`
5. `docs/RUNBOOK.md`

Ergänzende und unterstützende Dokumentationsbereiche:

- `docs/adr/`
- `docs/history/`
- `docs/gpt/`

Weitere direkt relevante Betriebsdokumente:

- `docs/RUNBOOK_VPS_WINDOWS_HARDENING.md`
- `docs/RUNBOOK_VPS_ACCESS_AND_CLOUDFLARE.md`
- `docs/PROJECT_STATE.md`
- `docs/_handoff/HANDOFF_Capsule_VPS_RDP_Karen_2026-04-06_FINAL.md`

---

## Kernfunktionen

Capsule deckt aktuell insbesondere folgende Bereiche ab:

- Verwaltung eines strukturierten Wardrobe-Bestands pro Nutzer
- API-basierter Zugriff auf Bestandsdaten
- Dashboard-/Webzugriff
- Ontology-/Taxonomy-nahe Strukturierung von Kategorien und Merkmalen
- Ingest- und Review-Workflows
- Bilder-/Metadaten-Verknüpfung
- operative Dokumentation, Handoffs und Recovery-Wissen im Repository

---

## Betriebsmodell

### Web
Die Weboberfläche ist öffentlich über Cloudflare Tunnel erreichbar:

- `https://capsule-studio.de`

### Öffentliche API für GPT / Integrationen
Die öffentliche API für Custom-GPT-Actions läuft über eine eigene API-Subdomain:

- `https://api.capsule-studio.de`

Beispiel-Endpunkt:

- `GET /api/v2/items?user=karen`

Authentifizierung erfolgt über:

- Header: `X-API-Key`
- Wert: `WARDROBE_API_KEY` aus der lokalen `.env`

### VPS-Admin-Zugang
Der administrative Zugriff auf den VPS erfolgt nicht mehr über öffentliches RDP, sondern über:

- Tailscale
- RDP gegen die Tailscale-IP des VPS

Öffentliches RDP auf Port `3389` ist geschlossen.

---

## Repository-Struktur

- `src/` – Anwendungscode
- `templates/` – HTML-Templates für Dashboard/Admin/Detailansichten
- `tests/` – Regressionen und Vertrags-Tests
- `tools/` – operative Helfer, Handoff, Reports, Recovery, Security, Gates
- `ontology/` – Ontologie, Mappings und fachliche Struktur
- `docs/` – Architektur-, Betriebs-, Handoff- und Release-Dokumentation
- `deploy/` – Deploy-/VPS-spezifische Skripte und Konfigurationen

---

## Lokale Entwicklung

### Umgebung aktivieren

```powershell
.\.venv\Scripts\Activate.ps1
```

### Quality Gates

```powershell
python .\tools\task_runner.py quality-gates
```

Alternativ, falls vorhanden:

```powershell
.\capsule.cmd quality-gates
```

---

## Security und Integrationen

### API-Schlüssel
Die Wardrobe-API nutzt einen projektspezifischen API-Key:

- `.env` → `WARDROBE_API_KEY=...`

Dieser Key ist relevant für:
- öffentliche API-Aufrufe,
- Custom-GPT-Actions,
- Integrations- und Smoke-Tests gegen die geschützte API.

### Nicht verwechseln
Der projektspezifische `WARDROBE_API_KEY` ist nicht dasselbe wie ein `OPENAI_API_KEY`.

Für Custom-GPT-Actions gegen Capsule muss der Header

- `X-API-Key`

mit dem Wert aus

- `WARDROBE_API_KEY`

gesetzt werden.

---

## Custom GPT / Action-Betrieb

Der stabile öffentliche Host für die GPT-Action ist:

- `https://api.capsule-studio.de`

Die Action soll nicht dauerhaft auf eine ngrok-Domain zeigen, wenn die produktive API über Cloudflare bereitsteht.

Für GPT-Actions gilt im stabilen Zielbild:

- Server-URL: `https://api.capsule-studio.de`
- Authentifizierung: API-Schlüssel
- Custom Header: `X-API-Key`

---

## Operative Hinweise

### VPS-Zielbild
- Windows-Firewall aktiv
- öffentliches RDP deaktiviert
- Admin-Zugang über Tailscale
- Cloudflare Tunnel als Windows-Service
- Web über `capsule-studio.de`
- API über `api.capsule-studio.de`

### Recovery-/Änderungsregel
Infrastruktur-, Zugangs- oder Tunneländerungen dürfen nicht nur ad hoc im Live-System erfolgen, sondern müssen im selben Arbeitsblock dokumentiert werden in:

- Runbook
- Handoff
- ggf. `PROJECT_STATE`

---

## Qualitätsanspruch

Änderungen gelten erst als belastbar, wenn sie technisch und operativ überprüfbar sind.

Dazu gehören je nach Scope insbesondere:

- lokale API-Funktion
- Integrations- oder Smoke-Tests
- Quality Gates
- Dokumentationsnachzug
- klarer Handoff-/Recovery-Stand

---

## Nächster Baseline-Schritt

Empfohlener nächster formaler Schritt:

- README / PROJECT_STATE / Runbooks auf denselben Ist-Zustand ziehen
- GitHub Release als erste stabile Produkt-Baseline setzen
- vorgeschlagener Tag: `v0.1.0`

---
