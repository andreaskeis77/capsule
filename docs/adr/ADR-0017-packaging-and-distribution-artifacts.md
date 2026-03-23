# ADR-0017: Packaging and Distribution Artifacts

## Status
Accepted

## Context
The repository already has stronger quality gates, release evidence, and governance.  
What was still missing was a versioned packaging contract and a repeatable way to emit release-oriented distribution metadata.

## Decision
Introduce:
- `pyproject.toml`
- `MANIFEST.in`
- `tools/package_distribution.py`
- `tools/release_artifact_bundle.py`
- packaging/release artifact tests
- a dedicated GitHub workflow for packaging contracts

## Consequences
- Packaging expectations are explicit and testable.
- Release evidence can now include packaging metadata.
- The repository becomes easier to distribute, archive, and hand off without implying public package publication.
