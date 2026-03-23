from __future__ import annotations

from src.ontology_runtime import OntologyManager as FacadeOntologyManager, _norm
from src.ontology_runtime_manager import OntologyManager as DirectOntologyManager
from src.ontology_runtime_normalize import normalize_runtime_token


def test_runtime_facade_reexports_manager_and_normalizer() -> None:
    assert FacadeOntologyManager is DirectOntologyManager
    assert _norm(" Mäntel & Röcke ") == normalize_runtime_token(" Mäntel & Röcke ")
