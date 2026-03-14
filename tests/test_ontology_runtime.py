from __future__ import annotations

from pathlib import Path

import pytest

from src.ontology_runtime import OntologyManager, _extract_yaml_from_md
from src.ontology_runtime_loader import build_runtime_seed_data


def _write_md_yaml(path: Path, body: str) -> None:
    path.write_text(f"header\n```yaml\n{body}\n```\nfooter\n", encoding="utf-8")


def _write_minimal_ontology_tree(tmp_path: Path) -> Path:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir()

    _write_md_yaml(
        ontology_dir / "ontology_part_02_taxonomy.md",
        """
        categories:
          - id: cat_tops
            label_de: Oberteile
          - id: cat_outerwear
            label_de: Jacken
            parent_id: cat_tops
        """,
    )
    _write_md_yaml(
        ontology_dir / "ontology_part_04_attributes_value_sets_core.md",
        """
        value_sets:
          - id: vs_color_family
            values:
              - value: blue
                synonyms_de: [blau]
          - id: vs_fit_type
            values:
              - value: regular
                synonyms_de: [normal]
          - id: vs_collar_type
            values:
              - value: round_neck
                synonyms_de: [rundhals]
        """,
    )
    _write_md_yaml(
        ontology_dir / "ontology_part_05_materials_sustainability_certifications.md",
        """
        materials:
          - id: mat_cotton
            label_de: Baumwolle
            synonyms: [cotton]
        """,
    )
    _write_md_yaml(
        ontology_dir / "ontology_part_06_fits_cuts_collars_sizes.md",
        """
        value_set_extensions_recommended:
          vs_collar_type:
            add_values:
              - value: turtleneck
                synonyms_de: [rollkragen]
        """,
    )

    return ontology_dir


def test_extract_yaml_from_md_requires_yaml_marker(tmp_path: Path) -> None:
    path = tmp_path / "broken.md"
    path.write_text("no fenced yaml here", encoding="utf-8")

    with pytest.raises(ValueError, match="YAML marker not found"):
        _extract_yaml_from_md(path)


def test_build_runtime_seed_data_merges_collar_extensions(tmp_path: Path) -> None:
    ontology_dir = _write_minimal_ontology_tree(tmp_path)

    seed_data = build_runtime_seed_data(ontology_dir)

    collar_values = seed_data["value_sets"]["collar"]
    assert [row["value"] for row in collar_values] == ["round_neck", "turtleneck"]
    assert seed_data["materials"][0]["id"] == "mat_cotton"


def test_load_from_files_raises_for_missing_required_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir()

    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_DIR", ontology_dir)

    with pytest.raises(RuntimeError, match="ontology_part_02_taxonomy.md"):
        OntologyManager.load_from_files()


def test_load_from_files_builds_manager_from_seed_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ontology_dir = _write_minimal_ontology_tree(tmp_path)
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_DIR", ontology_dir)
    monkeypatch.setattr("src.ontology_runtime.OntologyManager._load_legacy_from_db", staticmethod(lambda: {"category": [], "color_primary": [], "material_main": [], "fit": [], "collar": []}))
    monkeypatch.setattr("src.ontology_runtime.OntologyManager._load_overrides", staticmethod(lambda: {"category": {"tops alt": "cat_tops"}}))
    monkeypatch.setattr("src.ontology_runtime.OntologyManager._load_color_lexicon", staticmethod(lambda: {"marine": {"family": "blue", "label": "Marine"}}))
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_SUGGEST_THRESHOLD", 0.1)
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_FUZZY_THRESHOLD", 0.8)

    manager = OntologyManager.load_from_files()

    assert {category["id"] for category in manager.categories} == {"cat_tops", "cat_outerwear"}
    assert manager.normalize_field("category", "tops alt").matched_by == "override"
    color_result = manager.normalize_field("color_primary", "marine")
    assert color_result.canonical == "blue"
    assert color_result.matched_by == "lexicon"


def test_validate_or_normalize_rejects_legacy_in_strict_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = OntologyManager(
        categories=[{"id": "cat_tops", "label_de": "Oberteile"}],
        value_sets={"color_primary": [], "fit": [], "collar": []},
        materials=[],
        legacy={"category": ["historical_value"]},
    )
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_MODE", "strict")
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_ALLOW_LEGACY", False)
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_SUGGEST_THRESHOLD", 0.1)
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_FUZZY_THRESHOLD", 0.95)

    canonical, result = manager.validate_or_normalize("category", "historical_value")

    assert canonical is None
    assert result.matched_by == "legacy"


def test_normalize_field_returns_root_suggestions_for_unknown_category(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = OntologyManager(
        categories=[
            {"id": "cat_tops", "label_de": "Oberteile"},
            {"id": "cat_dresses", "label_de": "Kleider"},
        ],
        value_sets={"color_primary": [], "fit": [], "collar": []},
        materials=[],
    )
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_SUGGEST_THRESHOLD", 0.95)
    monkeypatch.setattr("src.ontology_runtime.settings.ONTOLOGY_FUZZY_THRESHOLD", 0.95)

    result = manager.normalize_field("category", "mystery bucket")

    assert result.canonical is None
    assert result.matched_by == "none"
    assert [suggestion.canonical for suggestion in result.suggestions] == ["cat_tops", "cat_dresses"]
