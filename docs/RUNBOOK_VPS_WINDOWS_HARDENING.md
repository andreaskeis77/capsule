# RUNBOOK – Capsule Windows VPS Recovery / Hardening / Repo-Fix

Stand: 2026-04-05  
Gilt für: `capsule` / Windows VPS / DEV-LAPTOP und VPS  
Zweck: belastbarer Rebuild- und Prüfpfad nach VPS-Neuaufbau, Security-Hardening, Capsule/ngrok-Wiederinbetriebnahme und Repo-Korrektur.

---

## 1. Ziel und Scope

Dieses Runbook dokumentiert den **bereits erreichten Recovery-Stand** und definiert den **sauberen Abschluss** in vier Schritten:

1. **Repo-Fixes auf dem DEV-LAPTOP sauber verifizieren und ins Repo bringen**  
2. **frisches, vollständiges Runbook ins Repo aufnehmen**  
3. **ngrok-Token rotieren und auf dem VPS neu setzen**  
4. **Reboot-Test des VPS durchführen**

Nicht Bestandteil dieses unmittelbaren Abschlusses:

- keine Umstellung auf separaten `capsule`-Betriebsuser
- keine Migration von Scheduled Tasks auf echte Windows-Services
- kein größeres Deployment-Redesign

Diese Themen sind bewusst nachgelagert.

---

## 2. Systemkontexte und Arbeitsregeln

### DEV-LAPTOP

- Gerät: lokaler Entwicklungsrechner
- Repo-Pfad: `C:\CapsuleWardrobeRAG`
- User-Kontext: normaler Windows-User
- „PowerShell als Administrator“ nur, wenn es wirklich nötig ist

### VPS

- Repo-Pfad: `C:\CapsuleWardrobeRAG`
- Betriebs-Admin: `srv-ops-admin`
- Für systemnahe Eingriffe: PowerShell als Administrator
- Für normale Sichtprüfungen: normale PowerShell-Sitzung genügt oft

### Arbeitsprinzip

- nur kleine, kontrollierte Änderungen
- nach jedem Block ein klarer Prüfpunkt
- erst prüfen, dann committen, dann pushen
- keine alten fehlerhaften Runbook-Versionen weiterverwenden

---

## 3. Bereits bestätigter Stand auf dem VPS

### 3.1 Security / Hardening bereits umgesetzt

Auf dem VPS wurden bereits erfolgreich umgesetzt:

- Windows Updates installiert
- neues lokales Adminkonto `srv-ops-admin` angelegt
- Login per RDP mit `\.\srv-ops-admin` erfolgreich getestet
- alter eingebauter Administrator deaktiviert
- `cloudbase-admin` als umbenanntes Built-in-Admin-Konto identifiziert und deaktiviert belassen
- Contabo-Firewall aktiviert, RDP nur von Heim-IP erlaubt
- Windows-Firewall ebenfalls auf RDP nur von Heim-IP eingeschränkt
- NLA für RDP aktiviert
- Account-Lockout gesetzt
- Passwortpolicy gehärtet
- Microsoft Defender aktiv und geprüft
- `cloudbase-init` analysiert und deaktiviert
- WinRM deaktiviert
- Print Spooler deaktiviert
- Google Updater deaktiviert
- unnötige Consumer-/Desktop-Firewallregeln deaktiviert
- Wireless Networking entfernt
- XPS Viewer entfernt
- Windows Admin Center Setup entfernt bzw. nicht mehr installiert
- SMB/NetBIOS pragmatisch reduziert, aber nicht maximal aggressiv gehärtet

### 3.2 Betriebsregel für den VPS

Der VPS wird **nicht** als persönlicher Desktop verwendet:

- kein privates Google-/Chrome-Profil
- keine privaten Dokumente
- keine privaten Mail- oder Passwort-Workflows
- nur serverrelevante Software

---

## 4. Bereits bestätigter Capsule-/ngrok-Betriebsstand auf dem VPS

### 4.1 Aktuelles Betriebsmodell

Capsule-API und ngrok laufen aktuell **nicht als Windows-Services**, sondern als **Windows Scheduled Tasks**.

Tasknamen:

- `Capsule-API`
- `Capsule-ngrok`

Aktuell laufen diese Tasks unter `SYSTEM`.

### 4.2 Funktional bestätigter Stand

Folgendes wurde bereits erfolgreich bestätigt:

