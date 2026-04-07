# RUNBOOK – Capsule VPS Access, Cloudflare Tunnel, API Subdomain, Custom GPT

**Status:** gültiger Zielzustand nach Reparatur am 2026-04-07  
**Repo-Pfad:** `C:\CapsuleWardrobeRAG`

---

## 1. Zweck

Dieses Runbook beschreibt den öffentlichen Zugangsweg für Web und API sowie die Kopplung des Custom GPT an die Wardrobe-API.

---

## 2. Architekturüberblick

### Web
- öffentliche Domain: `https://capsule-studio.de`
- Veröffentlichung über **Cloudflare Tunnel**
- `cloudflared` läuft als Windows-Service auf dem VPS

### API für GPT / externe Aufrufe
- öffentliche API-Domain: `https://api.capsule-studio.de`
- Tunnel-Ziel: `http://localhost:8000`
- API-Auth: Header `X-API-Key`

### Admin-Zugang
- **nicht** über Cloudflare
- **nicht** über öffentliches RDP
- ausschließlich über **Tailscale-RDP**

---

## 3. Cloudflare Tunnel

### Tunnel
- Name: `Contabo-Wardrobe`

### Dienst auf dem VPS
```powershell
Get-Service cloudflared | Format-Table Name, Status, StartType -Auto
```

Soll:
- `cloudflared`
- `Running`
- `Automatic`

### Störungssymptom 1033
Wenn Cloudflare **1033** liefert, zuerst prüfen:
- läuft `cloudflared` überhaupt?
- ist der Dienst aktiv?
- ist der Tunnel im Dashboard `DOWN` oder ohne Connector?

Typischer Reparaturweg:
1. Connector im Cloudflare-Dashboard prüfen
2. `cloudflared` auf dem VPS installieren, falls fehlend
3. Connector-/Service-Installationsbefehl auf dem VPS als Admin ausführen
4. Dashboard prüfen, ob der Tunnel wieder `HEALTHY` / verbunden ist

---

## 4. Published Routes

### API-Route für GPT
Eintrag im Tunnel:
- **Subdomain:** `api`
- **Domain:** `capsule-studio.de`
- **Path:** leer
- **Service Type:** `HTTP`
- **URL:** `localhost:8000`

Ergebnis:
- `https://api.capsule-studio.de`

### Erwarteter Browser-Test ohne Header
```text
https://api.capsule-studio.de/api/v2/items?user=karen
```

Soll:
- **Unauthorized JSON**
- **keine** Cloudflare-Access-Loginseite

Das bedeutet:
- Tunnel-Route funktioniert
- API ist öffentlich erreichbar
- nur der Header fehlt

---

## 5. Cloudflare Access

### Wichtiges Prinzip
Die API-Subdomain für den Custom GPT darf **nicht** auf eine interaktive Cloudflare-Access-Loginseite umgeleitet werden.

### Praxisregel
- `capsule-studio.de` kann separat mit Access-/Login-Mechanismen arbeiten
- `api.capsule-studio.de` muss für den GPT direkt auf die API führen

Wenn `api.capsule-studio.de` HTML für **Cloudflare Access Sign in** zurückgibt, ist die API-Route falsch abgesichert.

---

## 6. Lokale API-Prüfung

### Echte Funktionsprobe lokal auf dem VPS
```powershell
$key = "<WARDROBE_API_KEY>"

Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/v2/items?user=karen" `
  -Headers @{ "X-API-Key" = $key } `
  -Method GET `
  -UseBasicParsing
```

Soll:
- `StatusCode = 200`

### Öffentliche API-Prüfung mit Header
```powershell
$key = "<WARDROBE_API_KEY>"

Invoke-WebRequest `
  -Uri "https://api.capsule-studio.de/api/v2/items?user=karen" `
  -Headers @{ "X-API-Key" = $key } `
  -Method GET `
  -UseBasicParsing
```

Soll:
- `StatusCode = 200`

Wenn lokal `200`, öffentlich aber nicht, liegt das Problem im öffentlichen Pfad oder in Cloudflare.

---

## 7. Custom GPT / Action

### Authentifizierung im GPT
Im GPT-Editor:
- Typ: **API-Schlüssel**
- Untertyp: **Individuell**
- Name der Kopfzeile: `X-API-Key`
- API-Schlüsselwert: **Wert von `WARDROBE_API_KEY` aus `.env`**

### Nicht verwenden
- `OPENAI_API_KEY`

### Server in OpenAPI
```yaml
servers:
  - url: https://api.capsule-studio.de
```

### Minimaler Merksatz
Der GPT muss sich gegen **deine Wardrobe-API** authentifizieren.  
Darum gehört in den Action-Dialog **der selbst definierte Wardrobe-Key** und **nicht** ein OpenAI-Key.

---

## 8. OpenAPI-Schema – Zielzustand

Das im GPT verwendete Schema soll auf `https://api.capsule-studio.de` zeigen und den Header `X-API-Key` verwenden.

Die konkreten Endpunkte sind:
- `GET /api/v2/items`
- `POST /api/v2/items`
- `GET /api/v2/items/{item_id}`
- `PATCH /api/v2/items/{item_id}`
- `DELETE /api/v2/items/{item_id}`

Health-/Diagnose-Endpunkte sind für den GPT nicht erforderlich und sollten nur dann im Schema stehen, wenn sie im öffentlichen Pfad tatsächlich stabil funktionieren.

---

## 9. GPT-Fehlerbilder und typische Ursachen

### Fall A – HTML statt JSON
Symptom:
- Antwort enthält Cloudflare-Access-Loginseite

Ursache:
- API-Route läuft über Access/Login-Schutz

Fix:
- API auf eigene Subdomain legen
- Access-Regel für API-Pfad/Subdomain prüfen

### Fall B – `401 Unauthorized`
Symptom:
- JSON-Fehler der API

Ursache:
- falscher oder fehlender `X-API-Key`

Fix:
- `WARDROBE_API_KEY` aus `.env` prüfen
- denselben Wert im GPT-Dialog neu einsetzen

### Fall C – lokaler Test `200`, GPT trotzdem Fehler
Symptom:
- Backend funktioniert lokal, GPT meldet API-Fehler

Ursache:
- im GPT ist ein falscher oder alter Key gespeichert
- oder die Action hängt auf einem alten Zustand fest

Fix:
1. Key im GPT neu eintragen
2. Action speichern
3. wenn nötig Action löschen und neu anlegen

---

## 10. Ngrok

### Aktueller Stand
- historisch vorhanden
- für den **Custom GPT** nach Umstellung auf `api.capsule-studio.de` **nicht mehr erforderlich**

### Offene Entscheidung
Später separat prüfen:
- wird ngrok außerhalb des GPT überhaupt noch benötigt?
- falls nein: sauber stilllegen und Dokumentation bereinigen

---

## 11. Abschlussprüfung

### Prüfliste
1. `cloudflared` läuft
2. `capsule-studio.de` lädt
3. `api.capsule-studio.de/api/v2/items?user=karen` liefert ohne Header `Unauthorized JSON`
4. lokaler API-Test mit `X-API-Key` liefert `200`
5. öffentlicher API-Test mit `X-API-Key` liefert `200`
6. Custom GPT kann Bestandsdaten abrufen

---

## 12. Verweise

- `docs/RUNBOOK_VPS_WINDOWS_HARDENING.md`
- `docs/_handoff/HANDOFF_Capsule_VPS_RDP_Karen_2026-04-06_FINAL.md`
