# Repository Metrics Report v2

Generated: 2026-03-06T08:16:51+00:00  
Repository: `C:\CapsuleWardrobeRAG`  
Scan mode: `filesystem`  
Branch: `main`  
HEAD: `50097deaf4a87111faf10829f06c2e4aa3feab67`  
Git commits: 47  
Coverage available: False  
Radon available in run: False

## Executive Summary

- Files scanned: **1548**
- Git tracked files in repo: **97**
- Git-visible files: **109**
- Text files scanned: **762**
- Binary files scanned: **786**
- Engineering files: **95**
- Production files: **57**
- Python files: **102**
- Tracked code lines: **8663**
- Engineering code lines: **12965**
- Production code lines: **11081**
- Engineering comment density: **3.69%**
- Exact duplicate text groups: **287**
- Shadow duplicate pairs: **282**
- Quality issues emitted: **133**

## Scope Summary

| Scope | Files | Tracked | Code LOC | Doc lines | Comments | Binary | Churn | Avg risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_scanned | 1548 | 97 | 125272 | 100424 | 808 | 786 | 20722 | 1.22 |
| docs_only | 487 | 24 | 0 | 100424 | 0 | 1 | 6929 | 0.04 |
| engineering_core | 95 | 65 | 12965 | 0 | 497 | 0 | 13555 | 17.88 |
| git_visible | 99 | 97 | 11312 | 6134 | 464 | 4 | 20668 | 14.97 |
| production_core | 57 | 46 | 11081 | 0 | 427 | 0 | 12012 | 21.98 |
| tests_only | 38 | 19 | 1884 | 0 | 70 | 0 | 1543 | 11.73 |
| tracked_only | 97 | 97 | 8663 | 6134 | 344 | 4 | 20668 | 14.28 |
| workspace_noise | 1455 | 4 | 116609 | 94290 | 464 | 786 | 54 | 0.34 |

## Repo Mix by Role

| Role | Files | Code LOC | Doc lines | Comments | Churn | Avg risk |
| --- | --- | --- | --- | --- | --- | --- |
| log | 138 | 106248 | 0 | 0 | 0 | 0.00 |
| other | 58 | 6059 | 0 | 311 | 238 | 2.88 |
| tooling | 15 | 4414 | 0 | 229 | 2239 | 28.80 |
| application | 23 | 4028 | 0 | 190 | 7154 | 30.82 |
| test | 38 | 1884 | 0 | 70 | 1543 | 11.73 |
| template | 6 | 1328 | 0 | 8 | 1468 | 13.96 |
| config | 13 | 1311 | 0 | 0 | 1151 | 2.17 |
| asset | 768 | 0 | 0 | 0 | 0 | 0.00 |
| data | 2 | 0 | 0 | 0 | 0 | 0.00 |
| documentation | 487 | 0 | 100424 | 0 | 6929 | 0.04 |

## Repo Mix by Language

| Language | Files | Code LOC | Comments | Doc lines | Churn |
| --- | --- | --- | --- | --- | --- |
| LOG | 138 | 106248 | 0 | 0 | 0 |
| Python | 102 | 15183 | 730 | 0 | 10350 |
| HTML | 6 | 1328 | 8 | 0 | 1468 |
| JSON | 10 | 987 | 0 | 2219 | 945 |
| PowerShell | 6 | 476 | 58 | 0 | 304 |
| BAK | 3 | 446 | 0 | 0 | 262 |
| YAML | 4 | 188 | 0 | 0 | 115 |
| No Extension | 4 | 178 | 0 | 0 | 184 |
| Batch | 2 | 130 | 12 | 0 | 78 |
| EXAMPLE | 1 | 38 | 0 | 0 | 46 |
| SAMPLE | 2 | 36 | 0 | 0 | 20 |
| INI | 2 | 26 | 0 | 0 | 13 |
| CODE-WORKSPACE | 1 | 8 | 0 | 0 | 8 |
| DB | 2 | 0 | 0 | 0 | 0 |
| EXE | 1 | 0 | 0 | 0 | 0 |
| JFIF | 6 | 0 | 0 | 0 | 0 |
| JPEG | 136 | 0 | 0 | 0 | 0 |
| JPG | 630 | 0 | 0 | 0 | 0 |
| Markdown | 76 | 0 | 0 | 89765 | 6895 |
| PNG | 2 | 0 | 0 | 0 | 0 |
| PYD | 8 | 0 | 0 | 0 | 0 |
| Text | 406 | 0 | 0 | 8440 | 34 |

