# Release Process

## Purpose
This process turns a green codebase into a reproducible release with evidence.

## Preconditions
1. Local quality gates are green.
2. GitHub required checks are green.
3. No unresolved review conversation remains.
4. Release-impacting changes are covered by an ADR if architecture or governance changed.

## Release steps
1. Update or confirm the target version tag / release identifier.
2. Run:
   `python .\tools\release_evidence.py`
3. Review the generated release evidence bundle under `docs\_ops\releases\release_<timestamp>`.
4. Confirm the evidence contains:
   - gate status = OK
   - latest run directory
   - commit id, if available
   - workflow / required-check contract snapshot
5. Merge only after the evidence bundle is written and reviewed.
6. Create tag / release in GitHub using the same release identifier referenced in the evidence.

## Required human checks
- No accidental `.env`, tokens, or generated noise slipped in.
- Handoff / snapshot expectations are still met.
- Any DB or schema-affecting change includes migration compatibility evidence.
