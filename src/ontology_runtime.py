# FILE: src/ontology_runtime.py
from __future__ import annotations

from pathlib import Path

from src import settings
from src.ontology_runtime_loader import extract_yaml_from_md
from src.ontology_runtime_manager import OntologyManager
from src.ontology_runtime_normalize import normalize_runtime_token
from src.ontology_runtime_types import NormalizationResult, Suggestion


def _extract_yaml_from_md(path: Path) -> str:
    return extract_yaml_from_md(path)


def _norm(value: str) -> str:
    return normalize_runtime_token(value)


__all__ = [
    "NormalizationResult",
    "OntologyManager",
    "Suggestion",
    "_extract_yaml_from_md",
    "_norm",
    "settings",
]
