param(
    [ValidateSet('auto','tracked','git-visible','filesystem')]
    [string]$Mode = 'tracked',

    [switch]$WithTests,

    [string]$PytestTarget = 'tests',

    [string]$CoverageTarget = 'src',

    [string]$CoverageJson = '',

    [switch]$InstallOptionalDeps,

    [string]$OutDir = ''
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$PythonExe = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found at $PythonExe"
}

Set-Location $RepoRoot

if ($InstallOptionalDeps) {
    & $PythonExe -m pip install radon coverage pytest pytest-cov
}

$args = @(
    '.\tools\repo_metrics_bold.py',
    '.',
    '--scan-mode', $Mode
)

if ($WithTests) {
    $args += @('--run-tests', '--pytest-target', $PytestTarget, '--coverage-target', $CoverageTarget)
}

if ($CoverageJson -ne '') {
    $args += @('--coverage-json', $CoverageJson)
}

if ($OutDir -ne '') {
    $args += @('--out-dir', $OutDir)
}

Write-Host "Running repo metrics from $RepoRoot"
Write-Host "Mode: $Mode"
if ($WithTests) {
    Write-Host "Coverage run: enabled"
}

& $PythonExe @args
if ($LASTEXITCODE -ne 0) {
    throw "repo_metrics_bold.py failed with exit code $LASTEXITCODE"
}
