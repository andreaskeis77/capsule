# SECURITY

## Scope

This repository is designed for local-first development with explicit operational evidence. Security controls here are intentionally pragmatic: prevent accidental secret exposure, keep the Python supply chain pinned, and make release readiness observable.

## Baseline controls

- `.env` stays local and unversioned.
- `.env.example` documents required runtime configuration without carrying live secrets.
- `tools/secret_scan.py` is part of the tracked quality gates.
- Branch protection is documented in `.github/branch-protection.required-checks.json`.
- Quality gates and release evidence are expected before merges and releases.

## Secret handling

- Never commit live credentials or production endpoints with embedded credentials.
- Keep local secrets only in `.env` or in the local execution environment.
- Rotate any credential immediately if it was ever committed or pasted into a tracked artifact.
- Treat screenshots, exported logs and copied request payloads as potentially sensitive.

## Dependency and workflow hygiene

- Keep Python dependencies pinned.
- Use Dependabot for routine drift visibility.
- Review GitHub Actions changes as supply-chain relevant changes.
- Prefer first-party or well-established GitHub Actions and pin major versions intentionally.

## Security evidence

Nightly or on-demand repository hygiene should produce these artifacts under `docs/_ops/security/`:

- `security_inventory_latest.json`
- `security_inventory_latest.md`
- `security_hygiene_latest.json`
- `security_hygiene_latest.md`

These artifacts are not a replacement for penetration testing. They are the repo's lightweight, repeatable security readiness evidence.