## Top-Level Directories

| Directory | Files | Code LOC | Doc lines | Churn | Avg risk | Avg hotspot |
| --- | --- | --- | --- | --- | --- | --- |
| logs | 137 | 105695 | 0 | 0 | 0.00 | 0.56 |
| _release_staging | 670 | 7668 | 9620 | 0 | 0.60 | 1.20 |
| tools | 15 | 4414 | 0 | 2239 | 28.80 | 5725.44 |
| src | 23 | 4028 | 0 | 7154 | 30.82 | 18763.40 |
| . | 19 | 1172 | 695 | 2125 | 1.40 | 193.99 |
| tests | 19 | 942 | 0 | 1543 | 12.43 | 2050.26 |
| templates | 3 | 664 | 0 | 1468 | 19.60 | 2884.43 |
| 04_user_data | 3 | 595 | 0 | 42 | 0.38 | 23.71 |
| ontology | 11 | 94 | 4827 | 5375 | 1.56 | 94.70 |
| .venv_broken_20260215 | 9 | 0 | 0 | 0 | 0.00 | 0.20 |
| 02_wardrobe_images | 584 | 0 | 4171 | 0 | 0.00 | 0.15 |
| 03_database | 1 | 0 | 0 | 0 | 0.00 | 0.15 |
| docs | 54 | 0 | 81111 | 776 | 0.04 | 2.31 |

## Largest Engineering Files by Code LOC

