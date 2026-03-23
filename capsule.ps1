$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) {
    $py = 'python'
}
& $py (Join-Path $root 'tools\task_runner.py') @args
exit $LASTEXITCODE
