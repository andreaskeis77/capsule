# ADR-0004: Dashboard + Category Map modularization

## Status
Accepted

## Context
`src/web_dashboard.py` and `src/category_map.py` are both change-heavy files. Repo metrics identified `src/web_dashboard.py` as a major hotspot and `src/category_map.py` as both a hotspot and a complexity concern. The goal of this tranche is to reduce controller density and split taxonomy registry from inference logic without changing public behavior.

## Decision
We split the dashboard layer into:
- `src/web_dashboard.py` as compatibility facade and Flask app bootstrap
- `src/web_dashboard_routes.py` for route registration and controller logic
- `src/web_dashboard_support.py` for request/auth/http/helper logic

We split category mapping into:
- `src/category_map_registry.py` for canonical taxonomy registry and derived constants
- `src/category_map_rules.py` for normalization and inference heuristics
- `src/category_map.py` as compatibility facade

## Consequences
Positive:
- lower controller density in `web_dashboard.py`
- explicit separation between taxonomy registry and inference rules
- behavior remains available under the original import paths
- new focused tests protect parsing and category inference edge-cases

Trade-offs:
- more modules to navigate
- facade modules now re-export compatibility symbols intentionally