| File | Lang | Role | Code LOC | Comments | Churn | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| tools/repo_metrics_bold_v2.py | Python | tooling | 1474 | 66 | 0 | 49.15 |
| tools/repo_metrics_bold.py | Python | tooling | 1175 | 54 | 0 | 48.30 |
| src/api_v2.py | Python | application | 929 | 27 | 1946 | 82.03 |
| wardrobe_export.json | JSON | config | 903 | 0 | 903 | 18.55 |
| src/ingest_wardrobe.py | Python | application | 565 | 20 | 1106 | 79.11 |
| src/web_dashboard.py | Python | application | 464 | 23 | 1125 | 78.09 |
| src/ontology_runtime.py | Python | application | 385 | 12 | 465 | 74.66 |
| _release_staging/CapsuleWardrobeRAG/templates/index.html | HTML | template | 369 | 4 | 0 | 13.86 |
| templates/index.html | HTML | template | 369 | 4 | 686 | 28.63 |
| tools/project_audit_dump.py | Python | tooling | 350 | 26 | 446 | 53.89 |
| src/run_registry.py | Python | application | 311 | 6 | 407 | 54.56 |
| src/category_map.py | Python | application | 273 | 38 | 364 | 63.65 |
| tools/secret_scan.py | Python | tooling | 230 | 9 | 288 | 42.87 |
| tools/ontology_runtime_dump.py | Python | tooling | 214 | 4 | 263 | 37.46 |
| src/web_dashboard.py.bak | BAK | application | 212 | 0 | 262 | 21.14 |
| _release_staging/CapsuleWardrobeRAG/tests/test_api_v2_crud.py | Python | test | 169 | 4 | 0 | 19.19 |
| tests/test_api_v2_crud.py | Python | test | 169 | 4 | 417 | 26.38 |
| tools/project_data_snapshot.py | Python | tooling | 169 | 7 | 218 | 33.72 |
| _release_staging/CapsuleWardrobeRAG/templates/admin_item_edit.html | HTML | template | 167 | 0 | 0 | 6.27 |
| templates/admin_item_edit.html | HTML | template | 167 | 0 | 444 | 18.08 |

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
| src/api_v2.py | Critical | 82.03 | 929 | 1946 | 0.00 | large-file; low-maintainability; high-complexity-function; high-churn |
| src/ingest_wardrobe.py | Critical | 79.11 | 565 | 1106 | 0.00 | large-file; low-maintainability; high-complexity-function; high-churn |
| src/web_dashboard.py | Critical | 78.09 | 464 | 1125 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/ontology_runtime.py | High | 74.66 | 385 | 465 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/category_map.py | High | 63.65 | 273 | 364 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/run_registry.py | Moderate | 54.56 | 311 | 407 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/project_audit_dump.py | Moderate | 53.89 | 350 | 446 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/repo_metrics_bold_v2.py | Moderate | 49.15 | 1474 | 0 | 0.00 | large-file; low-maintainability; high-complexity-function |
| tools/repo_metrics_bold.py | Moderate | 48.30 | 1175 | 0 | 0.00 | large-file; low-maintainability; high-complexity-function |
| tools/secret_scan.py | Moderate | 42.87 | 230 | 288 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/db_schema.py | Moderate | 40.12 | 154 | 285 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/ontology_runtime_dump.py | Moderate | 37.46 | 214 | 263 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/ingest_recover.py | Moderate | 37.43 | 145 | 184 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/handoff_make.py | Moderate | 36.25 | 167 | 204 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| src/api_main.py | Low | 34.34 | 157 | 320 | 0.00 | low-maintainability; high-churn |
| tools/project_data_snapshot.py | Low | 33.72 | 169 | 218 | 0.00 | low-maintainability; high-churn |
| templates/index.html | Low | 28.63 | 369 | 686 | 0.00 | high-churn |
| tests/test_api_v2_crud.py | Low | 26.38 | 169 | 417 | 0.00 | low-maintainability; high-complexity-function; high-churn |
| tools/handoff_make_run.py | Low | 25.49 | 95 | 131 | 0.00 | low-maintainability; high-churn |
| src/settings.py | Low | 24.18 | 97 | 239 | 0.00 | low-maintainability; high-churn |

## Lowest Maintainability Python Files

| File | Radon MI | Approx MI | Avg CC | Max CC | Max fn len |
| --- | --- | --- | --- | --- | --- |
| _release_staging/CapsuleWardrobeRAG/src/api_v2.py | None | 0.00 | 6.93 | 43 | 203 |
| _release_staging/CapsuleWardrobeRAG/src/ingest_wardrobe.py | None | 0.00 | 5.10 | 52 | 297 |
| _release_staging/CapsuleWardrobeRAG/src/ontology_runtime.py | None | 0.00 | 11.75 | 60 | 134 |
| _release_staging/CapsuleWardrobeRAG/src/web_dashboard.py | None | 0.00 | 5.78 | 30 | 135 |
| src/api_v2.py | None | 0.00 | 6.93 | 43 | 203 |
| src/ingest_wardrobe.py | None | 0.00 | 5.10 | 52 | 297 |
| src/ontology_runtime.py | None | 0.00 | 11.75 | 60 | 134 |
| src/web_dashboard.py | None | 0.00 | 5.78 | 30 | 135 |
| tools/repo_metrics_bold.py | None | 0.00 | 5.45 | 30 | 120 |
| tools/repo_metrics_bold_v2.py | None | 0.00 | 6.04 | 51 | 169 |
| _release_staging/CapsuleWardrobeRAG/tools/project_audit_dump.py | None | 5.96 | 5.36 | 24 | 147 |
| tools/project_audit_dump.py | None | 5.96 | 5.36 | 24 | 147 |
| _release_staging/CapsuleWardrobeRAG/src/run_registry.py | None | 7.72 | 3.90 | 21 | 55 |
| src/run_registry.py | None | 7.72 | 3.90 | 21 | 55 |
| _release_staging/CapsuleWardrobeRAG/src/category_map.py | None | 8.35 | 12.14 | 65 | 114 |
| src/category_map.py | None | 8.35 | 12.14 | 65 | 114 |
| _release_staging/CapsuleWardrobeRAG/tools/secret_scan.py | None | 14.63 | 6.11 | 16 | 37 |
| tools/secret_scan.py | None | 14.63 | 6.11 | 16 | 37 |
| _release_staging/CapsuleWardrobeRAG/tools/ontology_runtime_dump.py | None | 17.09 | 3.80 | 16 | 128 |
| tools/ontology_runtime_dump.py | None | 17.09 | 3.80 | 16 | 128 |

