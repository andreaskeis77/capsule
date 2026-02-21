from __future__ import annotations

from pathlib import Path

import yaml


ALLOWED_FAMILIES = {
    "black",
    "white",
    "grey",
    "blue",
    "red",
    "green",
    "brown",
    "beige",
    "yellow_orange",
    "purple_pink",
    "metallic",
    "multicolor",
}


def test_color_lexicon_yaml_is_well_formed() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    p = repo_root / "ontology" / "color_lexicon.yaml"

    assert p.exists(), f"Missing file: {p}"

    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"Expected dict, got {type(data).__name__}"

    assert "version" in data, "Missing required top-level key: version"
    assert isinstance(data["version"], int), f"version must be int, got {type(data['version']).__name__}"

    for k, v in data.items():
        if k == "version":
            continue

        assert isinstance(k, str), f"Key must be str, got {type(k).__name__}"
        assert "{" not in k and "}" not in k, f"Suspicious key (likely YAML formatting bug): {k!r}"

        assert isinstance(v, dict), f"Value for {k!r} must be dict, got {type(v).__name__}: {v!r}"
        fam = v.get("family")
        assert isinstance(fam, str), f"family for {k!r} must be str, got {type(fam).__name__}"
        assert fam in ALLOWED_FAMILIES, f"Invalid family for {k!r}: {fam!r} (allowed: {sorted(ALLOWED_FAMILIES)})"