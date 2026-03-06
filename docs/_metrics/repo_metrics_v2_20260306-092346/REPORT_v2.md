# Repository Metrics Report v2

Generated: 2026-03-06T08:23:47+00:00  
Repository: `C:\CapsuleWardrobeRAG`  
Scan mode: `tracked`  
Branch: `main`  
HEAD: `50097deaf4a87111faf10829f06c2e4aa3feab67`  
Git commits: 47  
Coverage available: False  
Radon available in run: False

## Executive Summary

- Files scanned: **97**
- Git tracked files in repo: **97**
- Git-visible files: **122**
- Text files scanned: **93**
- Binary files scanned: **4**
- Engineering files: **65**
- Production files: **46**
- Python files: **50**
- Tracked code lines: **8663**
- Engineering code lines: **8506**
- Production code lines: **7564**
- Engineering comment density: **3.82%**
- Exact duplicate text groups: **0**
- Shadow duplicate pairs: **0**
- Quality issues emitted: **29**

## Scope Summary

| Scope | Files | Tracked | Code LOC | Doc lines | Comments | Binary | Churn | Avg risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_scanned | 97 | 97 | 8663 | 6134 | 344 | 4 | 20668 | 14.71 |
| docs_only | 24 | 24 | 0 | 6134 | 0 | 0 | 6929 | 0.80 |
| engineering_core | 65 | 65 | 8506 | 0 | 338 | 0 | 13555 | 21.61 |
| git_visible | 97 | 97 | 8663 | 6134 | 344 | 4 | 20668 | 14.71 |
| production_core | 46 | 46 | 7564 | 0 | 303 | 0 | 12012 | 25.24 |
| tests_only | 19 | 19 | 942 | 0 | 35 | 0 | 1543 | 12.81 |
| tracked_only | 97 | 97 | 8663 | 6134 | 344 | 4 | 20668 | 14.71 |
| workspace_noise | 4 | 4 | 0 | 0 | 0 | 4 | 0 | 0.00 |

## Repo Mix by Role

| Role | Files | Code LOC | Doc lines | Comments | Churn | Avg risk |
| --- | --- | --- | --- | --- | --- | --- |
| application | 23 | 4028 | 0 | 190 | 7154 | 31.67 |
| tooling | 13 | 1765 | 0 | 109 | 2239 | 26.65 |
| config | 7 | 1107 | 0 | 0 | 1151 | 3.57 |
| test | 19 | 942 | 0 | 35 | 1543 | 12.81 |
| template | 3 | 664 | 0 | 4 | 1468 | 20.47 |
| other | 4 | 157 | 0 | 6 | 184 | 0.70 |
| asset | 4 | 0 | 0 | 0 | 0 | 0.00 |
| documentation | 24 | 0 | 6134 | 0 | 6929 | 0.80 |

## Repo Mix by Language

| Language | Files | Code LOC | Comments | Doc lines | Churn |
| --- | --- | --- | --- | --- | --- |
| Python | 50 | 6267 | 305 | 0 | 10350 |
| JSON | 3 | 945 | 0 | 0 | 945 |
| HTML | 3 | 664 | 4 | 0 | 1468 |
| PowerShell | 3 | 238 | 29 | 0 | 304 |
| BAK | 1 | 212 | 0 | 0 | 262 |
| No Extension | 2 | 101 | 0 | 0 | 130 |
| YAML | 2 | 94 | 0 | 0 | 115 |
| Batch | 1 | 65 | 6 | 0 | 78 |
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
| src | 23 | 4028 | 0 | 7154 | 31.67 | 18763.40 |
| tools | 13 | 1765 | 0 | 2239 | 26.65 | 6596.59 |
| . | 17 | 1128 | 695 | 2071 | 1.54 | 213.80 |
| tests | 19 | 942 | 0 | 1543 | 12.81 | 2050.26 |
| templates | 3 | 664 | 0 | 1468 | 20.47 | 2884.43 |
| ontology | 11 | 94 | 4827 | 5375 | 1.58 | 94.70 |
| 04_user_data | 2 | 42 | 0 | 42 | 0.62 | 34.88 |
| docs | 9 | 0 | 612 | 776 | 0.25 | 13.08 |

## Largest Engineering Files by Code LOC

