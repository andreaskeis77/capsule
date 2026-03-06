# Repository Metrics Report v2

Generated: 2026-03-06T09:15:46+00:00  
Repository: `C:\CapsuleWardrobeRAG`  
Scan mode: `tracked`  
Branch: `main`  
HEAD: `50097deaf4a87111faf10829f06c2e4aa3feab67`  
Git commits: 47  
Coverage available: True  
Radon available in run: True

## Executive Summary

- Files scanned: **95**
- Git tracked files in repo: **95**
- Git-visible files: **157**
- Text files scanned: **91**
- Binary files scanned: **4**
- Engineering files: **63**
- Production files: **44**
- Python files: **50**
- Tracked code lines: **7548**
- Engineering code lines: **7391**
- Production code lines: **6449**
- Engineering comment density: **4.37%**
- Exact duplicate text groups: **0**
- Shadow duplicate pairs: **0**
- Quality issues emitted: **41**
- Tracked backup-like files: **0**
- Tracked generated/export candidates: **0**

## Scope Summary

| Scope | Files | Tracked | Code LOC | Doc lines | Comments | Binary | Churn | Avg risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_scanned | 95 | 95 | 7548 | 6134 | 344 | 4 | 19503 | 14.97 |
| docs_only | 24 | 24 | 0 | 6134 | 0 | 0 | 6929 | 0.94 |
| engineering_core | 63 | 63 | 7391 | 0 | 338 | 0 | 12390 | 22.16 |
| git_visible | 95 | 95 | 7548 | 6134 | 344 | 4 | 19503 | 14.97 |
| production_core | 44 | 44 | 6449 | 0 | 303 | 0 | 10847 | 27.17 |
| tests_only | 19 | 19 | 942 | 0 | 35 | 0 | 1543 | 10.55 |
| tracked_only | 95 | 95 | 7548 | 6134 | 344 | 4 | 19503 | 14.97 |
| workspace_noise | 4 | 4 | 0 | 0 | 0 | 4 | 0 | 0.00 |

## Repo Mix by Role

| Role | Files | Code LOC | Doc lines | Comments | Churn | Avg risk |
| --- | --- | --- | --- | --- | --- | --- |
| application | 22 | 3816 | 0 | 190 | 6892 | 32.99 |
| tooling | 13 | 1765 | 0 | 109 | 2239 | 28.08 |
| test | 19 | 942 | 0 | 35 | 1543 | 10.55 |
| template | 3 | 664 | 0 | 4 | 1468 | 28.79 |
| config | 6 | 204 | 0 | 0 | 248 | 3.06 |
| other | 4 | 157 | 0 | 6 | 184 | 0.85 |
| asset | 4 | 0 | 0 | 0 | 0 | 0.00 |
| documentation | 24 | 0 | 6134 | 0 | 6929 | 0.94 |

## Repo Mix by Language

| Language | Files | Code LOC | Comments | Doc lines | Churn |
| --- | --- | --- | --- | --- | --- |
| Python | 50 | 6267 | 305 | 0 | 10350 |
| HTML | 3 | 664 | 4 | 0 | 1468 |
| PowerShell | 3 | 238 | 29 | 0 | 304 |
| No Extension | 2 | 101 | 0 | 0 | 130 |
| YAML | 2 | 94 | 0 | 0 | 115 |
| Batch | 1 | 65 | 6 | 0 | 78 |
| JSON | 2 | 42 | 0 | 0 | 42 |
| EXAMPLE | 1 | 38 | 0 | 0 | 46 |
| SAMPLE | 1 | 18 | 0 | 0 | 20 |
| INI | 1 | 13 | 0 | 0 | 13 |
| CODE-WORKSPACE | 1 | 8 | 0 | 0 | 8 |
| JPG | 2 | 0 | 0 | 0 | 0 |
| Markdown | 22 | 0 | 0 | 6084 | 6895 |
| PNG | 2 | 0 | 0 | 0 | 0 |
| Text | 2 | 0 | 0 | 50 | 34 |