- lokale API: `http://127.0.0.1:8000/healthz` → `ok`
- öffentliche API via ngrok → `.../healthz` → `ok`

Wichtig: Im bisherigen Handoff wurde eine öffentliche URL genannt, die syntaktisch auffällig wirkt (`wardrobe.ngrok-app.com.ngrok.app`). Deshalb im nächsten Prüfzyklus **nicht blind übernehmen**, sondern den tatsächlich konfigurierten ngrok-Host bzw. die reale öffentliche URL explizit gegenprüfen.

Technisch bedeutet der bestätigte Stand:

- API läuft lokal auf `127.0.0.1:8000`
- ngrok published den Dienst öffentlich
- `/healthz` ist der gültige Health-Endpunkt

---

## 5. Technische Root Causes und Repo-Probleme

### 5.1 Defekt in `deploy/windows-vps/vps_run_api.ps1`

Der frühere Repo-Stand war für den aktuellen Code nicht mehr passend.

Problematisch war sinngemäß:

```powershell
python -m uvicorn src.server_entry:app ...
```

Das ist für den aktuellen Stand falsch, weil:

- `src.server_entry.py` aktuell kein geeignetes `app`-Objekt exportiert
- die tatsächlich laufende App derzeit unter `src.api_main:app` liegt

Zusätzlich musste der Startmechanismus so angepasst werden, dass die API im Task-Kontext robust hochkommt. Die funktionierende Hotfix-Variante auf dem VPS startet `uvicorn` für `src.api_main:app` via `Start-Process`.

### 5.2 Fehlende Datei `deploy/windows-vps/ngrok.template.yml`

`vps_bootstrap.ps1` erwartete diese Datei. Sie fehlte im Repo-Stand bzw. führte beim Bootstrap zu Problemen. Auf dem VPS wurde sie manuell ergänzt.

### 5.3 Veraltete Health-Referenzen

Mindestens diese Dateien zeigten noch auf `/health` statt `/healthz`:

- `deploy/windows-vps/example.vps-settings.ps1`
- `deploy/windows-vps/vps_smoke_test.ps1`

Diese Stellen müssen im Repo konsistent auf `/healthz` korrigiert werden.

---

## 6. Pflichtschritt 1 – Repo-Review auf dem DEV-LAPTOP

### 6.1 Ziel

Auf dem DEV-LAPTOP in `C:\CapsuleWardrobeRAG` die tatsächlichen Inhalte dieser Dateien prüfen:

- `deploy/windows-vps/vps_run_api.ps1`
- `deploy/windows-vps/ngrok.template.yml`
- `deploy/windows-vps/example.vps-settings.ps1`
- `deploy/windows-vps/vps_smoke_test.ps1`

Zusätzlich eine neue Runbook-Datei ins Repo aufnehmen, z. B.:

- `docs/RUNBOOK_VPS_WINDOWS_HARDENING.md`

### 6.2 Prüfkommando: Git-Status und Diff

**DEV-LAPTOP – normale PowerShell**

```powershell
cd C:\CapsuleWardrobeRAG

git status --short

git diff -- deploy/windows-vps/vps_run_api.ps1 `
             deploy/windows-vps/ngrok.template.yml `
             deploy/windows-vps/example.vps-settings.ps1 `
             deploy/windows-vps/vps_smoke_test.ps1
```

### 6.3 Prüfkommando: Dateiinhalte vollständig anzeigen

```powershell
cd C:\CapsuleWardrobeRAG

Write-Host "`n=== vps_run_api.ps1 ==="
Get-Content .\deploy\windows-vps\vps_run_api.ps1

Write-Host "`n=== ngrok.template.yml ==="
Get-Content .\deploy\windows-vps\ngrok.template.yml

Write-Host "`n=== example.vps-settings.ps1 ==="
Get-Content .\deploy\windows-vps\example.vps-settings.ps1

Write-Host "`n=== vps_smoke_test.ps1 ==="
Get-Content .\deploy\windows-vps\vps_smoke_test.ps1
```

### 6.4 Erwarteter Sollzustand pro Datei

#### `vps_run_api.ps1`

Muss fachlich mindestens sicherstellen:

- Start von `uvicorn`
- Ziel-App ist `src.api_main:app`
- Bindung an `127.0.0.1:8000`
- robuster Start im Task-Kontext, bevorzugt via `Start-Process`
- keine implizite Abhängigkeit auf ein nicht existierendes `src.server_entry:app`

#### `ngrok.template.yml`

Muss vorhanden sein und zum Bootstrap-Modell passen, also mindestens:

- Tunnel-/Endpoint-Definition für die lokale API
- Weiterleitung auf `http://127.0.0.1:8000`
- ein Format, aus dem `ngrok.yml` reproduzierbar erzeugt werden kann

