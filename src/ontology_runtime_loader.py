from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping

import yaml


REQUIRED_ONTOLOGY_FILES: Dict[str, str] = {
    "taxonomy": "ontology_part_02_taxonomy.md",
    "core": "ontology_part_04_attributes_value_sets_core.md",
    "materials": "ontology_part_05_materials_sustainability_certifications.md",
    "extensions": "ontology_part_06_fits_cuts_collars_sizes.md",
}


def extract_yaml_from_md(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="strict")
    idx = raw.find("```yaml")
    if idx == -1:
        raise ValueError(f"YAML marker not found in: {path}")
    yaml_block = raw[idx + len("```yaml") :].lstrip("\n")
    close = yaml_block.find("```")
    if close != -1:
        yaml_block = yaml_block[:close]
    return yaml_block.strip() + "\n"


def load_embedded_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(extract_yaml_from_md(path))
    if isinstance(data, dict):
        return data
    return {}


def ontology_source_paths(ontology_dir: Path) -> Dict[str, Path]:
    return {
        name: ontology_dir / filename
        for name, filename in REQUIRED_ONTOLOGY_FILES.items()
    }


def ensure_required_ontology_files(paths: Mapping[str, Path], ontology_dir: Path) -> None:
    missing = [path.name for path in paths.values() if not path.exists()]
    if missing:
        raise RuntimeError(
            "Ontology files missing. Expected: " + ", ".join(missing) + f" (dir={ontology_dir})"
        )


def merge_collar_type_extensions(
    core_value_sets: Dict[str, Dict[str, Any]],
    extension_doc: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for value_set_id, value_set in core_value_sets.items():
        cloned = dict(value_set)
        cloned["values"] = list(value_set.get("values", []) or [])
        merged[value_set_id] = cloned

    extensions = (extension_doc.get("value_set_extensions_recommended") or {})
    if "vs_collar_type" in extensions and "vs_collar_type" in merged:
        add_values = extensions["vs_collar_type"].get("add_values", []) or []
        merged["vs_collar_type"]["values"].extend(list(add_values))

    return merged


def build_runtime_seed_data(ontology_dir: Path) -> Dict[str, Any]:
    paths = ontology_source_paths(ontology_dir)
    ensure_required_ontology_files(paths, ontology_dir)

    docs = {name: load_embedded_yaml(path) for name, path in paths.items()}

    core_value_sets = {
        value_set["id"]: value_set
        for value_set in (docs["core"].get("value_sets", []) or [])
        if isinstance(value_set, dict) and value_set.get("id")
    }
    merged_value_sets = merge_collar_type_extensions(core_value_sets, docs["extensions"])

    return {
        "categories": docs["taxonomy"].get("categories", []) or [],
        "value_sets": {
            "color_primary": merged_value_sets.get("vs_color_family", {}).get("values", []) or [],
            "fit": merged_value_sets.get("vs_fit_type", {}).get("values", []) or [],
            "collar": merged_value_sets.get("vs_collar_type", {}).get("values", []) or [],
        },
        "materials": docs["materials"].get("materials", []) or [],
    }