## Top-Level Directories

| Directory | Files | Code LOC | Doc lines | Churn | Avg risk | Avg hotspot |
| --- | --- | --- | --- | --- | --- | --- |
| src | 22 | 3816 | 0 | 6892 | 32.99 | 18406.36 |
| tools | 13 | 1765 | 0 | 2239 | 28.08 | 6450.83 |
| tests | 19 | 942 | 0 | 1543 | 10.55 | 1974.31 |
| templates | 3 | 664 | 0 | 1468 | 28.79 | 2884.43 |
| . | 16 | 225 | 695 | 1168 | 0.81 | 32.93 |
| ontology | 11 | 94 | 4827 | 5375 | 2.13 | 94.70 |
| 04_user_data | 2 | 42 | 0 | 42 | 2.50 | 34.88 |
| docs | 9 | 0 | 612 | 776 | 0.32 | 13.08 |

## Largest Engineering Files by Code LOC

| File | Lang | Role | Code LOC | Comments | Churn | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| src/api_v2.py | Python | application | 929 | 27 | 1946 | 83.77 |
| src/ingest_wardrobe.py | Python | application | 565 | 20 | 1106 | 79.60 |
| src/web_dashboard.py | Python | application | 464 | 23 | 1125 | 75.80 |
| src/ontology_runtime.py | Python | application | 385 | 12 | 465 | 82.80 |
| templates/index.html | HTML | template | 369 | 4 | 686 | 40.51 |
| tools/project_audit_dump.py | Python | tooling | 350 | 26 | 446 | 56.18 |
| src/run_registry.py | Python | application | 311 | 6 | 407 | 55.52 |
| src/category_map.py | Python | application | 273 | 38 | 364 | 63.08 |
| tools/secret_scan.py | Python | tooling | 230 | 9 | 288 | 45.10 |
| tools/ontology_runtime_dump.py | Python | tooling | 214 | 4 | 263 | 37.93 |
| tests/test_api_v2_crud.py | Python | test | 169 | 4 | 417 | 26.69 |
| tools/project_data_snapshot.py | Python | tooling | 169 | 7 | 218 | 33.07 |
| templates/admin_item_edit.html | HTML | template | 167 | 0 | 444 | 26.48 |
| tools/handoff_make.py | Python | tooling | 167 | 10 | 204 | 35.92 |
| src/api_main.py | Python | application | 157 | 9 | 320 | 29.14 |
| src/db_schema.py | Python | application | 154 | 9 | 285 | 34.40 |
| tools/ingest_recover.py | Python | tooling | 145 | 8 | 184 | 40.26 |
| templates/item_detail.html | HTML | template | 128 | 0 | 338 | 19.39 |
| tools/handoff_snapshot.ps1 | PowerShell | tooling | 118 | 11 | 149 | 19.08 |
| src/settings.py | Python | application | 97 | 13 | 239 | 18.41 |

## Top Hotspots (Engineering)

