# RUNBOOK – Capsule VPS Windows Hardening and Access Model

**Status:** gültiger Zielzustand nach Stabilisierung am 2026-04-07  
**System:** Contabo Windows VPS  
**Repo-Pfad:** `C:\CapsuleWardrobeRAG`

---

## 1. Zielbild

Dieses Runbook beschreibt den aktuellen Soll-Zustand für den administrativen Zugang und die Basis-Härtung des Capsule-VPS.

### Soll-Zustand
- **Kein öffentliches RDP**
- **Admin-Zugang ausschließlich per Tailscale-RDP**
- **Windows Defender Firewall aktiv**
- **VNC deaktiviert**
- **Cloudflare Tunnel als Windows-Service**
- **Capsule API lokal auf `127.0.0.1:8000`**

---

## 2. Admin-Zugang

### Primärer Zugangsweg
- RDP über **Tailscale**
- aktuelle Tailscale-IP des VPS: `100.71.205.5`
- Login mit lokalem Windows-Benutzer, z. B. `\.\srv-ops-admin`

### Nicht mehr zulässig als Normalbetrieb
- öffentliches RDP auf `84.247.164.122:3389`
- breite Freigaben in der Contabo-Firewall
- deaktivierte Windows-Firewall

---

## 3. Firewall-Grundsätze

### Contabo-Firewall
- **kein** öffentlicher Inbound auf Port `3389`
- öffentliche Freigaben nur für tatsächlich benötigte Dienste

### Windows Defender Firewall
- alle Profile **Enabled = True**
- `DefaultInboundAction = Block`
- `DefaultOutboundAction = Allow`
- Standardgruppe **Remote Desktop** darf aktiv sein, solange öffentliches RDP bereits providerseitig geschlossen ist
- keine temporären Sonderregeln wie `TEMP-RDP-*` im Dauerbetrieb

### Prüfkommandos
```powershell
Get-NetFirewallProfile | Format-Table Name, Enabled, DefaultInboundAction, DefaultOutboundAction -Auto
Get-NetFirewallRule -DisplayGroup "Remote Desktop" |
  Select-Object DisplayName, Enabled, Profile, Direction, Action |
  Format-Table -Auto
Test-NetConnection 84.247.164.122 -Port 3389
```

Erwartung:
- `84.247.164.122:3389` → `TcpTestSucceeded : False`

---

## 4. Tailscale

### Ziel
Tailscale ersetzt den früheren öffentlichen RDP-Weg.

### Anforderungen
- Client auf VPS installiert
- Client auf DEV-LAPTOP installiert
- VPS auf **Run unattended** gesetzt

### Basisprüfungen
Auf Laptop:
```powershell
ping 100.71.205.5
mstsc /v:100.71.205.5
```

### Betriebsregel
Vor Änderungen an Firewall, Tunnel, Access oder Diensten immer zuerst sicherstellen, dass Tailscale-RDP funktioniert.

---

## 5. Recovery-Pfad

### VNC
- VNC ist **kein Normalbetrieb**
- VNC nur als temporärer Recovery-Weg verwenden
- nach erfolgreicher Stabilisierung wieder deaktivieren

### Reihenfolge bei Störungen
1. Tailscale-RDP prüfen
2. lokale Dienste prüfen
3. Cloudflare / `cloudflared` prüfen
4. nur im Ausnahmefall VNC vorübergehend aktivieren

---

## 6. Lokale App- und API-Laufzeit

### Capsule API
- läuft lokal auf `127.0.0.1:8000`
- Health-Check für Laufzeitprüfung: `/healthz`

### Prüfkommandos
```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
```

Optional mit API-Key für echte API-Route:
```powershell
$key = "<WARDROBE_API_KEY>"
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/v2/items?user=karen" `
  -Headers @{ "X-API-Key" = $key } `
  -Method GET `
  -UseBasicParsing
```

---

## 7. Dienste auf dem VPS

### Erwartete Kernkomponenten
- Capsule API
- Tailscale
- `cloudflared`
- optional: ngrok nur, wenn außerhalb des GPT noch gebraucht

### Cloudflared prüfen
```powershell
Get-Service cloudflared | Format-Table Name, Status, StartType -Auto
```

Soll:
- `Status = Running`
- `StartType = Automatic`

---

## 8. Reboot-Checkliste

Nach sicherheitsrelevanten Änderungen immer:
1. VPS neu starten
2. Tailscale-Ping prüfen
3. Tailscale-RDP prüfen
4. `cloudflared` prüfen
5. lokale API prüfen
6. öffentliche Web-/API-Domains prüfen

---

## 9. Dinge, die nicht wieder passieren sollen

- Windows-Firewall dauerhaft deaktivieren
- öffentliches RDP breit öffnen
- mehrere Schutzschichten gleichzeitig blind ändern
- Tailscale und VNC gleichzeitig aufgeben, bevor der neue Zugang validiert ist

---

## 10. Verweise

- Abschluss-Handoff: `docs/_handoff/HANDOFF_Capsule_VPS_RDP_Karen_2026-04-06_FINAL.md`
- Cloudflare-/GPT-Betrieb: `docs/RUNBOOK_VPS_ACCESS_AND_CLOUDFLARE.md`
