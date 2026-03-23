# Apply Safe Workspace Cleanup

This safe variant intentionally keeps these files in place:
- `capsule.ps1`
- `requirements-dev.txt`

## Steps

1. Copy `tools/workspace_cleanup_apply_safe.py` into `tools/`.
2. Dry-run:
   `python .\tools\workspace_cleanup_apply_safe.py`
3. Review:
   `docs\_ops\workspace_cleanup\run_<timestamp>\cleanup_summary.md`
4. Apply:
   `python .\tools\workspace_cleanup_apply_safe.py --apply`
