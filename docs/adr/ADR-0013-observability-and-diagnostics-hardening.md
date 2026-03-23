# ADR-0013: Observability and Diagnostics Hardening

## Status
Accepted

## Context
The repo already had strong operational scripts, but diagnostics were still distributed across raw logs, ad-hoc summaries and individual tool outputs. This made failure triage slower than necessary, especially when local quality gates were already mandatory and release evidence depended on those same artifacts.

## Decision
We add a standard diagnostics layer:

- shared report helpers in `tools/reporting_common.py`
- structured failure classification in `tools/quality_gate_diagnose.py`
- automatic `diagnosis.json` and `diagnosis.md` generation from `tools/run_quality_gates.py`
- a consolidated artifact index in `tools/ops_report_index.py`
- markdown output support in `tools/runs_report.py`
- standardized local task entrypoints for diagnostics and ops indexing

## Consequences
Positive:
- faster diagnosis of local gate failures
- more consistent operational artifacts
- easier handoff and release evidence review
- fewer path-format inconsistencies across Windows environments

Trade-offs:
- more generated files under `docs/_ops/`
- another layer of contract tests to maintain
