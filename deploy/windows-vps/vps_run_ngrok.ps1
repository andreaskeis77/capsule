param(
    [string]$SettingsPath = "$PSScriptRoot\vps-settings.ps1"
)

$ErrorActionPreference = "Stop"
. $SettingsPath

if (-not (Test-Path $NgrokExe)) {
    throw "ngrok executable not found: $NgrokExe"
}
if (-not (Test-Path $NgrokConfigPath)) {
    throw "ngrok config not found: $NgrokConfigPath"
}

New-Item -ItemType Directory -Force -Path $CapsuleLogsDir | Out-Null

$stdout = Join-Path $CapsuleLogsDir "capsule-ngrok.out.log"
$stderr = Join-Path $CapsuleLogsDir "capsule-ngrok.err.log"

& $NgrokExe start --all --config $NgrokConfigPath 1>> $stdout 2>> $stderr