## Most Complex Python Functions

| File | Function | CC | Max nesting | Length | Args | Docstring |
| --- | --- | --- | --- | --- | --- | --- |
| _release_staging/CapsuleWardrobeRAG/src/category_map.py | infer_internal_category | 65 | 1 | 114 | 2 | False |
| src/category_map.py | infer_internal_category | 65 | 1 | 114 | 2 | False |
| _release_staging/CapsuleWardrobeRAG/src/ontology_runtime.py | OntologyManager._build_indexes | 60 | 8 | 134 | 1 | False |
| src/ontology_runtime.py | OntologyManager._build_indexes | 60 | 8 | 134 | 1 | False |
| _release_staging/CapsuleWardrobeRAG/src/ingest_wardrobe.py | main | 52 | 9 | 297 | 1 | False |
| src/ingest_wardrobe.py | main | 52 | 9 | 297 | 1 | False |
| tools/repo_metrics_bold_v2.py | compute_scores | 51 | 3 | 71 | 2 | False |
| _release_staging/CapsuleWardrobeRAG/src/api_v2.py | update_item | 43 | 6 | 203 | 3 | False |
| src/api_v2.py | update_item | 43 | 6 | 203 | 3 | False |
| _release_staging/CapsuleWardrobeRAG/src/web_dashboard.py | index | 30 | 2 | 135 | 0 | True |
| src/web_dashboard.py | index | 30 | 2 | 135 | 0 | True |
| _release_staging/CapsuleWardrobeRAG/tests/test_api_v2_crud.py | test_create_update_delete | 30 | 0 | 86 | 1 | False |
| tests/test_api_v2_crud.py | test_create_update_delete | 30 | 0 | 86 | 1 | False |
| tools/repo_metrics_bold.py | compute_scores | 30 | 2 | 50 | 1 | False |
| _release_staging/CapsuleWardrobeRAG/src/api_v2.py | delete_item | 26 | 3 | 94 | 2 | False |
| src/api_v2.py | delete_item | 26 | 3 | 94 | 2 | False |
| _release_staging/CapsuleWardrobeRAG/tools/ingest_recover.py | main | 25 | 6 | 117 | 1 | False |
| tools/ingest_recover.py | main | 25 | 6 | 117 | 1 | False |
| _release_staging/CapsuleWardrobeRAG/tools/project_audit_dump.py | dump_project | 24 | 4 | 147 | 8 | False |
| tools/project_audit_dump.py | dump_project | 24 | 4 | 147 | 8 | False |

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

