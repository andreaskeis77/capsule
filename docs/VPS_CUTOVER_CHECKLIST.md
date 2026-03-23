# VPS Cutover Checklist

## Vor dem Cutover
- [ ] `main` ist grün validiert
- [ ] VPS erreichbar
- [ ] Python 3.12+ installiert
- [ ] Git installiert
- [ ] ngrok installiert
- [ ] `vps-settings.ps1` gesetzt
- [ ] ngrok Authtoken gesetzt
- [ ] optional reserved ngrok domain vorhanden

## Deployment
- [ ] Repo auf VPS geklont
- [ ] `vps_bootstrap.ps1` erfolgreich
- [ ] `vps_install_tasks.ps1` erfolgreich
- [ ] `vps_smoke_test.ps1` erfolgreich
- [ ] lokale Health-URL erfolgreich
- [ ] öffentliche Health-URL erfolgreich

## Cutover
- [ ] Custom GPT Action / Endpoint auf VPS-ngrok-URL umgestellt
- [ ] Website-Konfiguration auf VPS-Backend umgestellt
- [ ] Karen-Laptop-Server dauerhaft abgeschaltet
- [ ] Test durch Karen erfolgreich

## Nach dem Cutover
- [ ] Logs geprüft
- [ ] Update-Prozess dokumentiert
- [ ] Verantwortlichkeiten klar
