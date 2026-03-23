param(
    [string]$SettingsPath = "$PSScriptRoot\vps-settings.ps1",
    [switch]$SkipQualityGates
)

$ErrorActionPreference = "Stop"
. $SettingsPath

Set-Location $CapsuleRepoRoot

try { Stop-ScheduledTask -TaskName $CapsuleApiTaskName -ErrorAction SilentlyContinue } catch {}
try { Stop-ScheduledTask -TaskName $CapsuleNgrokTaskName -ErrorAction SilentlyContinue } catch {}

git fetch origin
git checkout $CapsuleGitBranch
git pull origin $CapsuleGitBranch

powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\vps_bootstrap.ps1" -SettingsPath $SettingsPath

if (-not $SkipQualityGates) {
    & $CapsulePythonExe .\tools\run_quality_gates.py
}

Start-ScheduledTask -TaskName $CapsuleApiTaskName
Start-ScheduledTask -TaskName $CapsuleNgrokTaskName

Write-Host "[OK] VPS update finished."
