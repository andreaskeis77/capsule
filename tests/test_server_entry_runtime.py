from __future__ import annotations

import src.server_entry as server_entry



def test_server_entry_main_uses_runtime_config(monkeypatch):
    calls: dict[str, object] = {}

    with monkeypatch.context() as m:
        m.setenv("WARDROBE_HOST", "127.0.0.1")
        m.setenv("WARDROBE_PORT", "5016")
        m.setenv("WARDROBE_DEBUG", "1")
        m.setenv("WARDROBE_APP_IMPORT", "src.api_main:app")

        import src.logging_config as logging_config
        import uvicorn

        m.setattr(logging_config, "setup_logging", lambda project_root: calls.setdefault("project_root", project_root))
        m.setattr(uvicorn, "run", lambda app, **kwargs: calls.update({"app": app, **kwargs}))

        server_entry.main()

    assert calls["app"] == "src.api_main:app"
    assert calls["host"] == "127.0.0.1"
    assert calls["port"] == 5016
    assert calls["reload"] is True
    assert calls["access_log"] is True
    assert calls["proxy_headers"] is True
