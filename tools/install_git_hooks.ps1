\
    $ErrorActionPreference = "Stop"

    $RepoRoot = Split-Path -Parent $PSScriptRoot
    $Source = Join-Path $RepoRoot "tools\hooks\pre-commit"
    $TargetDir = Join-Path $RepoRoot ".git\hooks"
    $Target = Join-Path $TargetDir "pre-commit"

    if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
      throw "No .git directory found under $RepoRoot"
    }

    if (-not (Test-Path $Source)) {
      throw "Hook source not found: $Source"
    }

    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    Copy-Item -Force $Source $Target

    Write-Host "[OK] Installed hook: $Target"
    Write-Host "[INFO] Ensure requirements-dev.txt is installed so ruff is available in your venv."
