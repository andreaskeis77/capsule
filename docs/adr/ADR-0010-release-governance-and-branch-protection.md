# ADR-0010: Release governance and branch-protection contract

## Status
Accepted

## Context
Local quality gates are now reliable, but green local runs alone do not create a durable merge and release contract.
The repository needs a repo-native governance layer that makes required checks explicit, standardizes pull request evidence,
and turns release evidence into a reproducible artifact rather than an informal comment.

## Decision
We introduce the following repository-governed contract:

1. A versioned branch-protection contract file at `.github/branch-protection.required-checks.json`.
2. A PR template that requires local gate evidence and governance confirmation.
3. A release evidence generator that consumes the most recent successful quality-gates run and writes a stable evidence bundle.
4. Tests that fail when the documented branch-protection contract becomes structurally invalid or when release evidence output drifts.

## Consequences
### Positive
- Merge expectations become explicit and reviewable in the repository.
- Release evidence is generated from artifacts, not memory.
- Governance drift becomes detectable in CI and locally.

### Negative
- There is one more repository contract to maintain when workflow names change.
- GitHub branch protection still must be configured in the GitHub UI or API; the repository file is the source-of-truth contract, not the enforcement mechanism itself.

## Operational rule
Merge to `main` should only happen when:
- local `python .\tools\run_quality_gates.py` is green,
- GitHub required checks are green,
- PR template evidence is completed,
- branch protection settings match `.github/branch-protection.required-checks.json`.
