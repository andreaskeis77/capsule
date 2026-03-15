from __future__ import annotations

import importlib
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from src.ingest_item_io import image_to_data_url

logger = logging.getLogger("WardrobeIngest")


def build_analysis_prompt(text_context: str) -> str:
    return (
        "Analysiere dieses Kleidungsstück.\n"
        f"TEXT-DATEN: '{text_context}'\n"
        "Nutze STRIKT die Mode-Ontologie IDs (cat_..., etc.).\n"
        "GIB NUR EIN VALIDES JSON ZURÜCK:\n"
        "{\n"
        '  "brand": "Marke", "category": "cat_...", "name": "Produktname",\n'
        '  "color_primary": "Farbe", "material_main": "Material",\n'
        '  "fit": "Passform", "collar": "Kragenform", "price": "Preis",\n'
        '  "vision_description": "Detaillierte Analyse"\n'
        "}"
    )


def build_analysis_content(
    image_paths: Sequence[Path],
    text_context: str,
    *,
    max_images: int,
    image_payload_loader: Optional[Callable[[Path], Optional[Dict[str, Any]]]] = None,
) -> List[Dict[str, Any]]:
    payload_loader = image_payload_loader if image_payload_loader is not None else image_to_data_url
    content: List[Dict[str, Any]] = [{"type": "text", "text": build_analysis_prompt(text_context)}]
    attached = 0
    for path in image_paths:
        if attached >= max_images:
            break
        payload = payload_loader(path)
        if payload is None:
            continue
        content.append(payload)
        attached += 1
    return content


def get_openai_client():
    try:
        module = importlib.import_module("openai")
        openai_cls = getattr(module, "OpenAI")
    except Exception as e:
        raise RuntimeError(f"OpenAI SDK not available: {e}") from e
    return openai_cls()


def analyze_item_hybrid(
    image_paths: Sequence[Path],
    text_context: str,
    *,
    model: str,
    max_images: int,
    client_factory: Optional[Callable[[], Any]] = None,
    image_payload_loader: Optional[Callable[[Path], Optional[Dict[str, Any]]]] = None,
    log: Optional[logging.Logger] = None,
) -> Optional[Dict[str, Any]]:
    active_logger = log if log is not None else logger
    client_builder = client_factory if client_factory is not None else get_openai_client
    content = build_analysis_content(
        image_paths,
        text_context,
        max_images=max_images,
        image_payload_loader=image_payload_loader,
    )

    client = client_builder()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
        )
        text = response.choices[0].message.content
        return json.loads(text)
    except Exception as e:
        active_logger.error("[OpenAI] error: %s", e)
        return None


def fake_ai(item_name: str, text_context: str) -> Dict[str, Any]:
    return {
        "name": item_name,
        "brand": None,
        "category": "cat_test",
        "color_primary": None,
        "material_main": None,
        "fit": None,
        "collar": None,
        "price": None,
        "vision_description": f"FAKE_AI: {text_context[:200]}".strip(),
    }
