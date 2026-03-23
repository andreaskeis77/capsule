# Observability and Diagnostics

This repo now standardizes operational diagnostics around a few stable artifact types:

- `docs/_ops/quality_gates/run_<timestamp>/summary.json|md`
- `docs/_ops/quality_gates/run_<timestamp>/diagnosis.json|md`
- `docs/_ops/releases/<release>_<timestamp>/release_evidence.json|md`
- `docs/_ops/report_index/ops_index_<timestamp>.json|md`

## Quality gate diagnosis

Every `tools/run_quality_gates.py` run now emits a diagnosis layer in addition to the step logs and summaries.

Use:

```powershell
python .\tools\quality_gate_diagnose.py .\docs\_ops\quality_gates\run_YYYYMMDD-HHMMSS
```

The diagnosis classifies common failure modes such as:

- PowerShell execution policy blocks
- encoding problems
- pytest assertion failures
- runtime smoke failures
- scanner findings

## Ops report index

To build a compact index over recent gate runs and release evidence:

```powershell
python .\tools\ops_report_index.py
```

This writes both JSON and Markdown into `docs/_ops/report_index/`.

## Run registry report

`tools/runs_report.py` now supports `--markdown` in addition to the existing text and JSON output.

Example:

```powershell
python .\tools\runs_report.py --since-hours 48 --markdown
```

## Task runner shortcuts

The standardized local entrypoint supports:

```powershell
python .\tools\task_runner.py diagnose-gates --latest-run run_YYYYMMDD-HHMMSS
python .\tools\task_runner.py ops-index
```

These commands stay repo-relative and Windows-friendly.
