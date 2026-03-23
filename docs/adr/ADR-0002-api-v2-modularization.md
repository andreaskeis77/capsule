# ADR-0002: Tranche B – API v2 modularization without behavior change

## Status
Accepted

## Context
`src/api_v2.py` had become a mixed-responsibility module: request/auth helpers, ontology runtime state, image helpers, Pydantic contracts, and all API v2 routes lived in one file.

That made targeted changes in API v2 expensive and increased hotspot risk.

## Decision
Split API v2 into four files while keeping the external import surface stable:

- `src/api_v2_contracts.py`
- `src/api_v2_runtime.py`
- `src/api_v2_routes.py`
- `src/api_v2.py` as compatibility shim

## Rules
- No endpoint path changes
- No schema changes
- No auth flow changes
- No DB behavior changes
- Existing imports via `from src import api_v2` remain valid
- `api_v2.init_ontology()` continues to control the live ontology state used by routes

## Consequences
### Positive
- Smaller change surfaces
- Clearer ownership boundaries
- Safer future work on auth/runtime/contracts/routes separately
- Existing CRUD regression tests continue to validate behavior

### Trade-offs
- One additional compatibility layer
- Slightly more import indirection for shared runtime state
