# FILE: src/ontology_runtime.py
from __future__ import annotations

import difflib
import re
import sqlite3
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from src import settings

logger = logging.getLogger("WardrobeControl")


def _extract_yaml_from_md(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="strict")
    idx = raw.find("```yaml")
    if idx == -1:
        raise ValueError(f"YAML marker not found in: {path}")
    y = raw[idx + len("```yaml") :].lstrip("\n")
    close = y.find("```")
    if close != -1:
        y = y[:close]
    return y.strip() + "\n"


def _norm(s: str) -> str:
    s = (s or "").strip().lower()
    if not s:
        return ""
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[\(\)\[\]\{\},;:\/\\\|]+", " ", s)
    s = s.replace("&", " and ")
    s = re.sub(r"[\s\-]+", " ", s).strip()
    s = re.sub(r"[^a-z0-9_ ]+", "", s)
    return s


@dataclass(frozen=True)
class Suggestion:
    canonical: str
    score: float
    label: Optional[str] = None


@dataclass(frozen=True)
class NormalizationResult:
    field: str
    original: str
    canonical: Optional[str]
    matched_by: str  # override|lexicon|exact/synonym|fuzzy|legacy|none
    confidence: float
    suggestions: List[Suggestion]
    meta: Optional[Dict[str, Any]] = None


