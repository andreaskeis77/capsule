# Developer Workflow

## Standard local entrypoints

The repository now exposes one canonical local command surface for day-to-day work:

- `capsule.cmd quality-gates`
- `capsule.cmd test`
- `capsule.cmd server`
- `capsule.cmd handoff`
- `capsule.cmd snapshot`
- `capsule.cmd audit`
- `capsule.cmd secret-scan --mode tracked`
- `capsule.cmd release-evidence --release-id <id>`

The command wrapper resolves `.venv\Scripts\python.exe` first and falls back to `python` only if the local virtual environment is absent.

## VS Code integration

`.vscode/tasks.json` mirrors the canonical entrypoints so the same commands are available from the VS Code task runner without inventing a second workflow.

## Design intent

This tranche does not replace the existing operational scripts. It standardizes how developers invoke them so local usage, onboarding, and release/handoff routines follow one predictable command surface.
