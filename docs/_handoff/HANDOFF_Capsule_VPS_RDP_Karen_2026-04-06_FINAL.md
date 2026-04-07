# HANDOFF – Capsule VPS Stabilisierung abgeschlossen / Tailscale / Cloudflare / Custom GPT API

**Datum:** 2026-04-07  
**Repo:** `https://github.com/andreaskeis77/capsule`  
**DEV-LAPTOP Repo:** `C:\CapsuleWardrobeRAG`  
**VPS Repo:** `C:\CapsuleWardrobeRAG`  
**Ausgangsbasis:** Vorheriger Handoff `HANDOFF_Capsule_VPS_RDP_Karen_2026-04-06.md`

---

## 1. Kurzfazit

Die kritischen Betriebsprobleme wurden behoben.

### Finaler Soll-Zustand jetzt
- **Öffentliches RDP auf `84.247.164.122:3389` ist geschlossen**
- **Admin-Zugang erfolgt jetzt per Tailscale-RDP**
- **Tailscale auf VPS und DEV-LAPTOP funktioniert**
- **Tailscale auf dem VPS läuft mit `Run unattended`**
- **Windows Defender Firewall ist wieder aktiviert**
- **temporäre Windows-RDP-Sonderregeln wurden entfernt**
- **VNC ist wieder deaktiviert**
- **Cloudflare Tunnel ist wieder als Windows-Service aktiv**
- **`capsule-studio.de` funktioniert wieder**
- **eigene API-Subdomain `api.capsule-studio.de` funktioniert**
- **Custom GPT Action funktioniert wieder gegen `api.capsule-studio.de`**
- **Karen-Bestand kann wieder aus dem Custom GPT abgerufen werden**

---

## 2. Wichtigste Endergebnisse

### A. Remote-Admin-Zugang
Der frühere Zustand mit öffentlichem RDP und IP-Whitelist war zu fragil.  
Er wurde ersetzt durch:

- **Tailscale-RDP**
- Ziel-IP aktuell: `100.71.205.5`
- Login erfolgreich mit lokalem Windows-Konto, z. B.:
  - `\.\srv-ops-admin`

### B. Firewall / RDP
Der unsichere Zwischenzustand wurde vollständig zurückgebaut:

- Windows Defender Firewall wieder **ON**
- Contabo-RDP-Testöffnung wieder **entfernt**
- öffentlicher Port `3389` wieder **geschlossen**
- externe Prüfung:
  - `Test-NetConnection 84.247.164.122 -Port 3389` → **False**
- Tailscale-Zugang bleibt funktionsfähig
- Reboot-Test erfolgreich

### C. VNC
- VNC war Recovery-Weg
- nach erfolgreicher Stabilisierung wieder **deaktiviert**

### D. Cloudflare Tunnel
Ursache des Cloudflare-Problems:
- auf dem VPS lief **kein** `cloudflared`
- kein Connector vorhanden
- Tunnel im Dashboard stand auf **DOWN**
- dadurch kam Cloudflare **1033**

Fix:
- `cloudflared` auf dem VPS installiert
- als **Windows-Service** registriert
- Dienststatus danach:
  - `cloudflared` = **Running**
  - `StartType` = **Automatic**

Ergebnis:
- Tunnel wieder online
- `capsule-studio.de` wieder erreichbar

### E. Public API für Custom GPT
Wichtiges Problem:
- `capsule-studio.de` ist die Hauptseite und kann mit Cloudflare Access / Login-Schutz belegt sein
- direkter API-Aufruf über diese Domain kann auf Access/Login landen
- daher wurde eine eigene API-Subdomain eingerichtet

Neue Route:
- **`api.capsule-studio.de`**
- Tunnel-Route auf:
  - `http://localhost:8000`

Browser-Test ohne Header:
- `https://api.capsule-studio.de/api/v2/items?user=karen`
- Ergebnis: **Unauthorized JSON**
- das ist korrekt und gewünscht, weil die Route funktioniert und nur der API-Key fehlt

### F. Custom GPT
Entscheidender Fix:
- Action war vorher noch auf **ngrok** konfiguriert
- außerdem gab es Verwirrung zwischen:
  - `OPENAI_API_KEY`
  - `WARDROBE_API_KEY`

Korrekt ist:
- im Custom GPT Action-Dialog muss **der Wert von `WARDROBE_API_KEY`** stehen
- **nicht** der `OPENAI_API_KEY`

Nach Korrektur:
- Action zeigt auf `https://api.capsule-studio.de`
- Header bleibt:
  - `X-API-Key`
- GPT konnte danach erfolgreich Bestandsdaten abrufen

---

## 3. Finales Betriebsmodell

### 3.1 Admin-Zugang VPS
Primärer Weg:
- **Tailscale-RDP**

Aktuelle Zieladresse:
- `100.71.205.5`

Benutzer:
- lokales Windows-Konto auf dem VPS, z. B.:
  - `\.\srv-ops-admin`

Nicht mehr vorgesehen:
- öffentliches RDP auf `84.247.164.122:3389`

### 3.2 Public Web
Öffentliche Website:
- `https://capsule-studio.de`

Betrieb:
- über **Cloudflare Tunnel**
- `cloudflared` läuft als Windows-Service auf dem VPS

