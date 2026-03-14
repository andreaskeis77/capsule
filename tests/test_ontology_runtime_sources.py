from __future__ import annotations

import sqlite3
from pathlib import Path

from src.ontology_runtime_sources import (
    empty_legacy_values,
    load_color_lexicon,
    load_legacy_values,
    load_overrides,
)


def test_load_overrides_skips_version_and_non_mapping_values(tmp_path: Path) -> None:
    path = tmp_path / "overrides.yaml"
    path.write_text(
        """
        version: 1
        category:
          tops alt: cat_tops
        ignored_list:
          - nope
        color_primary:
          marine: blue
        """,
        encoding="utf-8",
    )

    overrides = load_overrides(path)

    assert overrides == {
        "category": {"tops alt": "cat_tops"},
        "color_primary": {"marine": "blue"},
    }


def test_load_color_lexicon_skips_version_and_non_mapping_values(tmp_path: Path) -> None:
    path = tmp_path / "color_lexicon.yaml"
    path.write_text(
        """
        version: 1
        marine:
          family: blue
          label: Marine
        ignored_scalar: nope
        """,
        encoding="utf-8",
    )

    color_lexicon = load_color_lexicon(path)

    assert color_lexicon == {
        "marine": {"family": "blue", "label": "Marine"},
    }


def test_load_legacy_values_reads_distinct_trimmed_values(tmp_path: Path) -> None:
    db_path = tmp_path / "wardrobe.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE items (
            category TEXT,
            color_primary TEXT,
            material_main TEXT,
            fit TEXT,
            collar TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO items(category, color_primary, material_main, fit, collar) VALUES (?, ?, ?, ?, ?)",
        [
            ("cat_tops", "blue", "mat_cotton", "regular", "round_neck"),
            ("  cat_tops  ", "blue", "mat_cotton", "regular", "round_neck"),
            ("cat_outerwear", "navy", "mat_wool", "slim", "turtleneck"),
            ("   ", None, None, None, None),
        ],
    )
    conn.commit()
    conn.close()

    legacy = load_legacy_values(db_path)

    assert legacy["category"] == ["cat_outerwear", "cat_tops"]
    assert legacy["color_primary"] == ["blue", "navy"]
    assert legacy["material_main"] == ["mat_cotton", "mat_wool"]
    assert legacy["fit"] == ["regular", "slim"]
    assert legacy["collar"] == ["round_neck", "turtleneck"]


def test_load_legacy_values_returns_empty_mapping_when_query_fails(tmp_path: Path) -> None:
    db_path = tmp_path / "missing_table.db"
    sqlite3.connect(str(db_path)).close()

    legacy = load_legacy_values(db_path)

    assert legacy == empty_legacy_values()
