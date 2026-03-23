param(
    [string]$SettingsPath = "$PSScriptRoot\vps-settings.ps1"
)

$ErrorActionPreference = "Stop"

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    throw "Run this script as Administrator."
}

. $SettingsPath

$taskSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DisallowStartOnRemoteAppSession:$false `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -MultipleInstances IgnoreNew `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

$apiAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\vps_run_api.ps1`" -SettingsPath `"$SettingsPath`""
$ngrokAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\vps_run_ngrok.ps1`" -SettingsPath `"$SettingsPath`""

Register-ScheduledTask -TaskName $CapsuleApiTaskName -Action $apiAction -Trigger $trigger -Principal $principal -Settings $taskSettings -Force | Out-Null
Register-ScheduledTask -TaskName $CapsuleNgrokTaskName -Action $ngrokAction -Trigger $trigger -Principal $principal -Settings $taskSettings -Force | Out-Null

Start-ScheduledTask -TaskName $CapsuleApiTaskName
Start-ScheduledTask -TaskName $CapsuleNgrokTaskName

Write-Host "[OK] Scheduled tasks installed and started."
Write-Host "API task:   $CapsuleApiTaskName"
Write-Host "ngrok task: $CapsuleNgrokTaskName"
