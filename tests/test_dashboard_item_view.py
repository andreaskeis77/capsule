from src.dashboard_item_view import enrich_item_for_display, enrich_items_for_display


def test_enrich_item_for_display_maps_known_raw_category_and_primary_image():
    item = {
        "id": 1,
        "name": "Soft Poncho",
        "category": "poncho",
        "image_path": "karen/item-1",
    }

    def fake_loader(path):
        assert path == "karen/item-1"
        return ["/images/karen/item-1/main.jpg", "/images/karen/item-1/side.jpg"]

    enriched = enrich_item_for_display(item, fake_loader)

    assert enriched["category_key"] == "cat_other"
    assert enriched["category_raw"] == "poncho"
    assert enriched["category_mapped_from_raw"] is True
    assert enriched["category_is_unknown"] is False
    assert enriched["all_images"] == ["/images/karen/item-1/main.jpg", "/images/karen/item-1/side.jpg"]
    assert enriched["primary_image"] == "/images/karen/item-1/main.jpg"



def test_enrich_item_for_display_marks_unknown_category_and_handles_missing_images():
    item = {
        "id": 2,
        "name": "Mystery Garment",
        "category": "totally-unknown-category",
        "image_path": "karen/item-2",
    }

    def fake_loader(path):
        assert path == "karen/item-2"
        return []

    enriched = enrich_item_for_display(item, fake_loader)

    assert enriched["category_key"] is None
    assert enriched["category_raw"] == "totally-unknown-category"
    assert enriched["category_is_unknown"] is True
    assert enriched["category_mapped_from_raw"] is False
    assert enriched["all_images"] == []
    assert enriched["primary_image"] is None



def test_enrich_items_for_display_preserves_input_order():
    rows = [
        {"id": 11, "name": "A", "category": "poncho", "image_path": "a"},
        {"id": 12, "name": "B", "category": "coat", "image_path": "b"},
    ]

    def fake_loader(path):
        return [f"/images/{path}/main.jpg"]

    enriched = enrich_items_for_display(rows, fake_loader)

    assert [it["id"] for it in enriched] == [11, 12]
    assert enriched[0]["primary_image"] == "/images/a/main.jpg"
    assert enriched[1]["primary_image"] == "/images/b/main.jpg"
