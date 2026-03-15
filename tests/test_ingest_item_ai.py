from __future__ import annotations

from pathlib import Path

from src.ingest_item_ai import (
    analyze_item_hybrid,
    build_analysis_content,
    build_analysis_prompt,
    fake_ai,
    get_openai_client,
)


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [type("Choice", (), {"message": type("Message", (), {"content": content})()})()]


class _RecordingClient:
    def __init__(self, response_text: str):
        self.calls = []
        self.chat = type("Chat", (), {"completions": self})()
        self._response_text = response_text

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeResponse(self._response_text)


class _FailingClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, **kwargs):
        raise RuntimeError("boom")


def test_build_analysis_prompt_embeds_text_context():
    prompt = build_analysis_prompt("Leinenhemd in Blau")

    assert "Leinenhemd in Blau" in prompt
    assert '"category": "cat_..."' in prompt



def test_build_analysis_content_limits_images_and_skips_missing_payloads(tmp_path: Path):
    paths = [tmp_path / "1.jpg", tmp_path / "2.jpg", tmp_path / "3.jpg"]

    def fake_loader(path: Path):
        if path.name == "2.jpg":
            return None
        return {"type": "image_url", "image_url": {"url": f"data:{path.name}"}}

    content = build_analysis_content(paths, "ctx", max_images=1, image_payload_loader=fake_loader)

    assert content[0]["type"] == "text"
    assert len(content) == 2
    assert content[1]["image_url"]["url"] == "data:1.jpg"



def test_analyze_item_hybrid_parses_json_response(tmp_path: Path):
    image_paths = [tmp_path / "a.jpg", tmp_path / "b.jpg"]
    client = _RecordingClient('{"category": "cat_top", "name": "Test"}')

    def fake_loader(path: Path):
        return {"type": "image_url", "image_url": {"url": f"data:{path.name}"}}

    result = analyze_item_hybrid(
        image_paths,
        "context",
        model="gpt-test",
        max_images=2,
        client_factory=lambda: client,
        image_payload_loader=fake_loader,
    )

    assert result == {"category": "cat_top", "name": "Test"}
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["model"] == "gpt-test"
    assert call["response_format"] == {"type": "json_object"}
    assert call["messages"][0]["role"] == "user"
    assert len(call["messages"][0]["content"]) == 3



def test_analyze_item_hybrid_returns_none_when_client_fails(tmp_path: Path):
    result = analyze_item_hybrid(
        [tmp_path / "a.jpg"],
        "context",
        model="gpt-test",
        max_images=1,
        client_factory=_FailingClient,
        image_payload_loader=lambda _: {"type": "image_url", "image_url": {"url": "data:test"}},
    )

    assert result is None



def test_fake_ai_returns_deterministic_payload():
    result = fake_ai("item-1", "A" * 250)

    assert result["name"] == "item-1"
    assert result["category"] == "cat_test"
    assert result["vision_description"] == f"FAKE_AI: {'A' * 200}"



def test_get_openai_client_wraps_import_errors(monkeypatch):
    import importlib

    def boom(name: str):
        raise ImportError(f"missing {name}")

    monkeypatch.setattr(importlib, "import_module", boom)

    try:
        get_openai_client()
    except RuntimeError as exc:
        assert "OpenAI SDK not available" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")



def test_ingest_wardrobe_keeps_ai_helper_aliases_for_stable_imports():
    from src import ingest_wardrobe
    from src.ingest_item_ai import analyze_item_hybrid as ai_analyze_item_hybrid
    from src.ingest_item_ai import fake_ai as ai_fake_ai
    from src.ingest_item_ai import get_openai_client as ai_get_openai_client

    assert ingest_wardrobe.analyze_item_hybrid is ai_analyze_item_hybrid
    assert ingest_wardrobe._fake_ai is ai_fake_ai
    assert ingest_wardrobe._get_openai_client is ai_get_openai_client
