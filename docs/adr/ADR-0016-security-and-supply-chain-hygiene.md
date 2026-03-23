# ADR-0016: Security and supply-chain hygiene

## Status
Accepted

## Context

The repository already has local quality gates, a tracked secret scan, release evidence and branch-protection contracts. The next missing layer is lightweight, repeatable security hygiene evidence that covers dependency pinning, expected repository controls and nightly supply-chain visibility.

## Decision

We add:

- `tools/security_inventory.py` for control inventory and dependency pinning visibility
- `tools/security_hygiene_report.py` for higher-level hygiene status based on inventory and latest successful quality gates
- `.github/dependabot.yml` for dependency drift visibility
- `.github/workflows/security-hygiene-nightly.yml` for scheduled evidence generation
- `docs/SECURITY.md` as the operational security baseline

## Consequences

Positive:

- security posture becomes easier to inspect and hand off
- dependency pinning and missing repo controls become visible without external services
- nightly evidence complements, but does not replace, local quality gates

Trade-offs:

- another scheduled workflow must be reviewed and maintained
- the generated reports are evidence artifacts, not deep security analysis