### 3.3 Public API für GPT / externe Nutzung
Öffentliche API-Basis:
- `https://api.capsule-studio.de`

Backend-Ziel:
- `http://localhost:8000`

Auth:
- Header `X-API-Key`
- Wert = `WARDROBE_API_KEY` aus `.env`

---

## 4. Wichtige Zustände / Prüfungen

### Erfolgreich bestätigt
- `ping 100.71.205.5` → ok
- `mstsc /v:100.71.205.5` → ok
- Reboot des VPS → ok
- Tailscale danach weiter ok
- `Test-NetConnection 84.247.164.122 -Port 3389` → **False**
- `https://capsule-studio.de` → ok
- `https://api.capsule-studio.de/api/v2/items?user=karen` ohne Header → **Unauthorized JSON**
- `Invoke-WebRequest http://127.0.0.1:8000/api/v2/items?user=karen` mit korrektem `X-API-Key` → **200**
- Custom GPT Abruf von Karens Röcken → erfolgreich

### Entfernt / zurückgebaut
- breite Contabo-RDP-Regel
- temporäre Windows-RDP-Allow-Regeln (`TEMP-RDP-*`)
- VNC-Notbetrieb
- Abhängigkeit des Custom GPT von ngrok

---

## 5. Relevante Services / Komponenten

### Auf dem VPS aktiv
- Capsule API
- ngrok (historisch weiter vorhanden; für den GPT jetzt nicht mehr erforderlich)
- `cloudflared` als Windows-Service
- Tailscale

### Wichtig
Für den **Custom GPT** ist **ngrok jetzt nicht mehr erforderlich**, weil die Action auf `api.capsule-studio.de` umgestellt wurde.

Das heißt:
- GPT nutzt jetzt **Cloudflare / API-Subdomain**
- nicht mehr die frühere ngrok-URL

Ob ngrok sonst noch für andere Tests oder Altpfade gebraucht wird, ist separat zu entscheiden.

---

## 6. Custom GPT – finaler technischer Stand

### Authentication im GPT
- Typ: **API-Schlüssel**
- Untertyp: **Individuell**
- Header-Name: `X-API-Key`
- API-Schlüsselwert: **Wert von `WARDROBE_API_KEY` aus `.env`**

### Nicht verwenden
- `OPENAI_API_KEY`

### Server in OpenAPI
- `https://api.capsule-studio.de`

### Funktion bestätigt
Beispiel erfolgreicher Nutzer-Use-Case:
- „Ich bin Karen. Liste meine Röcke auf die ich habe.“

Antwort funktionierte wieder.

---

## 7. Lessons Learned

1. **Öffentliches RDP mit fester Heim-IP ist betrieblich zu fragil.**
2. **Tailscale ist für Admin-Zugang hier die robustere Lösung.**
3. **Cloudflare 1033 war kein App-Fehler, sondern fehlender `cloudflared`-Connector.**
4. **Website und API sollten getrennt gedacht werden.**
5. **Für GPT-Actions muss die öffentliche API-URL sauber von Access-/Login-Seiten getrennt sein.**
6. **Im GPT-Dialog muss der Key der Ziel-API hinterlegt sein, nicht ein OpenAI-Key.**
7. **Lokale Direkt-Tests (`127.0.0.1`) und öffentliche Direkt-Tests (`api.capsule-studio.de`) sind der schnellste Weg zur Fehlerisolation.**

---

## 8. Empfohlene nächste Aufräumthemen

### A. Repo-/Runbook-Dokumentation aktualisieren
Empfohlen:
- `docs/RUNBOOK_VPS_WINDOWS_HARDENING.md`
- neuer Abschluss-Handoff unter `docs/_handoff/`
- Doku zur GPT-API-Umstellung von ngrok auf `api.capsule-studio.de`

### B. ngrok-Bedarf final prüfen
Frage:
- wird ngrok außerhalb des GPT noch wirklich benötigt?
- falls nein: später sauber stilllegen

### C. Cloudflare sauber dokumentieren
Dokumentieren:
- Tunnelname: `Contabo-Wardrobe`
- `cloudflared` als Windows-Service
- Route:
  - `capsule-studio.de` → Web-Ziel laut Cloudflare-Tunnel-Konfiguration
  - `api.capsule-studio.de` → `http://localhost:8000`

### D. Optional
Später prüfen:
- ob Web- und API-Routen langfristig sauber getrennt bleiben sollen
- ob zusätzliche Härtung / Monitoring für `cloudflared` und API sinnvoll ist

---

## 9. Kurzfassung für den nächsten Chat

```text
Wir arbeiten im Capsule-VPS-Kontext weiter.

Aktueller finaler Zustand:
- öffentliches RDP ist geschlossen
- Admin-Zugang läuft über Tailscale-RDP auf 100.71.205.5
- Windows-Firewall ist aktiv
- VNC ist wieder deaktiviert
- Cloudflare Tunnel läuft als Windows-Service (cloudflared Running Automatic)
- capsule-studio.de funktioniert wieder
- api.capsule-studio.de ist die öffentliche API-Subdomain für den Custom GPT
- der Custom GPT nutzt X-API-Key mit dem Wert von WARDROBE_API_KEY
- OPENAI_API_KEY gehört NICHT in den GPT-Action-Dialog
```
