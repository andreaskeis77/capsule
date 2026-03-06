# Phase 0 Actions

Repository: `C:\CapsuleWardrobeRAG`  
Branch: `main`  
HEAD: `50097deaf4a87111faf10829f06c2e4aa3feab67`  
Scan mode: `tracked`

## Immediate Actions

1. **Keep coverage in the canonical metrics run.**
2. **Radon is available. Keep it enabled in the canonical run.**
3. **No tracked backup files were detected.**
4. **No tracked generated/export artifacts were detected.**

## Tracked Backup Files

- None

## Tracked Generated / Export Candidates

- None

## Engineering Hotspots To Watch

| File | Role | Code LOC | Churn | Risk | Hotspot |
| --- | --- | --- | --- | --- | --- |
| `src/api_v2.py` | application | 929 | 1946 | 83.77 | 132689.65 |
| `src/web_dashboard.py` | application | 464 | 1125 | 75.80 | 69468.27 |
| `src/ingest_wardrobe.py` | application | 565 | 1106 | 79.60 | 59641.88 |
| `src/ontology_runtime.py` | application | 385 | 465 | 82.80 | 47268.73 |
| `src/category_map.py` | application | 273 | 364 | 63.08 | 39307.83 |
| `tools/project_audit_dump.py` | tooling | 350 | 446 | 56.18 | 19942.92 |
| `src/run_registry.py` | application | 311 | 407 | 55.52 | 15727.82 |
| `src/db_schema.py` | application | 154 | 285 | 34.40 | 13897.78 |
| `tools/secret_scan.py` | tooling | 230 | 288 | 45.10 | 13693.87 |
| `tests/test_api_v2_crud.py` | test | 169 | 417 | 26.69 | 12799.53 |

## Suggested Commands

```powershell
.\.venv\Scripts\Activate.ps1
pip install radon coverage pytest pytest-cov
python .	oolsepo_metrics_bold.py . --scan-mode tracked --run-tests --pytest-target tests --coverage-target src
```

