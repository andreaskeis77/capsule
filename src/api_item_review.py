from __future__ import annotations

import logging
import sqlite3
from typing import Any, Dict, List, Optional, Sequence

from src.api_item_query import review_row_to_payload


def suggest_color_canonicals(
    *,
    ontology: Any,
    color_variant: Optional[str],
    request_id: str,
    logger: logging.Logger,
) -> List[str]:
    suggestions: List[str] = []
    if ontology is None or not color_variant:
        return suggestions

    try:
        nr = ontology.normalize_field("color_primary", color_variant)
        suggestions = [s.canonical for s in (getattr(nr, "suggestions", None) or [])]
    except Exception:
        logger.exception(
            "Ontology suggestion failed",
            extra={"request_id": request_id, "event": "ontology.suggest_failed", "value": color_variant},
        )
    return suggestions


def build_review_items(
    rows: Sequence[sqlite3.Row],
    *,
    ontology: Any,
    request_id: str,
    logger: logging.Logger,
) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    for row in rows:
        variant = row["color_variant"] if "color_variant" in row.keys() else None
        suggestions = suggest_color_canonicals(
            ontology=ontology,
            color_variant=variant,
            request_id=request_id,
            logger=logger,
        )
        payloads.append(review_row_to_payload(row, suggestions))
    return payloads