#### `example.vps-settings.ps1`

Muss mindestens konsistent sein mit:

- API auf `127.0.0.1:8000`
- Health-Endpunkt `/healthz`
- plausiblen Variablen für ngrok / Domain / Token / Repo-Pfade

#### `vps_smoke_test.ps1`

Muss mindestens testen:

- lokale Health-Prüfung auf `http://127.0.0.1:8000/healthz`
- öffentliche Health-Prüfung auf der realen ngrok-URL mit `/healthz`
- aussagekräftige Exit-Codes / Fehlermeldungen

### 6.5 Minimaler inhaltlicher Suchtest

```powershell
cd C:\CapsuleWardrobeRAG

Select-String -Path .\deploy\windows-vps\*.ps1, .\deploy\windows-vps\*.yml `
  -Pattern "src.server_entry:app","src.api_main:app","/health","/healthz"
```

Erwartung:

- produktive Startpfade sollten `src.api_main:app` referenzieren
- Health-Prüfungen sollten auf `/healthz` zeigen
- verbliebene `/health`-Treffer müssen bewusst bewertet werden

---

## 7. Pflichtschritt 2 – frisches Runbook ins Repo aufnehmen

Dieses Dokument soll inhaltlich als Basis dienen, aber **frisch** ins Repo übernommen werden. Kein Rückgriff auf den fehlerhaften Alt-Download.

Empfohlener Repo-Pfad:

```text
docs/RUNBOOK_VPS_WINDOWS_HARDENING.md
```

Prüfung:

```powershell
cd C:\CapsuleWardrobeRAG

Test-Path .\docs\RUNBOOK_VPS_WINDOWS_HARDENING.md
Get-Content .\docs\RUNBOOK_VPS_WINDOWS_HARDENING.md -First 40
```

---

## 8. Pflichtschritt 3 – Commit und Push der Repo-Fixes

### 8.1 Vor dem Commit

Empfohlen:

```powershell
cd C:\CapsuleWardrobeRAG

git status --short
```

Nur die wirklich beabsichtigten Dateien sollen enthalten sein:

- `deploy/windows-vps/vps_run_api.ps1`
- `deploy/windows-vps/ngrok.template.yml`
- `deploy/windows-vps/example.vps-settings.ps1`
- `deploy/windows-vps/vps_smoke_test.ps1`
- `docs/RUNBOOK_VPS_WINDOWS_HARDENING.md`

### 8.2 Add / Commit / Push

```powershell
cd C:\CapsuleWardrobeRAG

git add .\deploy\windows-vps\vps_run_api.ps1 `
        .\deploy\windows-vps\ngrok.template.yml `
        .\deploy\windows-vps\example.vps-settings.ps1 `
        .\deploy\windows-vps\vps_smoke_test.ps1 `
        .\docs\RUNBOOK_VPS_WINDOWS_HARDENING.md

git commit -m "fix(vps): repair api startup, ngrok bootstrap, healthz checks, and add runbook"

git push origin main
```

### 8.3 Nach dem Push

```powershell
cd C:\CapsuleWardrobeRAG

