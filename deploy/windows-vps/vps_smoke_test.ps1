param(
    [string]$SettingsPath = "$PSScriptRoot\vps-settings.ps1"
)

$ErrorActionPreference = "Stop"
. $SettingsPath

Write-Host "[INFO] Local health: $CapsuleLocalHealthUrl"
$local = Invoke-WebRequest -Uri $CapsuleLocalHealthUrl -UseBasicParsing -TimeoutSec 15
Write-Host "[OK] Local health status code: $($local.StatusCode)"

if ($CapsulePublicBaseUrl -and $CapsulePublicBaseUrl.Trim()) {
    $publicHealth = "$CapsulePublicBaseUrl/healthz"
    Write-Host "[INFO] Public health: $publicHealth"
    $pub = Invoke-WebRequest -Uri $publicHealth -UseBasicParsing -TimeoutSec 20
    Write-Host "[OK] Public health status code: $($pub.StatusCode)"
}

Write-Host "[OK] Smoke test passed."

