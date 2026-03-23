param(
    [string]$SettingsPath = "$PSScriptRoot\vps-settings.ps1"
)

$ErrorActionPreference = "Stop"
. $SettingsPath

New-Item -ItemType Directory -Force -Path $CapsuleLogsDir | Out-Null

$stdout = Join-Path $CapsuleLogsDir "capsule-api.out.log"
$stderr = Join-Path $CapsuleLogsDir "capsule-api.err.log"

Set-Location $CapsuleRepoRoot
& $CapsulePythonExe -m uvicorn src.server_entry:app --host $CapsuleBindHost --port $CapsuleBindPort --proxy-headers 1>> $stdout 2>> $stderr
