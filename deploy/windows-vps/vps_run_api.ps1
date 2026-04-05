param(
    [string]$SettingsPath = "$PSScriptRoot\vps-settings.ps1"
)

$ErrorActionPreference = "Stop"
. $SettingsPath

New-Item -ItemType Directory -Force -Path $CapsuleLogsDir | Out-Null

$stdout = Join-Path $CapsuleLogsDir "capsule-api.out.log"
$stderr = Join-Path $CapsuleLogsDir "capsule-api.err.log"

Set-Location $CapsuleRepoRoot

$args = @(
    "-m", "uvicorn",
    "src.api_main:app",
    "--host", $CapsuleBindHost,
    "--port", [string]$CapsuleBindPort,
    "--proxy-headers"
)

$proc = Start-Process `
    -FilePath $CapsulePythonExe `
    -ArgumentList $args `
    -WorkingDirectory $CapsuleRepoRoot `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 2

if ($proc.HasExited) {
    exit $proc.ExitCode
}

exit 0
