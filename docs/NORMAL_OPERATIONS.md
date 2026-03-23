# Normal Operations

After tranche completion, the repository should move into a steady operating mode.

## Daily path

1. Run local quality gates before meaningful changes.
2. Use the standardized task entrypoints for recurring actions.
3. Keep release evidence aligned with successful gate runs.
4. Use the readiness report when preparing a handoff or release.

## Recommended commands

```powershell
python .\tools\run_quality_gates.py
python .\tools\final_repo_baseline.py
python .\tools\final_readiness_report.py
python .\tools\repo_status_snapshot.py
```

## Handoff / release preparation

Before a handoff or release candidate:

- regenerate baseline
- regenerate readiness report
- regenerate repo status snapshot
- confirm the latest successful quality-gate run
- confirm release evidence exists or document why it does not
