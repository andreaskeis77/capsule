# ADR-0009 – GitHub CI Required Checks

## Status
Accepted

## Context
The repository now has stable local quality gates (`compileall`, `ruff_critical`, `pytest`,
`secret_scan_tracked`, `live_smoke`), but the public GitHub repository still has no visible
workflow layer. That means robustness depends on local discipline instead of repository-enforced
checks.

## Decision
Introduce a canonical GitHub CI layer with two workflows:

1. `quality-gates.yml`
   - runs on `push` to `main`
   - runs on every `pull_request`
   - supports `workflow_dispatch`
   - installs both runtime and dev dependencies
   - executes `python ./tools/run_quality_gates.py --start-server`
   - uploads `docs/_ops/quality_gates/` as build artifacts
   - emits a compact markdown summary into the GitHub job summary

2. `ops-nightly-health.yml`
   - runs on a nightly `schedule`
   - supports `workflow_dispatch`
   - executes the same quality gates
   - additionally runs `project_audit_dump.py` and `repo_metrics_bold.py`
   - uploads ops artifacts for inspection

## Consequences
### Positive
- Push and PR safety move from “local convention” to “repository-enforced”.
- CI artifacts mirror the local artifact model instead of inventing a second reporting path.
- Nightly health runs provide a lightweight operational pulse without changing the production code path.

### Negative
- CI runtime increases because live smoke starts the server in CI.
- Failures in build infrastructure become visible earlier and more often.

## Alternatives Considered
- Only one workflow for everything: rejected because nightly ops/reporting should not slow every PR.
- Lint/tests only, without live smoke: rejected because the manifest prefers proof over assumption on critical paths.
- Coverage gating in this tranche: deferred until coverage is made canonical in the repo.

## Rollback / Exit Strategy
If CI noise becomes excessive:
1. keep `quality-gates.yml` as the non-negotiable path,
2. disable only the nightly workflow,
3. revisit artifact scope or timeout values via a new ADR.
