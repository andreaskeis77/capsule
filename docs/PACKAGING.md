# Packaging

This repository now carries a minimal packaging contract for reproducible distribution metadata.

## Files
- `pyproject.toml` defines build metadata and optional developer dependencies.
- `MANIFEST.in` defines the source distribution include/exclude rules.
- `tools/package_distribution.py` emits a JSON payload with packaging metadata and file inventory.
- `tools/release_artifact_bundle.py` creates a release artifact manifest tied to the latest successful quality-gate run.

## Intent
This is not a claim that the repository is published to PyPI.  
The purpose is to make packaging and release artifacts explicit, testable, and reviewable.