| File | Lang | Role | Code LOC | Comments | Churn | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| src/api_v2.py | Python | application | 929 | 27 | 1946 | 82.58 |
| wardrobe_export.json | JSON | config | 903 | 0 | 903 | 18.55 |
| src/ingest_wardrobe.py | Python | application | 565 | 20 | 1106 | 79.53 |
| src/web_dashboard.py | Python | application | 464 | 23 | 1125 | 80.33 |
| src/ontology_runtime.py | Python | application | 385 | 12 | 465 | 77.62 |
| templates/index.html | HTML | template | 369 | 4 | 686 | 30.08 |
| tools/project_audit_dump.py | Python | tooling | 350 | 26 | 446 | 55.92 |
| src/run_registry.py | Python | application | 311 | 6 | 407 | 56.50 |
| src/category_map.py | Python | application | 273 | 38 | 364 | 65.77 |
| tools/secret_scan.py | Python | tooling | 230 | 9 | 288 | 44.39 |
| tools/ontology_runtime_dump.py | Python | tooling | 214 | 4 | 263 | 38.74 |
| src/web_dashboard.py.bak | BAK | application | 212 | 0 | 262 | 22.25 |
| tests/test_api_v2_crud.py | Python | test | 169 | 4 | 417 | 27.19 |
| tools/project_data_snapshot.py | Python | tooling | 169 | 7 | 218 | 34.81 |
| templates/admin_item_edit.html | HTML | template | 167 | 0 | 444 | 18.74 |
| tools/handoff_make.py | Python | tooling | 167 | 10 | 204 | 37.51 |
| src/api_main.py | Python | application | 157 | 9 | 320 | 35.35 |
| src/db_schema.py | Python | application | 154 | 9 | 285 | 41.40 |
| tools/ingest_recover.py | Python | tooling | 145 | 8 | 184 | 38.70 |
| templates/item_detail.html | HTML | template | 128 | 0 | 338 | 12.59 |

## Top Hotspots (Engineering)

| File | Lang | Role | Hotspot | Churn | Avg CC | Radon MI | Approx MI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| src/api_v2.py | Python | application | 152276.26 | 1946 | 6.93 | None | 0.00 |
| src/web_dashboard.py | Python | application | 67671.68 | 1125 | 5.78 | None | 0.00 |
| src/ingest_wardrobe.py | Python | application | 61768.33 | 1106 | 5.10 | None | 0.00 |
| src/ontology_runtime.py | Python | application | 51074.26 | 465 | 11.75 | None | 0.00 |
| src/category_map.py | Python | application | 38864.18 | 364 | 12.14 | None | 8.35 |
| tools/project_audit_dump.py | Python | tooling | 21644.54 | 446 | 5.36 | None | 5.96 |
| src/run_registry.py | Python | application | 16573.41 | 407 | 3.90 | None | 7.72 |
| src/db_schema.py | Python | application | 14585.38 | 285 | 6 | None | 25.98 |
| tools/secret_scan.py | Python | tooling | 14531.85 | 288 | 6.11 | None | 14.63 |
| tests/test_api_v2_crud.py | Python | test | 12799.53 | 417 | 5.88 | None | 19.48 |
| tools/ingest_recover.py | Python | tooling | 10788.71 | 184 | 8 | None | 23.04 |
| tools/handoff_make.py | Python | tooling | 10240.97 | 204 | 6.50 | None | 21.85 |
| tools/ontology_runtime_dump.py | Python | tooling | 8844.29 | 263 | 3.80 | None | 17.09 |
| src/api_main.py | Python | application | 7816.96 | 320 | 2.33 | None | 24.26 |
| tools/project_data_snapshot.py | Python | tooling | 7310.29 | 218 | 4 | None | 19.85 |
| templates/index.html | HTML | template | 4397.80 | 686 |  |  |  |
| src/settings.py | Python | application | 4311.73 | 239 | 1.71 | None | 30.78 |
| tools/handoff_make_run.py | Python | tooling | 3920.35 | 131 | 4 | None | 30.69 |
| tools/project_sanity_check.py | Python | tooling | 3578.98 | 92 | 6 | None | 35.95 |
| tests/test_ingest_wardrobe_idempotence.py | Python | test | 3459.25 | 119 | 6.33 | None | 31.25 |

## Highest Risk Files (Engineering)

| File | Risk | Score | Code LOC | Churn | Coverage % | Flags |
| --- | --- | --- | --- | --- | --- | --- |
| src/api_v2.py | Critical | 82.58 | 929 | 1946 | 0.00 | large-file; low-maintainability; high-complexity-function; high-churn |
| src/web_dashboard.py | Critical | 80.33 | 464 | 1125 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/ingest_wardrobe.py | Critical | 79.53 | 565 | 1106 | 0.00 | large-file; low-maintainability; high-complexity-function; high-churn |
| src/ontology_runtime.py | Critical | 77.62 | 385 | 465 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/category_map.py | High | 65.77 | 273 | 364 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/run_registry.py | High | 56.50 | 311 | 407 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/project_audit_dump.py | High | 55.92 | 350 | 446 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/secret_scan.py | Moderate | 44.39 | 230 | 288 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/db_schema.py | Moderate | 41.40 | 154 | 285 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/ontology_runtime_dump.py | Moderate | 38.74 | 214 | 263 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/ingest_recover.py | Moderate | 38.70 | 145 | 184 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/handoff_make.py | Moderate | 37.51 | 167 | 204 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/api_main.py | Moderate | 35.35 | 157 | 320 | 0.00 | low-maintainability; high-churn |
| tools/project_data_snapshot.py | Low | 34.81 | 169 | 218 | 0.00 | low-maintainability; high-churn |
| templates/index.html | Low | 30.08 | 369 | 686 | 0.00 | high-churn |
| tests/test_api_v2_crud.py | Low | 27.19 | 169 | 417 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/handoff_make_run.py | Low | 26.22 | 95 | 131 | 0.00 | low-maintainability; high-churn |
| src/settings.py | Low | 24.83 | 97 | 239 | 0.00 | low-maintainability; high-churn |
| src/web_dashboard.py.bak | Low | 22.25 | 212 | 262 | 0.00 | high-churn |
| tools/project_sanity_check.py | Low | 21.95 | 67 | 92 | 0.00 | low-maintainability |

