from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

from src import category_map as cm

ItemDict = Dict[str, Any]
ImageLoader = Callable[[Optional[str]], List[str]]


def enrich_item_for_display(item: Mapping[str, Any], image_loader: ImageLoader) -> ItemDict:
    """Return a display-ready item dict with category/image metadata.

    This keeps controller logic thin and ensures index/detail/admin use the same
    enrichment rules for category mapping and image loading.
    """
    d: ItemDict = dict(item)

    raw_cat = d.get("category")
    name = d.get("name")
    internal = cm.infer_internal_category(raw_cat, name=name)

    category_raw = (raw_cat or "").strip() if raw_cat is not None else ""
    all_images = image_loader(d.get("image_path"))

    d["category_key"] = internal
    d["category_label"] = cm.display_category_label(raw_cat, name=name)
    d["category_group"] = cm.category_group_for_internal(internal)
    d["category_raw"] = category_raw
    d["category_is_unknown"] = bool(category_raw) and internal is None
    d["category_mapped_from_raw"] = bool(category_raw) and (internal is not None) and (category_raw != internal)
    d["all_images"] = all_images
    d["primary_image"] = all_images[0] if all_images else None

    return d


def enrich_items_for_display(rows: Iterable[Mapping[str, Any]], image_loader: ImageLoader) -> List[ItemDict]:
    return [enrich_item_for_display(row, image_loader) for row in rows]


__all__ = [
    "ImageLoader",
    "ItemDict",
    "enrich_item_for_display",
    "enrich_items_for_display",
]
