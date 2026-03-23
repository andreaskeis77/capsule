# ADR-0005 – Ontology Runtime Index and Manager Modularization

## Status
Accepted

## Context
The ontology runtime was already partially decomposed into loader, matcher, service, sources and types modules. Two concentration points remained:
- `src/ontology_runtime.py` still mixed facade concerns, token normalization and manager orchestration.
- `src/ontology_runtime_index.py` still bundled index builders together with override and color-lexicon application.

This kept the runtime understandable, but it left one of the more critical consistency paths denser than the surrounding modules.

## Decision
We split the remaining responsibilities into stable internal modules while preserving the public import surface:
- `src/ontology_runtime_normalize.py` owns runtime token normalization.
- `src/ontology_runtime_manager.py` owns `OntologyManager` orchestration.
- `src/ontology_runtime_index_builders.py` owns pure index-construction helpers and dataclasses.
- `src/ontology_runtime_index_customization.py` owns override application and color-lexicon enrichment.
- `src/ontology_runtime.py` remains a compatibility facade.
- `src/ontology_runtime_index.py` remains the stable composition and re-export module.

## Consequences
Positive:
- Smaller units around a critical normalization path.
- Cleaner separation between pure builders and runtime customization/enrichment.
- Compatibility preserved for existing imports and tests.

Negative:
- More files in the ontology runtime subsystem.
- Internal navigation now depends on consistent re-export discipline.

## Guardrails
- No endpoint or schema change.
- No change to normalization semantics.
- Existing quality gates remain the acceptance contract.