## Lowest Maintainability Python Files

| File | Radon MI | Approx MI | Avg CC | Max CC | Max fn len |
| --- | --- | --- | --- | --- | --- |
| src/api_v2.py | None | 0.00 | 6.93 | 43 | 203 |
| src/ingest_wardrobe.py | None | 0.00 | 5.10 | 52 | 297 |
| src/ontology_runtime.py | None | 0.00 | 11.75 | 60 | 134 |
| src/web_dashboard.py | None | 0.00 | 5.78 | 30 | 135 |
| tools/project_audit_dump.py | None | 5.96 | 5.36 | 24 | 147 |
| src/run_registry.py | None | 7.72 | 3.90 | 21 | 55 |
| src/category_map.py | None | 8.35 | 12.14 | 65 | 114 |
| tools/secret_scan.py | None | 14.63 | 6.11 | 16 | 37 |
| tools/ontology_runtime_dump.py | None | 17.09 | 3.80 | 16 | 128 |
| tests/test_api_v2_crud.py | None | 19.48 | 5.88 | 30 | 86 |
| tools/project_data_snapshot.py | None | 19.85 | 4 | 14 | 110 |
| tools/handoff_make.py | None | 21.85 | 6.50 | 20 | 151 |
| tools/ingest_recover.py | None | 23.04 | 8 | 25 | 117 |
| src/api_main.py | None | 24.26 | 2.33 | 8 | 41 |
| src/db_schema.py | None | 25.98 | 6 | 15 | 86 |
| tools/handoff_make_run.py | None | 30.69 | 4 | 11 | 75 |
| src/settings.py | None | 30.78 | 1.71 | 4 | 81 |
| tests/test_ingest_wardrobe_idempotence.py | None | 31.25 | 6.33 | 17 | 88 |
| tests/test_error_contract.py | None | 33.12 | 4 | 6 | 33 |
| tools/runs_report.py | None | 34.50 | 5 | 7 | 64 |

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
| warning | coverage-unavailable |  | No coverage.json provided and --run-tests was not used. |
| warning | high-churn | src/api_main.py | Git churn is 320. |
| warning | high-churn | src/api_v2.py | Git churn is 1946. |
| warning | high-churn | src/category_map.py | Git churn is 364. |
| warning | high-churn | src/db_schema.py | Git churn is 285. |
| warning | high-churn | src/ingest_wardrobe.py | Git churn is 1106. |
| warning | high-churn | src/ontology_runtime.py | Git churn is 465. |
| warning | high-churn | src/run_registry.py | Git churn is 407. |
| warning | high-churn | src/web_dashboard.py | Git churn is 1125. |
| warning | high-churn | src/web_dashboard.py.bak | Git churn is 262. |
| warning | high-churn | templates/admin_item_edit.html | Git churn is 444. |
| warning | high-churn | templates/index.html | Git churn is 686. |
| warning | high-churn | templates/item_detail.html | Git churn is 338. |
| warning | high-churn | tools/ontology_runtime_dump.py | Git churn is 263. |
| warning | high-churn | tools/project_audit_dump.py | Git churn is 446. |
| warning | high-churn | tools/secret_scan.py | Git churn is 288. |
| warning | high-churn | wardrobe_export.json | Git churn is 903. |
| warning | high-function-complexity | src/api_v2.py | Max function CC is 43. |
| warning | high-function-complexity | src/category_map.py | Max function CC is 65. |
| warning | high-function-complexity | src/ingest_wardrobe.py | Max function CC is 52. |

## Exact Duplicate Text Groups

_No data._

## Shadow / Mirrored Duplicates

_No data._

## Notes

- v2 defaults to **Git-oriented scanning** (`auto -> tracked`) when `.git` is available. That prevents workspace logs, staging mirrors and untracked assets from inflating repo metrics.
- Python files are read with **UTF-8 BOM handling** (`utf-8-sig`) to avoid false parse errors from leading BOM bytes.
- Risk and hotspot scoring are now **role-weighted**, so logs/assets/data no longer dominate engineering risk.
- When coverage is unavailable, v2 emits an explicit quality warning instead of silently treating everything as uncovered.
- Duplicate detection highlights exact same-content text files and suffix-based shadow copies such as staging mirrors.

## Suggested Next Moves

1. Use **`scan_mode=tracked`** as your canonical repo snapshot.
2. Use **`scan_mode=git-visible`** when you want repo + current untracked engineering work.
3. Use the **issues** and **shadow duplicates** outputs to clean workspace noise before comparing snapshots.
4. Add coverage input for a much stronger production risk model.
