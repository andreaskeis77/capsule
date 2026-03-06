# Phase 0 Cleanup Report

Repository: `C:\CapsuleWardrobeRAG`

## Summary

- Tracked backup-like files: **0**
- Tracked generated/export candidates: **5**
- UTF-8 BOM text files: **12**

## Generated / Export Candidates

Review manually before removal. Keep only if they are canonical source data.

- `PROJECT_HANDOFF_WardrobeStudio_2026-01-29.md`
- `docs\CHAT_HANDOFF_TEMPLATE.md`
- `docs\HANDOFF_MANIFEST.md`
- `docs\HANDOFF_RUNTIME_STATE.md`
- `wardrobe_export.json`

Possible command for non-canonical artifacts:

- `git rm --cached "PROJECT_HANDOFF_WardrobeStudio_2026-01-29.md"`
- `git rm --cached "docs\CHAT_HANDOFF_TEMPLATE.md"`
- `git rm --cached "docs\HANDOFF_MANIFEST.md"`
- `git rm --cached "docs\HANDOFF_RUNTIME_STATE.md"`
- `git rm --cached "wardrobe_export.json"`

## UTF-8 BOM Files

These files start with a BOM. For Python files this can create noisy parsing/tooling issues.

- `docs\ENGINEERING_GUIDELINES.md`
- `requirements.txt`
- `src\api_main.py`
- `src\db_schema.py`
- `src\web_dashboard.py`
- `templates\admin_item_edit.html`
- `templates\index.html`
- `templates\item_detail.html`
- `tests\test_admin_item_edit_context_select.py`
- `tests\test_dashboard_index_filters.py`
- `tests\test_db_schema_migration.py`
- `tools\handoff_snapshot.ps1`

Dry run fix:

- `python .\tools\phase0_cleanup.py .`

Apply BOM removal:

- `python .\tools\phase0_cleanup.py . --strip-bom`

## Recommended Order

1. Remove tracked backup-like files.
2. Decide whether tracked export/generated artifacts are canonical or should leave Git.
3. Strip BOM from tracked text files, then rerun metrics and tests.
