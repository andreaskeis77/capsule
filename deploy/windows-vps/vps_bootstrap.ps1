param(
    [string]$SettingsPath = "$PSScriptRoot\vps-settings.ps1"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SettingsPath)) {
    throw "Settings file not found: $SettingsPath. Copy example.vps-settings.ps1 to vps-settings.ps1 first."
}

. $SettingsPath

if (-not (Test-Path $CapsuleRepoRoot)) {
    throw "Repo root not found: $CapsuleRepoRoot"
}

Set-Location $CapsuleRepoRoot

if (-not (Test-Path $CapsulePythonExe)) {
    $pythonLauncher = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonLauncher) {
        throw "No Python found. Install Python 3.12+ on the VPS first."
    }
    & $pythonLauncher.Source -m venv .venv
}

$python = Join-Path $CapsuleRepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Virtualenv python missing: $python"
}

New-Item -ItemType Directory -Force -Path $CapsuleLogsDir | Out-Null

& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt
if (Test-Path ".\requirements-dev.txt") {
    & $python -m pip install -r requirements-dev.txt
}

$domainLine = ""
if ($NgrokDomain -and $NgrokDomain.Trim()) {
    $domainLine = "domain: $NgrokDomain"
}
$template = Get-Content (Join-Path $PSScriptRoot "ngrok.template.yml") -Raw
$template = $template.Replace("__NGROK_AUTHTOKEN__", $NgrokAuthtoken)
$template = $template.Replace("    __DOMAIN_LINE__", $(if ($domainLine) { "    $domainLine" } else { "" }))
Set-Content -Path $NgrokConfigPath -Value $template -Encoding UTF8

Write-Host "[OK] VPS bootstrap finished."
Write-Host "Repo root: $CapsuleRepoRoot"
Write-Host "Python:    $python"
Write-Host "ngrok cfg: $NgrokConfigPath"