| Count | Bytes | SHA1 | Tracked paths | All paths |
| --- | --- | --- | --- | --- |
| 67 | 0 | da39a3ee5e6b4b0d3255bfef95601890afd80709 | src/__init__.py | 02_wardrobe_images/karen/13 Sandale mit Open Toe und Riemchen/13 Sandale mit Open Toe und Riemchen.txt \|\| 02_wardrobe_images/karen/19 Firma Salomon Spezialschuh Querfeldeinläufe/19 Firma Salomon Spezialschuh Querfeldeinläufe.txt \|\| 02_wardrobe_images/karen/27 Stiefelette von Post Excellence/27 Stiefelette von Post Excellence.txt \|\| 02_wardrobe_images/karen/28 Stiefel Beige Knöchelhoch/28 Stiefel Beige Knöchelhoch.txt \|\| _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/13 Sandale mit Open Toe und Riemchen/13 Sandale mit Open Toe und Riemchen.txt \|\| _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/19 Firma Salomon Spezialschuh Querfeldeinläufe/19 Firma Salomon Spezialschuh Querfeldeinläufe.txt \|\| _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/27 Stiefelette von Post Excellence/27 Stiefelette von Post Excellence.txt \|\| _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/28 Stiefel Beige Knöchelhoch/28 Stiefel Beige Knöchelhoch.txt \|\| _release_staging/CapsuleWardrobeRAG/src/__init__.py \|\| logs/ngrok.err.log \|\| logs/ngrok.err_20260201-104454.log \|\| logs/ngrok.err_20260201-110547.log \|\| logs/ngrok.err_20260201-112503.log \|\| logs/ngrok.err_20260201-125314.log \|\| logs/ngrok.err_20260201-150023.log \|\| logs/ngrok.err_20260215-110700.log \|\| logs/ngrok.err_20260215-121437.log \|\| logs/ngrok.err_20260215-122402.log \|\| logs/ngrok.err_20260215-202301.log \|\| logs/ngrok.err_20260215-223016.log \|\| logs/ngrok.err_20260221-185711.log \|\| logs/ngrok.err_20260301-161252.log \|\| logs/ngrok.err_20260301-181619.log \|\| logs/ngrok.err_20260301-194224.log \|\| logs/ngrok.out.log \|\| logs/ngrok.out_20260201-104454.log \|\| logs/ngrok.out_20260201-110547.log \|\| logs/ngrok.out_20260201-112503.log \|\| logs/ngrok.out_20260201-125314.log \|\| logs/ngrok.out_20260201-150023.log \|\| logs/ngrok.out_20260215-110700.log \|\| logs/ngrok.out_20260215-121437.log \|\| logs/ngrok.out_20260215-122402.log \|\| logs/ngrok.out_20260215-202301.log \|\| logs/ngrok.out_20260215-223016.log \|\| logs/ngrok.out_20260221-185711.log \|\| logs/ngrok.out_20260301-161252.log \|\| logs/ngrok.out_20260301-173802.log \|\| logs/ngrok.out_20260301-181619.log \|\| logs/ngrok.out_20260301-194224.log \|\| logs/server.out.log \|\| logs/server.out_20260201-104454.log \|\| logs/server.out_20260201-110547.log \|\| logs/server.out_20260201-112503.log \|\| logs/server.out_20260201-125314.log \|\| logs/server.out_20260201-150023.log \|\| logs/server.out_20260215-110700.log \|\| logs/server.out_20260215-113152.log \|\| logs/server.out_20260215-120835.log \|\| logs/server.out_20260215-121437.log \|\| logs/server.out_20260215-121915.log \|\| logs/server.out_20260215-122402.log \|\| logs/server.out_20260215-202301.log \|\| logs/server.out_20260215-223016.log \|\| logs/server.out_20260221-185711.log \|\| logs/server.out_20260222-124115.log \|\| logs/server.out_20260222-192059.log \|\| logs/server.out_20260222-195527.log \|\| logs/server.out_20260222-204434.log \|\| logs/server.out_20260222-205115.log \|\| logs/server.out_20260301-113913.log \|\| logs/server.out_20260301-161252.log \|\| logs/server.out_20260301-164448.log \|\| logs/server.out_20260301-173802.log \|\| logs/server.out_20260301-181619.log \|\| logs/server.out_20260301-194224.log \|\| src/__init__.py |
| 7 | 1617 | c9bb6d328b9a4a7c74a70ad8220ed65c60587a74 | docs/HANDOFF_MANIFEST.md | _release_staging/CapsuleWardrobeRAG/docs/HANDOFF_MANIFEST.md \|\| docs/HANDOFF_MANIFEST.md \|\| docs/_snapshot/handoff_20260222-204547/HANDOFF_MANIFEST.md \|\| docs/_snapshot/handoff_20260222-204618/HANDOFF_MANIFEST.md \|\| docs/_snapshot/handoff_20260301-161040/HANDOFF_MANIFEST.md \|\| docs/_snapshot/handoff_20260301-161316/HANDOFF_MANIFEST.md \|\| docs/_snapshot/latest/HANDOFF_MANIFEST.md |
| 7 | 673 | ef93967190c613979b79541e4074334e10a7914b | docs/HANDOFF_RUNTIME_STATE.md | _release_staging/CapsuleWardrobeRAG/docs/HANDOFF_RUNTIME_STATE.md \|\| docs/HANDOFF_RUNTIME_STATE.md \|\| docs/_snapshot/handoff_20260222-204547/HANDOFF_RUNTIME_STATE.md \|\| docs/_snapshot/handoff_20260222-204618/HANDOFF_RUNTIME_STATE.md \|\| docs/_snapshot/handoff_20260301-161040/HANDOFF_RUNTIME_STATE.md \|\| docs/_snapshot/handoff_20260301-161316/HANDOFF_RUNTIME_STATE.md \|\| docs/_snapshot/latest/HANDOFF_RUNTIME_STATE.md |
| 4 | 576 | 839c065cdd6048c9e0c686f9430adb6e62bef105 |  | docs/_snapshot/handoff_20260222-204547/sanity_check.txt \|\| docs/_snapshot/handoff_20260222-204618/sanity_check.txt \|\| docs/_snapshot/handoff_20260301-161316/sanity_check.txt \|\| docs/_snapshot/latest/sanity_check.txt |
| 2 | 684761 | 7f86840a8f915e46fcbd9ba28c674b2d220ac745 |  | docs/_snapshot/handoff_20260301-161316/project_audit_dump.md \|\| docs/_snapshot/latest/project_audit_dump.md |
| 2 | 45231 | d66a90081a8d1b2f3926afc71851d12ec9463708 | ontology/ontology_part_03_item_types.md | _release_staging/CapsuleWardrobeRAG/ontology/ontology_part_03_item_types.md \|\| ontology/ontology_part_03_item_types.md |
| 2 | 38176 | 254c2ae3d18ca6e8a23cbdeea0f0a1205507de91 | src/api_v2.py | _release_staging/CapsuleWardrobeRAG/src/api_v2.py \|\| src/api_v2.py |
| 2 | 34992 | 21a86a729a289031956ad70ee8a1f662ca0e1692 | ontology/ontology_part_04_attributes_value_sets_core.md | _release_staging/CapsuleWardrobeRAG/ontology/ontology_part_04_attributes_value_sets_core.md \|\| ontology/ontology_part_04_attributes_value_sets_core.md |
| 2 | 34571 | 43319ceaff8113e3e15d1ae45719babab850f8f1 | ontology/ontology_part_07_brands_shops.md | _release_staging/CapsuleWardrobeRAG/ontology/ontology_part_07_brands_shops.md \|\| ontology/ontology_part_07_brands_shops.md |
| 2 | 29768 | 044cf249eb5520ebe35aa0b1c2f1971491578251 | ontology/ontology_part_06_fits_cuts_collars_sizes.md | _release_staging/CapsuleWardrobeRAG/ontology/ontology_part_06_fits_cuts_collars_sizes.md \|\| ontology/ontology_part_06_fits_cuts_collars_sizes.md |
| 2 | 27039 | d75210b5f978a52d1c2e6771fff461282751e931 | ontology/ontology_part_08_rules_disambiguation.md | _release_staging/CapsuleWardrobeRAG/ontology/ontology_part_08_rules_disambiguation.md \|\| ontology/ontology_part_08_rules_disambiguation.md |
| 2 | 26571 | 490215443f3ec74482e9bb1a86ed58d0ca8f0b7e | src/ingest_wardrobe.py | _release_staging/CapsuleWardrobeRAG/src/ingest_wardrobe.py \|\| src/ingest_wardrobe.py |
| 2 | 22814 | 7010b7e5b311e358f7a83705c03283fb71fa606e | ontology/ontology_part_02_taxonomy.md | _release_staging/CapsuleWardrobeRAG/ontology/ontology_part_02_taxonomy.md \|\| ontology/ontology_part_02_taxonomy.md |
| 2 | 19295 | 27b03fba7b748c064e55184d51c149aa2db58bed | src/web_dashboard.py | _release_staging/CapsuleWardrobeRAG/src/web_dashboard.py \|\| src/web_dashboard.py |
| 2 | 17673 | 910fa8bc427109388b1567f389d6cb948a1e924c | src/ontology_runtime.py | _release_staging/CapsuleWardrobeRAG/src/ontology_runtime.py \|\| src/ontology_runtime.py |
| 2 | 16799 | fc151a13ad34bd8720e78fdb3725edb67e82cced | templates/index.html | _release_staging/CapsuleWardrobeRAG/templates/index.html \|\| templates/index.html |
| 2 | 15290 | ca142af51a1da26fe93c0f6d14833412dac14f37 | tools/project_audit_dump.py | _release_staging/CapsuleWardrobeRAG/tools/project_audit_dump.py \|\| tools/project_audit_dump.py |
| 2 | 12830 | 27aac166e130a337afa9db3b3e0dafe3f77129e5 | ontology/ontology_part_05_materials_sustainability_certifications.md | _release_staging/CapsuleWardrobeRAG/ontology/ontology_part_05_materials_sustainability_certifications.md \|\| ontology/ontology_part_05_materials_sustainability_certifications.md |
| 2 | 11211 | 2f1f0123b004c4b0e15060da2a78a75fba1207bf | src/run_registry.py | _release_staging/CapsuleWardrobeRAG/src/run_registry.py \|\| src/run_registry.py |
| 2 | 11037 | da2dca7691d3b8e19b50f7bfaea2a64b07ecce2f |  | docs/_snapshot/handoff_20260301-161316/ontology_runtime_dump.json \|\| docs/_snapshot/latest/ontology_runtime_dump.json |