| File | Lang | Role | Hotspot | Churn | Avg CC | Radon MI | Approx MI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| src/api_v2.py | Python | application | 132689.65 | 1946 | 6.93 | 1.14 | 0.00 |
| src/web_dashboard.py | Python | application | 69468.27 | 1125 | 5.78 | 25.78 | 0.00 |
| src/ingest_wardrobe.py | Python | application | 59641.88 | 1106 | 5.10 | 23.81 | 0.00 |
| src/ontology_runtime.py | Python | application | 47268.73 | 465 | 11.75 | 12.13 | 0.00 |
| src/category_map.py | Python | application | 39307.83 | 364 | 12.14 | 40.58 | 8.35 |
| tools/project_audit_dump.py | Python | tooling | 19942.92 | 446 | 5.36 | 40.07 | 5.96 |
| src/run_registry.py | Python | application | 15727.82 | 407 | 3.90 | 33.38 | 7.72 |
| src/db_schema.py | Python | application | 13897.78 | 285 | 6 | 58.95 | 25.98 |
| tools/secret_scan.py | Python | tooling | 13693.87 | 288 | 6.11 | 40.42 | 14.63 |
| tests/test_api_v2_crud.py | Python | test | 12799.53 | 417 | 5.88 | 38.65 | 19.48 |
| tools/ingest_recover.py | Python | tooling | 11088.40 | 184 | 8 | 44.74 | 23.04 |
| tools/handoff_make.py | Python | tooling | 10240.97 | 204 | 6.50 | 53.55 | 21.85 |
| tools/ontology_runtime_dump.py | Python | tooling | 9028.55 | 263 | 3.80 | 49.00 | 17.09 |
| src/api_main.py | Python | application | 7816.96 | 320 | 2.33 | 60.16 | 24.26 |
| tools/project_data_snapshot.py | Python | tooling | 7471.12 | 218 | 4 | 52.49 | 19.85 |
| src/settings.py | Python | application | 4550.39 | 239 | 1.71 | 68.69 | 30.78 |
| templates/index.html | HTML | template | 4397.80 | 686 |  |  |  |
| tools/handoff_make_run.py | Python | tooling | 3920.35 | 131 | 4 | 55.79 | 30.69 |
| tools/project_sanity_check.py | Python | tooling | 3578.98 | 92 | 6 | 74.01 | 35.95 |
| tests/test_run_registry_redaction.py | Python | test | 3163.32 | 58 | 15 | 58.44 | 40.43 |

## Highest Risk Files (Engineering)

| File | Risk | Score | Code LOC | Churn | Coverage % | Flags |
| --- | --- | --- | --- | --- | --- | --- |
| src/api_v2.py | Critical | 83.77 | 929 | 1946 | 54.82 | large-file; low-maintainability; high-complexity-function; low-coverage; high-churn |
| src/ontology_runtime.py | Critical | 82.80 | 385 | 465 | 59.12 | low-maintainability; high-complexity-function; low-coverage; high-churn |
| src/ingest_wardrobe.py | Critical | 79.60 | 565 | 1106 | 0.00 | large-file; low-maintainability; high-complexity-function; low-coverage; high-churn |
| src/web_dashboard.py | Critical | 75.80 | 464 | 1125 | 49.63 | low-maintainability; high-complexity-function; low-coverage; high-churn |
| src/category_map.py | High | 63.08 | 273 | 364 | 59.91 | low-maintainability; high-complexity-function; low-coverage; high-churn |
| tools/project_audit_dump.py | High | 56.18 | 350 | 446 | 0.00 | low-maintainability; high-complexity-function; missing-coverage-data; high-churn |
| src/run_registry.py | High | 55.52 | 311 | 407 | 71.21 | low-maintainability; high-complexity-function; high-churn |
| tools/secret_scan.py | Moderate | 45.10 | 230 | 288 | 0.00 | low-maintainability; high-complexity-function; missing-coverage-data; high-churn |
| templates/index.html | Moderate | 40.51 | 369 | 686 | 0.00 | missing-coverage-data; high-churn |
| tools/ingest_recover.py | Moderate | 40.26 | 145 | 184 | 0.00 | low-maintainability; high-complexity-function; missing-coverage-data; high-churn |
| tools/ontology_runtime_dump.py | Moderate | 37.93 | 214 | 263 | 0.00 | low-maintainability; high-complexity-function; missing-coverage-data; high-churn |
| tools/handoff_make.py | Moderate | 35.92 | 167 | 204 | 0.00 | high-complexity-function; missing-coverage-data; high-churn |
| src/db_schema.py | Low | 34.40 | 154 | 285 | 82.35 | high-churn |
| tools/project_data_snapshot.py | Low | 33.07 | 169 | 218 | 0.00 | missing-coverage-data; high-churn |
| src/api_main.py | Low | 29.14 | 157 | 320 | 70.77 | high-churn |
| tests/test_api_v2_crud.py | Low | 26.69 | 169 | 417 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| templates/admin_item_edit.html | Low | 26.48 | 167 | 444 | 0.00 | missing-coverage-data; high-churn |
| tools/handoff_make_run.py | Low | 25.28 | 95 | 131 | 0.00 | missing-coverage-data; high-churn |
| src/check_db.py | Low | 24.93 | 40 | 57 | 0.00 | low-coverage |
| src/reset_folders.py | Low | 22.54 | 43 | 58 | 0.00 | low-coverage |