class OntologyManager:
    def __init__(
        self,
        categories: List[Dict[str, Any]],
        value_sets: Dict[str, List[Dict[str, Any]]],
        materials: List[Dict[str, Any]],
        *,
        legacy: Optional[Dict[str, List[str]]] = None,
        overrides: Optional[Dict[str, Dict[str, str]]] = None,
        color_lexicon: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.categories = categories
        self.value_sets = value_sets
        self.materials = materials
        self.legacy = legacy or {}
        self.overrides_raw = overrides or {}
        self.color_lexicon_raw = color_lexicon or {}

        self._idx_category: Dict[str, str] = {}
        self._cat_label: Dict[str, str] = {}
        self._cat_parent: Dict[str, Optional[str]] = {}

        self._idx_color: Dict[str, str] = {}
        self._idx_fit: Dict[str, str] = {}
        self._idx_collar: Dict[str, str] = {}
        self._idx_material: Dict[str, str] = {}
        self._mat_label: Dict[str, str] = {}

        self._override: Dict[str, Dict[str, str]] = {
            "category": {},
            "color_primary": {},
            "fit": {},
            "collar": {},
            "material_main": {},
        }

        self._color_lexicon: Dict[str, Dict[str, Any]] = {}
        self._category_roots: List[str] = []

        self._build_indexes()

    @classmethod
    def load_from_files(cls) -> "OntologyManager":
        odir = settings.ONTOLOGY_DIR

        tax = odir / "ontology_part_02_taxonomy.md"
        core = odir / "ontology_part_04_attributes_value_sets_core.md"
        mats = odir / "ontology_part_05_materials_sustainability_certifications.md"
        ext = odir / "ontology_part_06_fits_cuts_collars_sizes.md"

        missing = [p.name for p in [tax, core, mats, ext] if not p.exists()]
        if missing:
            raise RuntimeError(
                "Ontology files missing. Expected: " + ", ".join(missing) + f" (dir={odir})"
            )

        tax_y = yaml.safe_load(_extract_yaml_from_md(tax))
        core_y = yaml.safe_load(_extract_yaml_from_md(core))
        mats_y = yaml.safe_load(_extract_yaml_from_md(mats))
        ext_y = yaml.safe_load(_extract_yaml_from_md(ext))

        categories = tax_y.get("categories", []) or []
        core_value_sets = {vs["id"]: vs for vs in (core_y.get("value_sets", []) or [])}

        ext_vse = (ext_y.get("value_set_extensions_recommended") or {})
        if "vs_collar_type" in ext_vse and "vs_collar_type" in core_value_sets:
            add = ext_vse["vs_collar_type"].get("add_values", []) or []
            core_value_sets["vs_collar_type"]["values"].extend(add)

        vs_color = core_value_sets.get("vs_color_family", {}).get("values", []) or []
        vs_fit = core_value_sets.get("vs_fit_type", {}).get("values", []) or []
        vs_collar = core_value_sets.get("vs_collar_type", {}).get("values", []) or []

        value_sets = {
            "color_primary": vs_color,
            "fit": vs_fit,
            "collar": vs_collar,
        }

        materials = mats_y.get("materials", []) or []

        legacy = cls._load_legacy_from_db()
        overrides = cls._load_overrides()
        color_lexicon = cls._load_color_lexicon()

        return cls(
            categories=categories,
            value_sets=value_sets,
            materials=materials,
            legacy=legacy,
            overrides=overrides,
            color_lexicon=color_lexicon,
        )

    @staticmethod
    def _load_overrides() -> Dict[str, Dict[str, str]]:
        p = settings.ONTOLOGY_OVERRIDES_FILE
        if not p or not Path(p).exists():
            return {}
        try:
            data = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {}
            out: Dict[str, Dict[str, str]] = {}
            for k, v in data.items():
                if k == "version":
                    continue
                if isinstance(v, dict):
                    out[k] = {str(a): str(b) for a, b in v.items()}
            logger.info(f"Loaded ontology overrides from {p}", extra={"request_id": "-"})
            return out
        except Exception as e:
            logger.exception(f"Failed to load ontology overrides: {e}", extra={"request_id": "-"})
            return {}

    @staticmethod
    def _load_color_lexicon() -> Dict[str, Dict[str, Any]]:
        p = settings.ONTOLOGY_COLOR_LEXICON_FILE
        if not p or not Path(p).exists():
            return {}
        try:
            data = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {}
            out: Dict[str, Dict[str, Any]] = {}
            for k, v in data.items():
                if k == "version":
                    continue
                if isinstance(v, dict):
                    out[str(k)] = dict(v)
            logger.info(
                f"Loaded color lexicon from {p} ({len(out)} entries)",
                extra={"request_id": "-"},
            )
            return out
        except Exception as e:
            logger.exception(f"Failed to load color lexicon: {e}", extra={"request_id": "-"})
            return {}

    @staticmethod
    def _load_legacy_from_db() -> Dict[str, List[str]]:
        legacy: Dict[str, List[str]] = {k: [] for k in ["category", "color_primary", "material_main", "fit", "collar"]}
        try:
            conn = sqlite3.connect(str(settings.DB_PATH))
            cur = conn.cursor()
            for field in legacy.keys():
                cur.execute(f"SELECT DISTINCT {field} FROM items WHERE {field} IS NOT NULL AND TRIM({field}) != ''")
                vals = [r[0] for r in cur.fetchall() if isinstance(r[0], str)]
                legacy[field] = sorted(set(v.strip() for v in vals if v and v.strip()))
            conn.close()
        except Exception:
            pass
        return legacy

    def _build_indexes(self) -> None:
        # categories
        cat_ids = set()
        for c in self.categories:
            cid = c.get("id", "")
            if not cid:
                continue
            cat_ids.add(cid)
            parent_id = c.get("parent_id") or None
            self._cat_parent[cid] = parent_id

            label_de = c.get("label_de") or ""
            label_en = c.get("label_en") or ""
            self._cat_label[cid] = label_de or label_en or cid

            tokens = [cid, label_de, label_en]
            examples = c.get("examples") or []
            if isinstance(examples, list):
                tokens.extend([str(x) for x in examples])

            for t in tokens:
                nt = _norm(str(t))
                if nt:
                    self._idx_category[nt] = cid

        self._category_roots = [cid for cid, pid in self._cat_parent.items() if not pid]

        # value sets
        color_values = set()
        for row in self.value_sets.get("color_primary", []):
            val = row.get("value")
            if not val:
                continue
            color_values.add(val)
            self._idx_color[_norm(val)] = val
            for syn in (row.get("synonyms_de") or []):
                self._idx_color[_norm(str(syn))] = val

        fit_values = set()
        for row in self.value_sets.get("fit", []):
            val = row.get("value")
            if not val:
                continue
            fit_values.add(val)
            self._idx_fit[_norm(val)] = val
            for syn in (row.get("synonyms_de") or []):
                self._idx_fit[_norm(str(syn))] = val

        collar_values = set()
        for row in self.value_sets.get("collar", []):
            val = row.get("value")
            if not val:
                continue
            collar_values.add(val)
            self._idx_collar[_norm(val)] = val
            for syn in (row.get("synonyms_de") or []):
                self._idx_collar[_norm(str(syn))] = val

        # materials
        material_ids = set()
        for m in self.materials:
            mid = m.get("id")
            if not mid:
                continue
            material_ids.add(mid)
            label_de = m.get("label_de") or ""
            label_en = m.get("label_en") or ""
            self._mat_label[mid] = label_de or label_en or mid

            tokens = [mid, label_de, label_en]
            syns = m.get("synonyms") or []
            if isinstance(syns, list):
                tokens.extend([str(x) for x in syns])

            for t in tokens:
                nt = _norm(str(t))
                if nt:
                    self._idx_material[nt] = mid

        # overrides
        raw = self.overrides_raw or {}
        for field, mapping in raw.items():
            if field not in self._override or not isinstance(mapping, dict):
                continue
            for k, canon in mapping.items():
                nk = _norm(str(k))
                canon_s = str(canon).strip()
                if not nk or not canon_s:
                    continue

                ok = False
                if field == "category":
                    ok = canon_s in cat_ids
                    if ok:
                        self._idx_category[nk] = canon_s
                elif field == "color_primary":
                    ok = canon_s in color_values
                    if ok:
                        self._idx_color[nk] = canon_s
                elif field == "fit":
                    ok = canon_s in fit_values
                    if ok:
                        self._idx_fit[nk] = canon_s
                elif field == "collar":
                    ok = canon_s in collar_values
                    if ok:
                        self._idx_collar[nk] = canon_s
                elif field == "material_main":
                    ok = canon_s in material_ids
                    if ok:
                        self._idx_material[nk] = canon_s

                if ok:
                    self._override[field][nk] = canon_s
                else:
                    logger.warning(
                        f"Ignoring invalid override: field={field} key={k} -> {canon_s}",
                        extra={"request_id": "-"},
                    )

        # color lexicon
        for raw_key, meta in (self.color_lexicon_raw or {}).items():
            nk = _norm(raw_key)
            if not nk:
                continue
            family = str(meta.get("family", "")).strip()
            if family and family in color_values:
                self._color_lexicon[nk] = dict(meta)
                self._idx_color[nk] = family
            else:
                logger.warning(
                    f"Ignoring invalid color_lexicon entry: {raw_key} -> {family}",
                    extra={"request_id": "-"},
                )

    def _suggest(
        self,
        index: Dict[str, str],
        label_map: Optional[Dict[str, str]],
        value: str,
        limit: int = 5,
    ) -> List[Suggestion]:
        q = _norm(value)
        if not q:
            return []

        candidate_keys = list(index.keys())
        scored: Dict[str, float] = {}

        close = difflib.get_close_matches(q, candidate_keys, n=50, cutoff=settings.ONTOLOGY_SUGGEST_THRESHOLD)
        for k in close:
            canon = index[k]
            score = difflib.SequenceMatcher(None, q, k).ratio()
            scored[canon] = max(scored.get(canon, 0.0), score)

        out = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:limit]
        suggestions: List[Suggestion] = []
        for canon, sc in out:
            label = (label_map or {}).get(canon)
            suggestions.append(Suggestion(canonical=canon, score=round(sc, 3), label=label))
        return suggestions

    def _index_for(self, field: str) -> Tuple[Dict[str, str], Optional[Dict[str, str]]]:
        if field == "category":
            return self._idx_category, self._cat_label
        if field == "color_primary":
            return self._idx_color, None
        if field == "fit":
            return self._idx_fit, None
        if field == "collar":
            return self._idx_collar, None
        if field == "material_main":
            return self._idx_material, self._mat_label
        raise ValueError(f"Unsupported field: {field}")

    def normalize_field(self, field: str, value: str) -> NormalizationResult:
        original = value or ""
        v = original.strip()
        if not v:
            return NormalizationResult(field=field, original=original, canonical=None, matched_by="none", confidence=0.0, suggestions=[], meta=None)

        idx, labels = self._index_for(field)
        k = _norm(v)

        # override
        ov = self._override.get(field, {})
        if k in ov:
            canon = ov[k]
            suggestions = self._suggest(idx, labels, v, limit=5)
            return NormalizationResult(field=field, original=original, canonical=canon, matched_by="override", confidence=1.0, suggestions=suggestions, meta=None)

        # color lexicon
        if field == "color_primary" and k in self._color_lexicon:
            canon = self._idx_color.get(k)
            suggestions = self._suggest(idx, labels, v, limit=5)
            return NormalizationResult(
                field=field,
                original=original,
                canonical=canon,
                matched_by="lexicon",
                confidence=1.0,
                suggestions=suggestions,
                meta=dict(self._color_lexicon[k]),
            )

        # exact/synonym
        canon_exact = idx.get(k)
        if canon_exact:
            suggestions = self._suggest(idx, labels, v, limit=5)
            return NormalizationResult(field=field, original=original, canonical=canon_exact, matched_by="exact/synonym", confidence=1.0, suggestions=suggestions, meta=None)

        # fuzzy
        suggestions = self._suggest(idx, labels, v, limit=5)
        if suggestions:
            best = suggestions[0]
            if best.score >= settings.ONTOLOGY_FUZZY_THRESHOLD:
                return NormalizationResult(field=field, original=original, canonical=best.canonical, matched_by="fuzzy", confidence=best.score, suggestions=suggestions, meta=None)

        # legacy
        legacy_vals = set(self.legacy.get(field, []) or [])
        if v in legacy_vals:
            return NormalizationResult(field=field, original=original, canonical=v, matched_by="legacy", confidence=1.0, suggestions=suggestions, meta=None)

        # category fallback suggestions (help GPT)
        if field == "category" and not suggestions and self._category_roots:
            root_sugs = [
                Suggestion(canonical=cid, score=0.2, label=self._cat_label.get(cid))
                for cid in self._category_roots[:5]
            ]
            return NormalizationResult(field=field, original=original, canonical=None, matched_by="none", confidence=0.0, suggestions=root_sugs, meta=None)

        return NormalizationResult(field=field, original=original, canonical=None, matched_by="none", confidence=0.0, suggestions=suggestions, meta=None)

    def validate_or_normalize(self, field: str, value: Optional[str]) -> Tuple[Optional[str], NormalizationResult]:
        if value is None:
            nr = NormalizationResult(field=field, original="", canonical=None, matched_by="none", confidence=0.0, suggestions=[], meta=None)
            return None, nr

        nr = self.normalize_field(field, value)

        if settings.ONTOLOGY_MODE == "off":
            return value, nr

        if nr.canonical is None:
            return None, nr

        if settings.ONTOLOGY_MODE == "strict":
            if nr.matched_by == "legacy" and not settings.ONTOLOGY_ALLOW_LEGACY:
                return None, nr

        return nr.canonical, nr
