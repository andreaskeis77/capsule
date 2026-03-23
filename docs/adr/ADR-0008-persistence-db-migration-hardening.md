# ADR-0008: Persistence / DB / Migration Hardening

## Status
Accepted

## Context
The repository already had a pragmatic SQLite schema bootstrap in `src/db_schema.py`,
but persistence concerns were still spread across multiple files:

- `src/db_schema.py` owned both schema definition and migration-like behavior
- `src/update_db_schema.py` implemented a second, narrower schema path
- `src/database_manager.py` recreated a reduced schema independently
- `src/check_db.py` used field assumptions that no longer matched the canonical DB shape

This created avoidable drift risk on a critical path: data integrity and reproducible setup.

## Decision
Introduce a small persistence hardening layer without bringing in a full ORM or external
migration framework.

The tranche adds:
- shared SQLite helpers in `src/db_sqlite.py`
- a minimal schema version ledger in `src/db_schema_migrations.py`
- `schema_migrations` creation/recording from canonical `ensure_schema()`
- `update_db_schema.py` as a compatibility shim that now routes into `ensure_schema()`
- `database_manager.py` reset behavior aligned with canonical schema creation
- `check_db.py` aligned with the current DB schema via `src/db_inspect.py`

## Consequences
Positive:
- one canonical schema path
- version evidence in the DB itself
- less duplication in persistence bootstrap
- safer future migration staging

Tradeoffs:
- still intentionally lightweight; this is not a full migration runner yet
- baseline migration recording is version-table based, not file-based SQL sequencing

## Rollback
Revert the tranche files and keep the previous direct-schema scripts.

## Follow-up
A later tranche may introduce file-backed numbered migrations once schema evolution
justifies that extra operational surface.