## Lowest Maintainability Python Files

| File | Radon MI | Approx MI | Avg CC | Max CC | Max fn len |
| --- | --- | --- | --- | --- | --- |
| src/api_v2.py | 1.14 | 0.00 | 6.93 | 43 | 203 |
| src/ontology_runtime.py | 12.13 | 0.00 | 11.75 | 60 | 134 |
| src/ingest_wardrobe.py | 23.81 | 0.00 | 5.10 | 52 | 297 |
| src/web_dashboard.py | 25.78 | 0.00 | 5.78 | 30 | 135 |
| src/run_registry.py | 33.38 | 7.72 | 3.90 | 21 | 55 |
| tests/test_api_v2_crud.py | 38.65 | 19.48 | 5.88 | 30 | 86 |
| tools/project_audit_dump.py | 40.07 | 5.96 | 5.36 | 24 | 147 |
| tools/secret_scan.py | 40.42 | 14.63 | 6.11 | 16 | 37 |
| src/category_map.py | 40.58 | 8.35 | 12.14 | 65 | 114 |
| tools/ingest_recover.py | 44.74 | 23.04 | 8 | 25 | 117 |
| tools/ontology_runtime_dump.py | 49.00 | 17.09 | 3.80 | 16 | 128 |
| tests/test_run_registry.py | 51.49 | 37.65 | 4.25 | 9 | 21 |
| tools/project_data_snapshot.py | 52.49 | 19.85 | 4 | 14 | 110 |
| tests/test_web_dashboard_legacy_api_auth.py | 52.80 | 35.51 | 3 | 5 | 31 |
| tools/handoff_make.py | 53.55 | 21.85 | 6.50 | 20 | 151 |
| tests/test_error_contract.py | 53.78 | 33.12 | 4 | 6 | 33 |
| tests/test_ontology_color_lexicon.py | 55.54 | 44.17 | 13 | 13 | 23 |
| tools/handoff_make_run.py | 55.79 | 30.69 | 4 | 11 | 75 |
| tools/runs_report.py | 56.45 | 34.50 | 5 | 7 | 64 |
| tests/test_dashboard_index_filters.py | 56.70 | 39.99 | 3.67 | 5 | 37 |

## Most Complex Python Functions

