from __future__ import annotations

import logging

from src.ontology_runtime import _norm
from src.ontology_runtime_index import build_category_indexes, build_material_indexes, build_value_index
from src.ontology_runtime_index_customization import apply_runtime_overrides, empty_override_index, override_targets


def test_override_targets_and_apply_runtime_overrides_stay_consistent(caplog) -> None:
    category_data = build_category_indexes(
        [{"id": "cat_tops", "label_de": "Oberteile"}],
        normalize=_norm,
    )
    color_data = build_value_index(
        [{"value": "blue", "synonyms_de": ["blau"]}],
        normalize=_norm,
    )
    fit_data = build_value_index(
        [{"value": "regular", "synonyms_de": ["normal"]}],
        normalize=_norm,
    )
    collar_data = build_value_index(
        [{"value": "round_neck", "synonyms_de": ["rundhals"]}],
        normalize=_norm,
    )
    material_data = build_material_indexes(
        [{"id": "mat_cotton", "label_de": "Baumwolle", "synonyms": ["cotton"]}],
        normalize=_norm,
    )

    targets = override_targets(
        category_data=category_data,
        color_data=color_data,
        fit_data=fit_data,
        collar_data=collar_data,
        material_data=material_data,
    )

    assert empty_override_index() == {
        "category": {},
        "color_primary": {},
        "fit": {},
        "collar": {},
        "material_main": {},
    }

    with caplog.at_level(logging.WARNING, logger="WardrobeControl"):
        applied = apply_runtime_overrides(
            {
                "category": {"tops alt": "cat_tops", "broken": "cat_missing"},
                "material_main": {"baumwolle": "mat_cotton"},
            },
            targets=targets,
            normalize=_norm,
        )

    assert applied["category"] == {_norm("tops alt"): "cat_tops"}
    assert applied["material_main"] == {_norm("baumwolle"): "mat_cotton"}
    assert "Ignoring invalid override: field=category key=broken -> cat_missing" in caplog.text
