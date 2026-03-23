# VPS Deployment Runbook

## Ziel
Capsule wird auf einem **Windows-VPS** als zentraler Laufzeitstandort betrieben.  
Der VPS übernimmt:
- API / Web-App
- ngrok-Tunnel
- Logs
- Update-Pfad per Git

Karen braucht danach **keinen lokalen Server** mehr.

## Betriebsmodell
- Backend bindet lokal auf `127.0.0.1:8000`
- Öffentliche Erreichbarkeit läuft über ngrok auf dem VPS
- Custom GPT und Website nutzen dieselbe öffentliche Ziel-URL
- Website spricht nur mit dem VPS-Backend; OpenAI-Aufrufe gehören serverseitig ins Backend

## Erstinstallation auf dem VPS
```powershell
cd C:\
git clone https://github.com/andreaskeis77/capsule.git C:\CapsuleWardrobeRAG
cd C:\CapsuleWardrobeRAG
Copy-Item .\deploy\windows-vps\example.vps-settings.ps1 .\deploy\windows-vps\vps-settings.ps1
# vps-settings.ps1 bearbeiten
powershell -ExecutionPolicy Bypass -File .\deploy\windows-vps\vps_bootstrap.ps1
powershell -ExecutionPolicy Bypass -File .\deploy\windows-vps\vps_install_tasks.ps1
powershell -ExecutionPolicy Bypass -File .\deploy\windows-vps\vps_smoke_test.ps1
```

## Update auf dem VPS
```powershell
cd C:\CapsuleWardrobeRAG
powershell -ExecutionPolicy Bypass -File .\deploy\windows-vps\vps_update_from_git.ps1
```

## Logs
- `logs\vps\capsule-api.out.log`
- `logs\vps\capsule-api.err.log`
- `logs\vps\capsule-ngrok.out.log`
- `logs\vps\capsule-ngrok.err.log`

## Fehlerbild
1. `vps_smoke_test.ps1` lokal ausführen
2. Scheduled Tasks prüfen:
   - `Capsule-API`
   - `Capsule-ngrok`
3. Logdateien in `logs\vps\` prüfen
4. Bei Code-Änderungen immer zuerst lokal `python .\tools\run_quality_gates.py`
