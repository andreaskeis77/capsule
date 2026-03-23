from __future__ import annotations

from pathlib import Path

import src.runtime_config as runtime_config
import src.settings as settings



def test_load_runtime_config_normalizes_repo_relative_paths(monkeypatch):
    with monkeypatch.context() as m:
        m.setenv("WARDROBE_DB_PATH", "tmp/db/custom.db")
        m.setenv("WARDROBE_LOG_DIR", "tmp/logs")
        m.setenv("WARDROBE_LOG_FILE", "tmp/logs/wardrobe.log")
        cfg = runtime_config.load_runtime_config()

    assert cfg.db_path == (runtime_config.BASE_DIR / "tmp" / "db" / "custom.db").resolve()
    assert cfg.log_dir == (runtime_config.BASE_DIR / "tmp" / "logs").resolve()
    assert cfg.log_file == (runtime_config.BASE_DIR / "tmp" / "logs" / "wardrobe.log").resolve()



def test_reload_settings_updates_runtime_globals(monkeypatch):
    with monkeypatch.context() as m:
        m.setenv("WARDROBE_PORT", "5111")
        m.setenv("WARDROBE_HOST", "127.0.0.1")
        m.setenv("WARDROBE_APP_IMPORT", "src.api_main:app")
        settings.reload_settings()
        assert settings.PORT == 5111
        assert settings.HOST == "127.0.0.1"
        assert settings.APP_IMPORT_PATH == "src.api_main:app"

    settings.reload_settings()



def test_build_uvicorn_kwargs_uses_runtime_fields(monkeypatch):
    with monkeypatch.context() as m:
        m.setenv("WARDROBE_HOST", "127.0.0.1")
        m.setenv("WARDROBE_PORT", "5015")
        m.setenv("WARDROBE_DEBUG", "1")
        m.setenv("WARDROBE_ACCESS_LOG", "0")
        m.setenv("WARDROBE_PROXY_HEADERS", "0")
        cfg = runtime_config.load_runtime_config()
        kwargs = runtime_config.build_uvicorn_kwargs(cfg)

    assert kwargs == {
        "host": "127.0.0.1",
        "port": 5015,
        "reload": True,
        "access_log": False,
        "use_colors": False,
        "log_config": None,
        "proxy_headers": False,
    }