## Shadow / Mirrored Duplicates

| Source | Shadow | Bytes | Tracked src | Tracked shadow |
| --- | --- | --- | --- | --- |
| .gitignore | _release_staging/CapsuleWardrobeRAG/.gitignore | 845 | True | False |
| 02_wardrobe_images/andreas/2025 06 Luxor Businesshemd  modern fit Global Kent Bleu/2025 06 Luxor Businesshemd  modern fit Global Kent Bleu.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/andreas/2025 06 Luxor Businesshemd  modern fit Global Kent Bleu/2025 06 Luxor Businesshemd  modern fit Global Kent Bleu.txt | 789 | False | False |
| 02_wardrobe_images/andreas/Pailletten Jacket/Pailletten Jacket.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/andreas/Pailletten Jacket/Pailletten Jacket.txt | 2299 | False | False |
| 02_wardrobe_images/karen/01 Sandalen von der Marke Tamaris Rot/Sandalen von der Marke Tamaris.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/01 Sandalen von der Marke Tamaris Rot/Sandalen von der Marke Tamaris.txt | 441 | False | False |
| 02_wardrobe_images/karen/02 Sandalen von der Marke Tamaris Blau/Sandalen von der Marke Tamaris Blau.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/02 Sandalen von der Marke Tamaris Blau/Sandalen von der Marke Tamaris Blau.txt | 577 | False | False |
| 02_wardrobe_images/karen/03 flachen Pumps mit Keilabsatz Tamaris SChwarz/flachen Pumps mit Keilabsatz Tamaris SChwarz.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/03 flachen Pumps mit Keilabsatz Tamaris SChwarz/flachen Pumps mit Keilabsatz Tamaris SChwarz.txt | 611 | False | False |
| 02_wardrobe_images/karen/04 flachen Pumps mit Keilabsatz Tamaris beige-nude/flachen Pumps mit Keilabsatz Tamaris beige-nude.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/04 flachen Pumps mit Keilabsatz Tamaris beige-nude/flachen Pumps mit Keilabsatz Tamaris beige-nude.txt | 484 | False | False |
| 02_wardrobe_images/karen/05 flachen Pump mit einem Keilabsatz Tamaris/05 flachen Pump mit einem Keilabsatz Tamaris.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/05 flachen Pump mit einem Keilabsatz Tamaris/05 flachen Pump mit einem Keilabsatz Tamaris.txt | 741 | False | False |
| 02_wardrobe_images/karen/06 hohe Pumps ist von Tamaris aus der Serie Heart/06 hohe Pumps ist von Tamaris aus der Serie Heart.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/06 hohe Pumps ist von Tamaris aus der Serie Heart/06 hohe Pumps ist von Tamaris aus der Serie Heart.txt | 1223 | False | False |
| 02_wardrobe_images/karen/07 hohe Pumps ist von Tamaris aus der Serie Heart schwarz/07 hohe Pumps ist von Tamaris aus der Serie Heart schwarz.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/07 hohe Pumps ist von Tamaris aus der Serie Heart schwarz/07 hohe Pumps ist von Tamaris aus der Serie Heart schwarz.txt | 938 | False | False |
| 02_wardrobe_images/karen/08 Tanzschuh für die Tanzschule/08 Tanzschuh für die Tanzschule.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/08 Tanzschuh für die Tanzschule/08 Tanzschuh für die Tanzschule.txt | 1257 | False | False |
| 02_wardrobe_images/karen/09 Manolo Blanik/09 Manolo Blanik.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/09 Manolo Blanik/09 Manolo Blanik.txt | 1029 | False | False |
| 02_wardrobe_images/karen/13 Sandale mit Open Toe und Riemchen/13 Sandale mit Open Toe und Riemchen.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/13 Sandale mit Open Toe und Riemchen/13 Sandale mit Open Toe und Riemchen.txt | 0 | False | False |
| 02_wardrobe_images/karen/14 sportlichen Schuh der Firma Adidas/14 sportlichen Schuh der Firma Adidas.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/14 sportlichen Schuh der Firma Adidas/14 sportlichen Schuh der Firma Adidas.txt | 1481 | False | False |
| 02_wardrobe_images/karen/15 pinken Sneakern von der Marke Skechers/15 pinken Sneakern von der Marke Skechers.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/15 pinken Sneakern von der Marke Skechers/15 pinken Sneakern von der Marke Skechers.txt | 1179 | False | False |
| 02_wardrobe_images/karen/16 dunkelrosa Sneaker Marke Adidas/16 dunkelrosa Sneaker Marke Adidas.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/16 dunkelrosa Sneaker Marke Adidas/16 dunkelrosa Sneaker Marke Adidas.txt | 1354 | False | False |
| 02_wardrobe_images/karen/17 Sneaker in Neonorange Marke Skechers/17 Sneaker in Neonorange Marke Skechers.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/17 Sneaker in Neonorange Marke Skechers/17 Sneaker in Neonorange Marke Skechers.txt | 934 | False | False |
| 02_wardrobe_images/karen/18 Tennisschuh der Firma Asics/18 Tennisschuh der Firma Asics.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/18 Tennisschuh der Firma Asics/18 Tennisschuh der Firma Asics.txt | 836 | False | False |
| 02_wardrobe_images/karen/19 Firma Salomon Spezialschuh Querfeldeinläufe/19 Firma Salomon Spezialschuh Querfeldeinläufe.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/19 Firma Salomon Spezialschuh Querfeldeinläufe/19 Firma Salomon Spezialschuh Querfeldeinläufe.txt | 0 | False | False |
| 02_wardrobe_images/karen/20 Marke Asics Sportschuh/20 Marke Asics Sportschuh.txt | _release_staging/CapsuleWardrobeRAG/02_wardrobe_images/karen/20 Marke Asics Sportschuh/20 Marke Asics Sportschuh.txt | 1257 | False | False |

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
