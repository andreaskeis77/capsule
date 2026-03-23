# Windows VPS Deployment

## Zielbild
- Capsule läuft zentral auf einem Windows-VPS.
- Die API/Web-App bindet **nur lokal** auf `127.0.0.1:8000`.
- Externer Zugriff läuft ausschließlich über **ngrok auf dem VPS**.
- Karen braucht danach keinen lokalen Server mehr.

## Reihenfolge
1. Repo auf den VPS klonen nach `C:\CapsuleWardrobeRAG`
2. `example.vps-settings.ps1` zu `vps-settings.ps1` kopieren und anpassen
3. `vps_bootstrap.ps1` ausführen
4. `vps_install_tasks.ps1` als Administrator ausführen
5. `vps_smoke_test.ps1` ausführen
6. ngrok-Domain im Custom GPT und ggf. in der Website hinterlegen

## Update-Pfad
- Code ändern, committen, nach GitHub pushen
- Auf dem VPS:
  `powershell -ExecutionPolicy Bypass -File .\deploy\windows-vps\vps_update_from_git.ps1`
