# HANDOFF – VPS Recovery Final State – 2026-04-05

## Finaler stabiler Zustand

- Capsule-API läuft als Scheduled Task `Capsule-API`
- ngrok läuft als Windows-Service `ngrok`
- Service-Account für ngrok: `.\svc-capsule`
- alter Scheduled Task `Capsule-ngrok` ist deaktiviert
- lokaler Health-Check: `http://127.0.0.1:8000/healthz` → ok
- öffentlicher Health-Check: `https://wardrobe.ngrok-app.com.ngrok.app/healthz` → ok
- `vps_smoke_test.ps1` → erfolgreich
- Reboot-Test → erfolgreich

## Wichtig

- API-Service-Migration via WinSW wurde versucht und zurückgerollt
- API bleibt vorerst bewusst beim Scheduled Task
- ngrok-Token wurde nicht rotiert
- `ngrok.yml` musste manuell korrigiert werden; Template-/Bootstrap-Logik noch prüfen