\
    param(
      [switch]$ReuseServer,
      [switch]$SkipLiveSmoke,
      [switch]$SkipCompileAll,
      [switch]$SkipRuff,
      [switch]$SkipPytest,
      [switch]$SkipSecretScan,
      [string]$BaseUrl = "",
      [string]$Host = "127.0.0.1",
      [int]$Port = 5012,
      [string]$User = "karen",
      [string]$Ids = "112,101,110"
    )

    $ErrorActionPreference = "Stop"

    $RepoRoot = Split-Path -Parent $PSScriptRoot
    $Py = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $Py)) {
      $Py = "python"
    }

    $Args = @(
      (Join-Path $RepoRoot "tools\run_quality_gates.py"),
      "--host", $Host,
      "--port", "$Port",
      "--user", $User,
      "--ids", $Ids
    )

    if ($BaseUrl) {
      $Args += @("--base-url", $BaseUrl)
    }

    if ($ReuseServer) {
      $Args += "--reuse-server"
    } elseif (-not $SkipLiveSmoke) {
      $Args += "--start-server"
    } else {
      $Args += "--skip-live-smoke"
    }

    if ($SkipCompileAll) { $Args += "--skip-compileall" }
    if ($SkipRuff) { $Args += "--skip-ruff" }
    if ($SkipPytest) { $Args += "--skip-pytest" }
    if ($SkipSecretScan) { $Args += "--skip-secret-scan" }

    Push-Location $RepoRoot
    try {
      & $Py @Args
      exit $LASTEXITCODE
    }
    finally {
      Pop-Location
    }
