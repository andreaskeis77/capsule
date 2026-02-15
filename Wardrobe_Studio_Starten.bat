@echo off
setlocal EnableExtensions

REM =============================================================================
REM WARDROBE STUDIO - SICHERER SYSTEMSTART (v8.3 - PS5.1 kompatibel)
REM Fix: PowerShell 5.1 erlaubt NICHT stdout+stderr auf dieselbe Datei via Start-Process.
REM      Daher: getrennte Logfiles (*.out.log / *.err.log)
REM =============================================================================

pushd "%~dp0"
set "ROOT=%CD%"

set "HOST=127.0.0.1"
set "PORT=5002"
set "DEFAULT_USER=karen"
set "LOCAL_BASE=http://%HOST%:%PORT%"
set "DASH_URL=%LOCAL_BASE%/?user=%DEFAULT_USER%"
set "HEALTH_URL=%LOCAL_BASE%/healthz"
set "V2_HEALTH_URL=%LOCAL_BASE%/api/v2/health"
set "NGROK_DOMAIN=wardrobe.ngrok-app.com.ngrok.app"

REM switches (0/1)
if not defined START_NGROK set "START_NGROK=1"
if not defined OPEN_DASHBOARD set "OPEN_DASHBOARD=1"
if not defined OPEN_DOCS set "OPEN_DOCS=0"
if not defined FORCE_RESTART set "FORCE_RESTART=0"
if not defined KEEP_CONSOLE_OPEN set "KEEP_CONSOLE_OPEN=1"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$root='%ROOT%';" ^
  "$logDir=Join-Path $root 'logs'; New-Item -ItemType Directory -Force -Path $logDir | Out-Null;" ^
  "$ts=(Get-Date).ToString('yyyyMMdd-HHmmss');" ^
  "$startup=Join-Path $logDir 'startup.log';" ^
  "$serverOut=Join-Path $logDir 'server.out.log'; $serverErr=Join-Path $logDir 'server.err.log';" ^
  "$ngrokOut=Join-Path $logDir 'ngrok.out.log'; $ngrokErr=Join-Path $logDir 'ngrok.err.log';" ^
  "function Rotate([string]$p){ if(Test-Path $p){ $dir=[IO.Path]::GetDirectoryName($p); $base=[IO.Path]::GetFileNameWithoutExtension($p); $ext=[IO.Path]::GetExtension($p); $arch=[IO.Path]::Combine($dir, ($base+'_'+$ts+$ext)); Move-Item -Force $p $arch } }" ^
  "Rotate $startup; Rotate $serverOut; Rotate $serverErr; Rotate $ngrokOut; Rotate $ngrokErr;" ^
  "function Log([string]$m){ $line=((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')+' '+$m); Write-Host $line; Add-Content -Path $startup -Value $line }" ^
  "Log '============================================================';" ^
  "Log ('WARDROBE STUDIO START (v8.3) root='+$root);" ^
  "Log ('LOCAL_BASE=%LOCAL_BASE%'); Log ('DASH_URL=%DASH_URL%'); Log ('START_NGROK=%START_NGROK% FORCE_RESTART=%FORCE_RESTART%');" ^
  "Log ('LOGS: startup.log, server.out.log, server.err.log, ngrok.out.log, ngrok.err.log');" ^
  "$py=Join-Path $root '.venv\Scripts\python.exe'; if(!(Test-Path $py)){ Log ('[ERROR] Python nicht gefunden: '+$py); exit 1 }" ^
  "$ngrok=$null; if(Test-Path (Join-Path $root 'tools\ngrok.exe')){ $ngrok=(Join-Path $root 'tools\ngrok.exe') } else { $cmd=Get-Command ngrok -ErrorAction SilentlyContinue; if($cmd){ $ngrok=$cmd.Source } };" ^
  "if($env:START_NGROK -eq '1' -and -not $ngrok){ Log '[ERROR] ngrok.exe nicht gefunden (tools\ngrok.exe oder PATH)'; exit 1 }" ^
  "function HttpCode([string]$url){ try{ (Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 -Uri $url).StatusCode } catch { 0 } }" ^
  "function IsListening([int]$port){ (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) -ne $null }" ^
  "if(IsListening %PORT%){ $hc=HttpCode '%HEALTH_URL%'; if($hc -ne 200){ Log ('[WARN] Port %PORT% belegt, health='+$hc); if($env:FORCE_RESTART -eq '1'){ Log '[INFO] FORCE_RESTART -> Kill process on port';" ^
  "  $pids=(Get-NetTCPConnection -State Listen -LocalPort %PORT% -ErrorAction SilentlyContinue | Select-Object -Expand OwningProcess -Unique);" ^
  "  foreach($pid in $pids){ Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }; Start-Sleep -Seconds 1 } else { Log '[ERROR] Abbruch. Set FORCE_RESTART=1.'; exit 1 } } else { Log '[OK] Server läuft bereits.' } }" ^
  "if(-not (IsListening %PORT%)){" ^
  "  Log '[INFO] Starte FastAPI Server...';" ^
  "  '' | Set-Content -Path $serverOut; '' | Set-Content -Path $serverErr;" ^
  "  $p = Start-Process -WorkingDirectory $root -FilePath $py -ArgumentList @('-m','src.server_entry') -PassThru -WindowStyle Normal -RedirectStandardOutput $serverOut -RedirectStandardError $serverErr;" ^
  "  Log ('[INFO] Server PID='+$p.Id);" ^
  "}" ^
  "Log '[INFO] Warte auf Readiness...';" ^
  "$ready=$false; for($i=0;$i -lt 60;$i++){ if((HttpCode '%HEALTH_URL%') -eq 200){ $ready=$true; break }; Start-Sleep -Seconds 1 }" ^
  "if(-not $ready){ Log '[ERROR] Server nicht ready nach 60s'; Log '[INFO] Tail server.err.log:'; if(Test-Path $serverErr){ Get-Content $serverErr -Tail 120 | ForEach-Object { Log ('  '+$_) } }; Log '[INFO] Tail server.out.log:'; if(Test-Path $serverOut){ Get-Content $serverOut -Tail 120 | ForEach-Object { Log ('  '+$_) } }; exit 1 }" ^
  "Log '[OK] Server ist UP.'; Log ('[INFO] /api/v2/health -> '+(HttpCode '%V2_HEALTH_URL%'));" ^
  "if($env:OPEN_DASHBOARD -eq '1'){ Log '[INFO] Öffne Dashboard...'; Start-Process '%DASH_URL%' }" ^
  "if($env:OPEN_DOCS -eq '1'){ Start-Process '%LOCAL_BASE%/docs' }" ^
  "if($env:START_NGROK -eq '1'){" ^
  "  Log '[INFO] Starte ngrok...'; '' | Set-Content -Path $ngrokOut; '' | Set-Content -Path $ngrokErr;" ^
  "  Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue;" ^
  "  Start-Process -WorkingDirectory $root -FilePath $ngrok -ArgumentList @('http','--domain=%NGROK_DOMAIN%','%PORT%') -WindowStyle Normal -RedirectStandardOutput $ngrokOut -RedirectStandardError $ngrokErr | Out-Null;" ^
  "  $public=$null; for($i=0;$i -lt 30;$i++){ try{ $t=Invoke-RestMethod -TimeoutSec 2 -Uri 'http://127.0.0.1:4040/api/tunnels'; $public=($t.tunnels | Where-Object { $_.public_url -like 'https://*' } | Select-Object -First 1).public_url } catch { $public=$null } ; if($public){ break }; Start-Sleep -Seconds 1 }" ^
  "  if(-not $public){ Log '[ERROR] ngrok public_url nicht gefunden (30s)'; Log '[INFO] Tail ngrok.err.log:'; if(Test-Path $ngrokErr){ Get-Content $ngrokErr -Tail 200 | ForEach-Object { Log ('  '+$_) } }; Log '[INFO] Tail ngrok.out.log:'; if(Test-Path $ngrokOut){ Get-Content $ngrokOut -Tail 200 | ForEach-Object { Log ('  '+$_) } }; exit 1 }" ^
  "  Log ('[OK] ngrok public URL: '+$public);" ^
  "}" ^
  "Log '[DONE] Startup erfolgreich.'; exit 0"

set "RC=%ERRORLEVEL%"
popd

if "%KEEP_CONSOLE_OPEN%"=="1" pause
exit /b %RC%