git status --short
git log -1 --stat
```

Erwartung:

- Worktree sauber oder nur bewusst uncommittete Restdateien
- letzter Commit enthält genau die VPS-Fixdateien und das Runbook

---

## 9. Pflichtschritt 4 – ngrok-Token rotieren

### 9.1 Warum

Der ngrok-Token wurde in einem früheren Chat sichtbar. Deshalb ist Rotation Pflicht.

### 9.2 Zielzustand

- neuer ngrok-Token erzeugt
- alter Token als kompromittiert behandeln
- neuer Token auf dem VPS in `deploy/windows-vps/vps-settings.ps1` setzen
- `Capsule-ngrok` neu starten
- öffentliche Health-Prüfung erneut durchführen

### 9.3 Ablauf

#### Schritt A – außerhalb des VPS

- im ngrok-Konto anmelden
- alten Token widerrufen / rotieren
- neuen Token erzeugen

#### Schritt B – Token auf dem VPS aktualisieren

**VPS – `srv-ops-admin`, PowerShell als Administrator nur falls nötig**

```powershell
cd C:\CapsuleWardrobeRAG
notepad .\deploy\windows-vps\vps-settings.ps1
```

Dort den neuen Token eintragen.

Danach Datei prüfen:

```powershell
Get-Content .\deploy\windows-vps\vps-settings.ps1
```

Achtung: nur kontrolliert anzeigen, nicht unnötig weiterverteilen oder irgendwo committen. `vps-settings.ps1` bleibt eine lokale Betriebsdatei und gehört nicht in Git.

### 9.4 ngrok-Task neu starten

```powershell
Stop-ScheduledTask -TaskName "Capsule-ngrok" -ErrorAction SilentlyContinue
Start-ScheduledTask -TaskName "Capsule-ngrok"
```

Kurze Sichtprüfung:

```powershell
Get-ScheduledTask -TaskName "Capsule-ngrok" | Get-ScheduledTaskInfo
```

### 9.5 Öffentliche URL prüfen

Den tatsächlich genutzten ngrok-Host / die öffentliche URL explizit verifizieren. Nicht blind alte Chatwerte übernehmen.

Beispielprüfung:

```powershell
Invoke-RestMethod https://<DEINE-TATSAECHLICHE-NGROK-URL>/healthz
```

Erwartung:

- Antwort `ok`

---

## 10. VPS-Validierung nach Rotation

### 10.1 Lokale API

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
```

Erwartung:

- `ok`

### 10.2 API-Task prüfen

```powershell
Get-ScheduledTask -TaskName "Capsule-API" | Get-ScheduledTaskInfo
```

### 10.3 ngrok-Task prüfen

```powershell
Get-ScheduledTask -TaskName "Capsule-ngrok" | Get-ScheduledTaskInfo
```

Optional zusätzlich:

```powershell
Get-Process python -ErrorAction SilentlyContinue
Get-Process ngrok -ErrorAction SilentlyContinue
```

---

## 11. Pflichtschritt 5 – Reboot-Test des VPS

### 11.1 Ziel

Nach Repo-Fix und Token-Rotation prüfen, ob der Server einen Neustart sauber überlebt.

### 11.2 Durchführung

**VPS – `srv-ops-admin`**

```powershell
shutdown /r /t 0
```

Nach dem Neustart erneut anmelden und diese Reihenfolge prüfen:

### 11.3 Task-Status nach Reboot

```powershell
Get-ScheduledTask -TaskName "Capsule-API" | Get-ScheduledTaskInfo
Get-ScheduledTask -TaskName "Capsule-ngrok" | Get-ScheduledTaskInfo
```

### 11.4 Lokale Health-Prüfung

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
```

Erwartung:

- `ok`

### 11.5 Öffentliche Health-Prüfung

```powershell
Invoke-RestMethod https://<DEINE-TATSAECHLICHE-NGROK-URL>/healthz
```

Erwartung:

- `ok`

### 11.6 Optionaler Smoke-Test via Skript

Wenn `vps_smoke_test.ps1` sauber korrigiert wurde:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\windows-vps\vps_smoke_test.ps1
```

---

## 12. Empfohlene Gate-Logik für den nächsten Chatdurchlauf

### Gate A – Repo Review bestanden

Erst wenn diese Aussagen stimmen, weitergehen:

- `vps_run_api.ps1` zeigt auf `src.api_main:app`
- `ngrok.template.yml` existiert wirklich
- `example.vps-settings.ps1` nutzt `/healthz`
- `vps_smoke_test.ps1` nutzt `/healthz`
- neues Runbook liegt im Repo

### Gate B – Git sauber

- nur beabsichtigte Dateien im Commit
- Commit erfolgreich
- Push erfolgreich

### Gate C – Token-Rotation sauber

- Token erneuert
- `Capsule-ngrok` neugestartet
- öffentlicher `/healthz` erfolgreich

### Gate D – Reboot-Test sauber

- `Capsule-API` nach Reboot wieder oben
- `Capsule-ngrok` nach Reboot wieder oben
- lokal `/healthz` ok
- öffentlich `/healthz` ok

---

## 13. Was bewusst später kommt

Diese Architekturfragen sind sinnvoll, aber bewusst nicht Teil des unmittelbaren Recovery-Abschlusses:

