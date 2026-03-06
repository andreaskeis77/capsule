# repo_metrics_bold

Current canonical version of the repository metrics analyzer.

This version is tuned for **Phase 0 / repo hygiene + measurement hardening**.
It keeps the script filename stable (`repo_metrics_bold.py`) so you can overwrite the old file in place.

## What this version adds

- **Git-first canonical snapshots**
  `auto` still resolves to `tracked` when `.git` exists.

- **Phase-0 policy findings**
  The run now emits findings for:
  - tracked backup-like files (`*.bak`, `*.tmp`, `*.orig`, `*.rej`, `*~`)
  - tracked staging/snapshot paths
  - tracked generated/export-style artifacts such as `*export*.json`

- **Cleanup candidate output**
  Additional artifact:
  - `cleanup_candidates.csv`

- **Phase-0 action report**
  Additional artifact:
  - `PHASE0_ACTIONS.md`

- **BOM-safe Python parsing**
  Python files are read with `utf-8-sig`, avoiding false parse failures from leading BOM bytes.

- **Role-weighted risk / hotspot scoring**
  Logs, assets and non-engineering noise do not dominate engineering risk.

## Canonical usage

From the repo root:

```powershell
cd C:\CapsuleWardrobeRAG
.\.venv\Scripts\Activate.ps1
python .\tools\repo_metrics_bold.py . --scan-mode tracked
```

Recommended strong run with coverage + radon available:

```powershell
pip install radon coverage pytest pytest-cov
python .\tools\repo_metrics_bold.py . --scan-mode tracked --run-tests --pytest-target tests --coverage-target src
```

Repo + current untracked engineering work:

```powershell
python .\tools\repo_metrics_bold.py . --scan-mode git-visible
```

Full workspace audit:

```powershell
python .\tools\repo_metrics_bold.py . --scan-mode filesystem
```

## Output artifacts

The script writes a timestamped folder under:

```text
docs\_metrics\repo_metrics_v2_<timestamp>\
```

Main outputs:

- `repo_metrics_v2.json`
- `REPORT_v2.md`
- `PHASE0_ACTIONS.md`
- `files.csv`
- `functions.csv`
- `languages.csv`
- `roles.csv`
- `directories.csv`
- `scopes.csv`
- `hotspots.csv`
- `risky_files.csv`
- `duplicates_exact.csv`
- `duplicates_shadow.csv`
- `issues.csv`
- `cleanup_candidates.csv`

## Recommended workflow

1. Use `tracked` as the canonical repo baseline.
2. Run at least one coverage-backed snapshot before major refactoring.
3. Review `cleanup_candidates.csv` and `PHASE0_ACTIONS.md` before the next cleanup or architecture pass.
4. Keep overwriting the same script filename instead of version-suffixed copies.
