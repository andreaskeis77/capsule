# tools/handoff_snapshot.ps1
# PowerShell 5.1 compatible snapshot generator
[CmdletBinding()]
param(
    [switch]$IncludeLogs,
    [int]$LogTail = 120
)

$ErrorActionPreference = 'Stop'

# ---------- helpers ----------
$Out = New-Object System.Collections.Generic.List[string]

function Add-Line([string]$s) {
    $script:Out.Add($s) | Out-Null
}

function Add-Section([string]$title) {
    Add-Line ''
    Add-Line ('## ' + $title)
    Add-Line ''
}

function Add-CodeBlock([string]$text) {
    Add-Line '```'
    if ([string]::IsNullOrWhiteSpace($text)) {
        Add-Line '_(no output)_'
    } else {
        Add-Line ($text.TrimEnd())
    }
    Add-Line '```'
}

function Run-Cmd([string]$title, [scriptblock]$cmd) {
    Add-Section $title
    try {
        $r = & $cmd 2>&1 | Out-String
        Add-CodeBlock $r
    } catch {
        Add-CodeBlock ('ERROR: ' + $_.Exception.Message)
    }
}

function Add-Tree([string]$pathToTree) {
    Add-Section ('tree ' + $pathToTree)
    if (-not (Test-Path $pathToTree)) {
        Add-Line '_(path not found)_'
        return
    }
    try {
        $r = tree /a /f $pathToTree 2>&1 | Out-String
        Add-CodeBlock $r
    } catch {
        Add-CodeBlock ('ERROR: ' + $_.Exception.Message)
    }
}

# ---------- paths ----------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir '..')).Path

$SnapshotDir  = Join-Path $Root 'docs\_snapshot'
$SnapshotFile = Join-Path $SnapshotDir 'latest.md'
New-Item -ItemType Directory -Force -Path $SnapshotDir | Out-Null

# ---------- header ----------
$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Add-Line '# Wardrobe Studio - Chat Handoff Snapshot'
Add-Line ''
Add-Line ('- Generated: ' + $ts)
Add-Line ('- Root: ' + $Root)
Add-Line ''

Add-Section 'Key URLs'
Add-Line '- Local base: http://127.0.0.1:5002'
Add-Line '- Dashboard: http://127.0.0.1:5002/?user=karen'
Add-Line '- Health: http://127.0.0.1:5002/healthz'
Add-Line '- API v2 health: http://127.0.0.1:5002/api/v2/health'
Add-Line '- ngrok fixed domain: https://wardrobe.ngrok-app.com.ngrok.app'

# ---------- git ----------
Push-Location $Root
Run-Cmd 'git status' { git status }
Run-Cmd 'git log (last 10)' { git log --oneline -n 10 }
Run-Cmd 'git branch' { git branch }
Pop-Location

# ---------- python ----------
Run-Cmd 'python --version' { python --version }
Run-Cmd 'where python' { where python }

$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
if (Test-Path $VenvPython) {
    Run-Cmd '.venv python --version' { & $VenvPython --version }

    Add-Section '.venv pip freeze (count + first 25)'
    try {
        $freeze = & $VenvPython -m pip freeze 2>&1
        $count = ($freeze | Measure-Object).Count
        $head  = $freeze | Select-Object -First 25
        Add-CodeBlock ('COUNT=' + $count + "`r`n`r`n" + ($head -join "`r`n"))
    } catch {
        Add-CodeBlock ('ERROR: ' + $_.Exception.Message)
    }
} else {
    Add-Section '.venv'
    Add-Line '_(no .venv\Scripts\python.exe found)_'
}

# ---------- structure ----------
Add-Line ''
Add-Line '# Repo Structure'
Add-Tree (Join-Path $Root 'src')
Add-Tree (Join-Path $Root 'templates')
Add-Tree (Join-Path $Root 'ontology')
Add-Tree (Join-Path $Root 'tools')

# ---------- requirements ----------
$Req = Join-Path $Root 'requirements.txt'
if (Test-Path $Req) {
    Run-Cmd 'requirements.txt (first 40 lines)' { Get-Content $Req -TotalCount 40 }
} else {
    Add-Section 'requirements.txt'
    Add-Line '_(missing)_'
}

# ---------- optional logs ----------
if ($IncludeLogs) {
    Add-Line ''
    Add-Line '# Logs (tail)'
    $LogDir = Join-Path $Root 'logs'
    if (Test-Path $LogDir) {
        $Startup   = Join-Path $LogDir 'startup.log'
        $ServerErr = Join-Path $LogDir 'server.err.log'
        $NgrokErr  = Join-Path $LogDir 'ngrok.err.log'

        if (Test-Path $Startup)   { Run-Cmd 'logs/startup.log (tail)'    { Get-Content $Startup -Tail $LogTail } }
        if (Test-Path $ServerErr) { Run-Cmd 'logs/server.err.log (tail)' { Get-Content $ServerErr -Tail $LogTail } }
        if (Test-Path $NgrokErr)  { Run-Cmd 'logs/ngrok.err.log (tail)'  { Get-Content $NgrokErr -Tail $LogTail } }
    } else {
        Add-Section 'logs/'
        Add-Line '_(no logs directory)_'
    }
}

# ---------- write ----------
$Out | Set-Content -Encoding UTF8 -Path $SnapshotFile
Write-Host ('OK: wrote snapshot -> ' + $SnapshotFile)
Write-Host 'Tip: run with logs:  .\tools\handoff_snapshot.ps1 -IncludeLogs'
