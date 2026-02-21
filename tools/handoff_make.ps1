# tools/handoff_make.ps1
# Wardrobe Studio - One-command Handoff (PS 5.1 compatible)
# - Ensures venv python is used
# - Starts server if not running
# - Waits for readiness
# - Runs python master: tools/handoff_make.py
# - Optionally stops server it started
#
# Usage:
#   .\tools\handoff_make.ps1
#   .\tools\handoff_make.ps1 -User karen -Ids "112,101,110" -StopServer
#   .\tools\handoff_make.ps1 -BaseUrl "http://127.0.0.1:5002" -Port 5002
#
[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path ".").Path,
    [string]$BaseUrl = "http://127.0.0.1:5002",
    [int]$Port = 5002,
    [string]$User = "karen",
    [string]$Ids = "112,101,110",
    [int]$TimeoutSec = 35,
    [switch]$StopServer
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err ($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

function Test-Url200([string]$url) {
    try {
        $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 8 -Uri $url
        return ($r.StatusCode -eq 200)
    } catch {
        return $false
    }
}

function Wait-Ready([string]$base, [int]$timeout) {
    $deadline = (Get-Date).AddSeconds($timeout)
    $h1 = "$base/healthz"
    $h2 = "$base/api/v2/health"

    while ((Get-Date) -lt $deadline) {
        $ok1 = Test-Url200 $h1
        $ok2 = Test-Url200 $h2
        if ($ok1 -and $ok2) { return $true }
        Start-Sleep -Milliseconds 650
    }
    return $false
}

function Find-ListeningPid([int]$port) {
    try {
        $c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop | Select-Object -First 1
        if ($null -ne $c) { return [int]$c.OwningProcess }
    } catch { }
    return $null
}

# --- Resolve paths ---
Set-Location $RepoRoot
$venvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    throw "venv python not found: $venvPy"
}

$handoffPy = Join-Path $RepoRoot "tools\handoff_make.py"
if (-not (Test-Path $handoffPy)) {
    throw "Missing tools\handoff_make.py (python master). Create it first."
}

# --- Is server already running? ---
$existingPid = Find-ListeningPid $Port
$startedPid = $null

if ($existingPid) {
    Write-Info ("Server already listening on port {0} (PID={1}). Will reuse." -f $Port, $existingPid)
} else {
    Write-Info ("No listener on port {0}. Starting server..." -f $Port)

    # Start server (no new window), capture process object
    $serverArgs = @("-m", "src.server_entry")
    $p = Start-Process -FilePath $venvPy -ArgumentList $serverArgs -PassThru -WorkingDirectory $RepoRoot -WindowStyle Hidden
    $startedPid = $p.Id
    Write-Info ("Started server PID={0}. Waiting for readiness..." -f $startedPid)

    $ready = Wait-Ready $BaseUrl $TimeoutSec
    if (-not $ready) {
        Write-Err "Server did not become ready in time."
        Write-Err "Try opening $BaseUrl/healthz and check logs/server.err.log"
        if ($startedPid) {
            try { Stop-Process -Id $startedPid -Force -ErrorAction SilentlyContinue } catch { }
        }
        exit 2
    }
    Write-Info "Server is ready."
}

# --- Run Python handoff master ---
Write-Info "Running handoff_make.py..."
& $venvPy $handoffPy --base $BaseUrl --user $User --ids $Ids
$rc = $LASTEXITCODE
Write-Info ("handoff_make.py exit code={0}" -f $rc)

# --- Stop server if requested AND we started it ---
if ($StopServer -and $startedPid) {
    Write-Info ("Stopping server we started (PID={0})..." -f $startedPid)
    try { Stop-Process -Id $startedPid -Force -ErrorAction Stop } catch { Write-Warn "Could not stop PID=$startedPid" }
} elseif ($StopServer -and -not $startedPid) {
    Write-Warn "StopServer requested, but server was already running before. Not stopping it."
}

exit $rc