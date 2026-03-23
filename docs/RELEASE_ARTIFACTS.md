# Release Artifacts

Release evidence and packaging evidence should travel together.

## Standard outputs
- `docs/_ops/quality_gates/run_<timestamp>/summary.json`
- `docs/_ops/packaging/distribution_payload.json`
- `docs/_ops/release_artifacts/<release-id>.json`

## Rule
A release artifact manifest should point to the latest successful quality-gate run using repo-relative POSIX-style paths.