- Betrieb unter separatem Service-User statt `SYSTEM`
- echte Windows-Services statt Scheduled Tasks
- härtere SMB-/NetBIOS-Minimierung
- zentrales Logging / Eventlog-orientierter Service-Betrieb
- Secrets-Handling weiter professionalisieren

Sinnvolle spätere Evolutionsstufe:

- `Capsule-API` als echter Windows-Service
- `ngrok` als eigener Windows-Service
- klar definierte Recovery- und Log-Pfade

---

## 14. Empfohlener Einstieg im neuen Chat

Die erste Arbeitsrunde im neuen Chat sollte exakt so beginnen:

1. **DEV-LAPTOP:** Repo-Review der vier Deploy-Dateien  
2. **DEV-LAPTOP:** neues Runbook als Markdown-Datei finalisieren  
3. **DEV-LAPTOP:** Add / Commit / Push  
4. **VPS:** ngrok-Token rotieren  
5. **VPS:** `Capsule-ngrok` neu starten und Health prüfen  
6. **VPS:** Reboot-Test durchführen

---

## 15. Kurzfassung für operative Abarbeitung

### DEV-LAPTOP

```powershell
cd C:\CapsuleWardrobeRAG

git status --short
git diff -- deploy/windows-vps/vps_run_api.ps1 deploy/windows-vps/ngrok.template.yml deploy/windows-vps/example.vps-settings.ps1 deploy/windows-vps/vps_smoke_test.ps1
Get-Content .\deploy\windows-vps\vps_run_api.ps1
Get-Content .\deploy\windows-vps\ngrok.template.yml
Get-Content .\deploy\windows-vps\example.vps-settings.ps1
Get-Content .\deploy\windows-vps\vps_smoke_test.ps1
Select-String -Path .\deploy\windows-vps\*.ps1, .\deploy\windows-vps\*.yml -Pattern "src.server_entry:app","src.api_main:app","/health","/healthz"
```

Dann:

```powershell
git add .\deploy\windows-vps\vps_run_api.ps1 `
        .\deploy\windows-vps\ngrok.template.yml `
        .\deploy\windows-vps\example.vps-settings.ps1 `
        .\deploy\windows-vps\vps_smoke_test.ps1 `
        .\docs\RUNBOOK_VPS_WINDOWS_HARDENING.md

git commit -m "fix(vps): repair api startup, ngrok bootstrap, healthz checks, and add runbook"
git push origin main
```

### VPS

```powershell
cd C:\CapsuleWardrobeRAG
notepad .\deploy\windows-vps\vps-settings.ps1
Stop-ScheduledTask -TaskName "Capsule-ngrok" -ErrorAction SilentlyContinue
Start-ScheduledTask -TaskName "Capsule-ngrok"
Invoke-RestMethod http://127.0.0.1:8000/healthz
Invoke-RestMethod https://<DEINE-TATSAECHLICHE-NGROK-URL>/healthz
shutdown /r /t 0
```

Nach Reboot erneut:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
Invoke-RestMethod https://<DEINE-TATSAECHLICHE-NGROK-URL>/healthz
```

---

## 16. Abschlusskriterium

Der Recovery-/Hardening-Abschnitt ist erst dann wirklich abgeschlossen, wenn alle folgenden Punkte erfüllt sind:

- Repo-Fixes sind sauber geprüft
- Runbook ist frisch und vollständig im Repo
- Commit und Push sind erfolgt
- ngrok-Token ist rotiert
- lokale Health-Prüfung ist erfolgreich
- öffentliche Health-Prüfung ist erfolgreich
- Reboot-Test ist erfolgreich

Erst danach sollte die nächste Infrastrukturstufe diskutiert werden.

## 17. Final validierter Ist-Zustand nach Recovery

Stand nach erfolgreichem Reboot-Test auf dem VPS:

### 17.1 Aktives Betriebsmodell

- **Capsule-API** läuft aktuell weiterhin als **Windows Scheduled Task**
  - Taskname: `Capsule-API`
  - aktueller Zustand: funktionsfähig
  - lokaler Health-Check: `http://127.0.0.1:8000/healthz` → `ok`

- **ngrok** läuft aktuell als **echter Windows-Service**
  - Service-Name: `ngrok`
  - Service-Account: `.\svc-capsule`
  - öffentlicher Health-Check: `https://wardrobe.ngrok-app.com.ngrok.app/healthz` → `ok`

- Der frühere Scheduled Task **`Capsule-ngrok`** wurde deaktiviert und ist nicht mehr der aktive Betriebsweg.

