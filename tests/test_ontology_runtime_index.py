from __future__ import annotations

import logging

from src.ontology_runtime import _norm
from src.ontology_runtime_index import (
    apply_color_lexicon_entries,
    build_category_indexes,
    build_runtime_indexes,
    empty_override_index,
)


def test_empty_override_index_contains_supported_fields() -> None:
    assert empty_override_index() == {
        "category": {},
        "color_primary": {},
        "fit": {},
        "collar": {},
        "material_main": {},
    }


def test_build_category_indexes_collects_labels_examples_and_roots() -> None:
    data = build_category_indexes(
        [
            {
                "id": "cat_tops",
                "label_de": "Oberteile",
                "label_en": "Tops",
                "examples": ["Shirt", "Bluse"],
            },
            {
                "id": "cat_outerwear",
                "label_de": "Jacken",
                "parent_id": "cat_tops",
            },
        ],
        normalize=_norm,
    )

    assert data.cat_ids == {"cat_tops", "cat_outerwear"}
    assert data.idx_category[_norm("Oberteile")] == "cat_tops"
    assert data.idx_category[_norm("Shirt")] == "cat_tops"
    assert data.idx_category[_norm("Jacken")] == "cat_outerwear"
    assert data.cat_label["cat_outerwear"] == "Jacken"
    assert data.cat_parent["cat_outerwear"] == "cat_tops"
    assert data.category_roots == ["cat_tops"]


def test_build_runtime_indexes_applies_valid_overrides_and_skips_invalid(caplog) -> None:
    categories = [{"id": "cat_tops", "label_de": "Oberteile"}]
    value_sets = {
        "color_primary": [{"value": "blue", "synonyms_de": ["blau"]}],
        "fit": [{"value": "regular", "synonyms_de": ["normal"]}],
        "collar": [{"value": "round_neck", "synonyms_de": ["rundhals"]}],
    }
    materials = [{"id": "mat_cotton", "label_de": "Baumwolle", "synonyms": ["cotton"]}]

    with caplog.at_level(logging.WARNING, logger="WardrobeControl"):
        indexes = build_runtime_indexes(
            categories=categories,
            value_sets=value_sets,
            materials=materials,
            overrides_raw={
                "category": {"tops alt": "cat_tops", "broken": "cat_missing"},
                "material_main": {"baumwolle": "mat_cotton"},
                "ignored": {"x": "y"},
            },
            color_lexicon_raw=None,
            normalize=_norm,
        )

    assert indexes.override["category"] == {_norm("tops alt"): "cat_tops"}
    assert indexes.override["material_main"] == {_norm("baumwolle"): "mat_cotton"}
    assert indexes.idx_category[_norm("tops alt")] == "cat_tops"
    assert indexes.idx_material[_norm("baumwolle")] == "mat_cotton"
    assert "Ignoring invalid override: field=category key=broken -> cat_missing" in caplog.text


def test_apply_color_lexicon_entries_requires_valid_family(caplog) -> None:
    color_index = {_norm("blue"): "blue"}

    with caplog.at_level(logging.WARNING, logger="WardrobeControl"):
        color_lexicon = apply_color_lexicon_entries(
            {
                "marine": {"family": "blue", "label": "Marine"},
                "broken": {"family": "violet", "label": "Broken"},
            },
            valid_families={"blue"},
            color_index=color_index,
            normalize=_norm,
        )

    assert color_lexicon == {_norm("marine"): {"family": "blue", "label": "Marine"}}
    assert color_index[_norm("marine")] == "blue"
    assert "Ignoring invalid color_lexicon entry: broken -> violet" in caplog.text
