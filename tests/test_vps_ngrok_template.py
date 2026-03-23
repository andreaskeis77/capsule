from pathlib import Path


def test_ngrok_template_contains_named_tunnel():
    content = Path("deploy/windows-vps/ngrok.template.yml").read_text(encoding="utf-8")
    assert "tunnels:" in content
    assert "wardrobe-api:" in content
    assert "addr: 8000" in content
    assert "__NGROK_AUTHTOKEN__" in content