### 17.2 Reboot-validierter Endzustand

Nach erfolgreichem Neustart des VPS wurde bestätigt:

- `ngrok`-Service startet korrekt
- `Capsule-API`-Task startet korrekt
- lokaler `/healthz` ist erreichbar
- öffentlicher `/healthz` ist erreichbar
- `vps_smoke_test.ps1` läuft erfolgreich durch

### 17.3 Wichtige Betriebsbewertung

Damit ist der Recovery-Abschnitt operativ erfolgreich abgeschlossen.

Der derzeitige stabile Zielzustand ist ausdrücklich:

- **Capsule-API als Scheduled Task belassen**
- **ngrok als Windows-Service belassen**

---

## 18. Ergebnis der API-Service-Migration

### 18.1 Versuch

Es wurde versucht, die Capsule-API ebenfalls von Scheduled Task auf einen echten Windows-Service umzustellen, mit **WinSW** als Service-Wrapper und dem Service-Account `.\svc-capsule`.

### 18.2 Ergebnis

Dieser Versuch war **nicht erfolgreich**.

Beim Test nach Umstellung zeigte sich:

- `CapsuleApi`-Service blieb gestoppt
- lokaler API-Endpunkt `http://127.0.0.1:8000/healthz` war nicht erreichbar
- öffentlicher Endpunkt lieferte dadurch `502 Bad Gateway`
- der Smoke-Test schlug fehl

### 18.3 Maßnahme

Die Änderung wurde sauber **zurückgerollt**:

- WinSW-basierter `CapsuleApi`-Service wurde entfernt
- `Capsule-API` Scheduled Task wurde wieder aktiviert
- API wurde wieder per Task gestartet
- lokaler und öffentlicher Health-Check waren danach wieder erfolgreich

### 18.4 Schlussfolgerung

Die API-Service-Migration ist **derzeit nicht Teil des produktiven Zielzustands**.

Bis zu einer sauberen technischen Klärung bleibt die API bewusst bei:

- **Scheduled Task**
- **nicht als WinSW-Service**

---

## 19. Bekannte offene Punkte

### 19.1 ngrok-Template-/Bootstrap-Logik nicht abschließend bereinigt

Während der Recovery zeigte sich, dass `ngrok.yml` zeitweise ungültig war, weil dort der Platzhalter `__DOMAIN_LINE__` wörtlich verblieben war.

Die Datei musste manuell repariert werden, damit ngrok wieder korrekt starten konnte.

Daraus folgt:

- die Logik rund um `ngrok.template.yml`
- sowie die Verarbeitung in `vps_bootstrap.ps1` und/oder `vps_run_ngrok.ps1`

ist fachlich noch einmal gezielt zu prüfen.

### 19.2 ngrok-Token nicht rotiert

Der ngrok-Token wurde im Verlauf der Arbeiten sichtbar und später nicht rotiert.

Das blockiert den aktuellen Betrieb nicht, bleibt aber ein offener Security-Follow-up.

### 19.3 Service-Migration der API vertagt

Die Frage, ob die Capsule-API künftig ebenfalls als echter Windows-Service betrieben werden soll, ist weiterhin offen.

Diese Entscheidung wurde bewusst vertagt, weil der aktuelle Produktionszustand stabil ist und der WinSW-Versuch nicht erfolgreich war.

---

## 20. Aktuelle operative Empfehlung

Bis auf Weiteres gilt für den VPS folgender Zielzustand:

- **Capsule-API** über Scheduled Task `Capsule-API`
- **ngrok** über Windows-Service `ngrok`
- **Capsule-ngrok** Task deaktiviert lassen
- keine weitere Live-Umbauarbeit auf dem VPS ohne separaten Change-Schritt

---

## 21. Empfohlener nächster Engineering-Bolt

Der nächste kleine, kontrollierte Folgeschritt sollte auf dem DEV-LAPTOP vorbereitet werden und nur diese Punkte behandeln:

1. Prüfung von `vps_bootstrap.ps1`
2. Prüfung von `vps_run_ngrok.ps1`
3. Klärung, warum `ngrok.yml` mit `__DOMAIN_LINE__` in einen ungültigen Zustand geraten konnte
4. Dokumentations-Update für den finalen Betriebszustand
5. Optionale Entscheidungsvorlage: API dauerhaft als Task belassen oder später mit anderem Service-Ansatz erneut migrieren

