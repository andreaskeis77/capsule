# ADR-0007 — Tooling / Ops Consolidation

## Status
Accepted

## Context
The repo already contains several operational scripts under `tools/`:
- handoff generation
- runtime dumps
- data snapshots
- run-registry reports
- secret scanning

Those scripts are useful, but they currently duplicate small but important mechanics:
- repo-root discovery / bootstrap for `src` imports
- timestamp generation
- SHA-256 helpers
- robust text reading
- safe artifact writing
- subprocess capture / truncation

The repo metrics report also marks tooling as a real maintainability surface, not noise. In particular, `tools/repo_metrics_bold.py`, `tools/project_audit_dump.py`, `tools/secret_scan.py` and `tools/handoff_make.py` are part of the operational risk picture. The engineering manifest also requires deterministic artifacts, strong observability and stable overwrite-in-place file naming. That makes shared ops helpers the right next consolidation move. 

## Decision
Introduce shared helper modules for tooling:
- `tools/ops_paths.py`
- `tools/ops_common.py`

Refactor selected operational scripts onto those helpers without changing their CLI contracts:
- `tools/handoff_make.py`
- `tools/handoff_make_run.py`
- `tools/project_data_snapshot.py`
- `tools/ontology_runtime_dump.py`
- `tools/runs_report.py`
- `tools/secret_scan.py`

## Consequences
Positive:
- less duplicate bootstrap / hashing / write logic
- more consistent artifact handling
- safer future refactors of audit/handoff tooling
- lower risk of drift between similar operational scripts

Trade-offs:
- `tools/` becomes more explicitly modular, so helper modules themselves become part of the stable surface
- direct script execution must support both `tools.*` imports and sibling fallback imports

## Non-goals
This tranche does **not** fully rewrite:
- `tools/project_audit_dump.py`
- `tools/repo_metrics_bold.py`
- PowerShell snapshot scripts

Those remain candidates for a later tranche once the Python helper layer has stabilized.
