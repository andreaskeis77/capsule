# Workspace Cleanup Plan

This cleanup script is intentionally conservative.

## What it does

Default mode is **dry-run**. It reads the newest inventory under:

- `docs/_ops/workspace_inventory/run_<timestamp>/cleanup_candidates.csv`

Then it creates a cleanup plan and logs under:

- `docs/_ops/workspace_cleanup/run_<timestamp>/`

It will only plan/apply the following classes:

- archive root-level untracked work notes and temporary helper files such as `APPLY_TRANCHE_*.md`
- archive `docs/_metrics`
- delete `_release_staging`
- delete obvious replaceable log files such as `logs/wardrobe.log`
- delete `.env.bak`
- delete `capsule_server_seed.zip`

It does **not** touch:

- `src/`, `tests/`, `tools/`, `ontology/`, `templates/`
- `02_wardrobe_images`, `03_database`, `04_user_data`
- `docs/_ops`, `docs/_snapshot`
- tracked documentation under `docs/`
- `.env`

## Run

Dry-run first:

```powershell
cd C:\CapsuleWardrobeRAG
.\.venv\Scripts\Activate.ps1
python .\tools\workspace_cleanup_apply.py
```

Apply the plan:

```powershell
cd C:\CapsuleWardrobeRAG
.\.venv\Scripts\Activate.ps1
python .\tools\workspace_cleanup_apply.py --apply
```

## Output

- `cleanup_summary.md`
- `cleanup_plan.csv`
- `cleanup_execution.json`
- `protected_items.json`