| File | Function | CC | Max nesting | Length | Args | Docstring |
| --- | --- | --- | --- | --- | --- | --- |
| src/category_map.py | infer_internal_category | 65 | 1 | 114 | 2 | False |
| src/ontology_runtime.py | OntologyManager._build_indexes | 60 | 8 | 134 | 1 | False |
| src/ingest_wardrobe.py | main | 52 | 9 | 297 | 1 | False |
| src/api_v2.py | update_item | 43 | 6 | 203 | 3 | False |
| src/web_dashboard.py | index | 30 | 2 | 135 | 0 | True |
| tests/test_api_v2_crud.py | test_create_update_delete | 30 | 0 | 86 | 1 | False |
| src/api_v2.py | delete_item | 26 | 3 | 94 | 2 | False |
| tools/ingest_recover.py | main | 25 | 6 | 117 | 1 | False |
| tools/project_audit_dump.py | dump_project | 24 | 4 | 147 | 8 | False |
| src/run_registry.py | compute_kpis | 21 | 3 | 49 | 2 | False |
| tools/handoff_make.py | main | 20 | 2 | 151 | 0 | False |
| src/api_v2.py | create_item | 17 | 3 | 152 | 2 | False |
| tests/test_ingest_wardrobe_idempotence.py | test_ingest_idempotence_duplicate_goes_to_quarantine | 17 | 0 | 88 | 2 | False |
| tools/ontology_runtime_dump.py | main | 16 | 2 | 128 | 0 | False |
| tools/secret_scan.py | scan_text | 16 | 4 | 37 | 2 | False |
| src/db_schema.py | ensure_schema | 15 | 5 | 86 | 3 | True |
| src/ontology_runtime.py | OntologyManager.normalize_field | 15 | 2 | 57 | 3 | False |
| tests/test_run_registry_redaction.py | test_run_registry_redacts_secrets_in_meta_and_events | 15 | 0 | 46 | 2 | False |
| tools/project_data_snapshot.py | main | 14 | 5 | 110 | 0 | False |
| src/ontology_runtime.py | OntologyManager.load_from_files | 14 | 1 | 51 | 1 | False |

## Quality Gates / Issues

| Severity | Kind | Path | Details |
| --- | --- | --- | --- |
| warning | high-churn | src/api_main.py | Git churn is 320. |
| warning | high-churn | src/api_v2.py | Git churn is 1946. |
| warning | high-churn | src/category_map.py | Git churn is 364. |
| warning | high-churn | src/db_schema.py | Git churn is 285. |
| warning | high-churn | src/ingest_wardrobe.py | Git churn is 1106. |
| warning | high-churn | src/ontology_runtime.py | Git churn is 465. |
| warning | high-churn | src/run_registry.py | Git churn is 407. |
| warning | high-churn | src/web_dashboard.py | Git churn is 1125. |
| warning | high-churn | templates/admin_item_edit.html | Git churn is 444. |
| warning | high-churn | templates/index.html | Git churn is 686. |
| warning | high-churn | templates/item_detail.html | Git churn is 338. |
| warning | high-churn | tools/ontology_runtime_dump.py | Git churn is 263. |
| warning | high-churn | tools/project_audit_dump.py | Git churn is 446. |
| warning | high-churn | tools/secret_scan.py | Git churn is 288. |
| warning | high-function-complexity | src/api_v2.py | Max function CC is 43. |
| warning | high-function-complexity | src/category_map.py | Max function CC is 65. |
| warning | high-function-complexity | src/ingest_wardrobe.py | Max function CC is 46. |
| warning | high-function-complexity | src/ontology_runtime.py | Max function CC is 61. |
| warning | high-function-complexity | src/run_registry.py | Max function CC is 22. |
| warning | high-function-complexity | src/web_dashboard.py | Max function CC is 34. |

## Exact Duplicate Text Groups

_No data._

## Shadow / Mirrored Duplicates

_No data._

## Notes

- The script defaults to **Git-oriented scanning** (`auto -> tracked`) when `.git` is available. That prevents workspace logs, staging mirrors and untracked assets from inflating repo metrics.
- Python files are read with **UTF-8 BOM handling** (`utf-8-sig`) to avoid false parse errors from leading BOM bytes.
- Risk and hotspot scoring are **role-weighted**, so logs/assets/data no longer dominate engineering risk.
- The report now emits **phase-0 policy findings** for tracked backup files and tracked generated/export-style artifacts.
- When coverage is unavailable, the report emits an explicit quality warning instead of silently treating everything as uncovered.

## Suggested Next Moves

1. Use **`scan_mode=tracked`** as your canonical repo snapshot.
2. Run the canonical snapshot with **coverage + radon**.
3. Review **cleanup_candidates.csv** and **PHASE0_ACTIONS.md** before the next refactoring wave.
4. Remove tracked backup files and decide which generated/export artifacts should leave the canonical repo.
