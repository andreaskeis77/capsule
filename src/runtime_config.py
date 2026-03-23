from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Set

from src.runtime_env import (
    BASE_DIR,
    get_env_bool,
    get_env_float,
    get_env_int,
    get_env_str,
    load_project_dotenv,
    normalize_env_path,
)


@dataclass(frozen=True)
class RuntimeConfig:
    wardrobe_env: str
    debug: bool
    log_level: str
    allow_local_noauth: bool
    api_key: str
    db_path: Path
    img_dir: Path
    trash_dir: Path
    log_dir: Path
    log_file: Path
    max_image_mb: int
    max_image_bytes: int
    image_max_dim: int
    image_jpeg_quality: int
    store_original: bool
    mount_flask: bool
    ontology_mode: str
    ontology_allow_legacy: bool
    ontology_fuzzy_threshold: float
    ontology_suggest_threshold: float
    ontology_dir: Path
    ontology_overrides_file: Path
    ontology_color_lexicon_file: Path
    ontology_tolerant_fields: Set[str]
    host: str
    port: int
    app_import_path: str
    proxy_headers: bool
    access_log: bool


_ALLOWED_ONTOLOGY_MODES = {"off", "soft", "strict"}



def load_runtime_config() -> RuntimeConfig:
    load_project_dotenv(BASE_DIR)

    wardrobe_env = get_env_str("WARDROBE_ENV", "dev").lower()
    debug = get_env_bool("WARDROBE_DEBUG", "0")
    log_level = get_env_str("WARDROBE_LOG_LEVEL", "INFO").upper()

    allow_local_noauth = get_env_bool("WARDROBE_ALLOW_LOCAL_NOAUTH", "0")
    api_key = get_env_str("WARDROBE_API_KEY", "")

    db_path = normalize_env_path(
        get_env_str("WARDROBE_DB_PATH", ""),
        default=BASE_DIR / "03_database" / "wardrobe.db",
        base_dir=BASE_DIR,
    )
    img_dir = normalize_env_path(
        get_env_str("WARDROBE_IMG_DIR", ""),
        default=BASE_DIR / "02_wardrobe_images",
        base_dir=BASE_DIR,
    )
    trash_dir = normalize_env_path(
        get_env_str("WARDROBE_TRASH_DIR", ""),
        default=BASE_DIR / "04_user_data" / "trash_images",
        base_dir=BASE_DIR,
    )
    log_dir = normalize_env_path(
        get_env_str("WARDROBE_LOG_DIR", ""),
        default=BASE_DIR / "04_user_data" / "logs",
        base_dir=BASE_DIR,
    )
    log_file = normalize_env_path(
        get_env_str("WARDROBE_LOG_FILE", ""),
        default=log_dir / "api.log",
        base_dir=BASE_DIR,
    )

    max_image_mb = get_env_int("WARDROBE_MAX_IMAGE_MB", "8")
    max_image_bytes = max(0, max_image_mb) * 1024 * 1024
    image_max_dim = get_env_int("WARDROBE_IMAGE_MAX_DIM", "1600")
    image_jpeg_quality = get_env_int("WARDROBE_IMAGE_JPEG_QUALITY", "85")
    store_original = get_env_bool("WARDROBE_STORE_ORIGINAL", "0")

    mount_flask = get_env_bool("WARDROBE_MOUNT_FLASK", "1")

    ontology_mode = get_env_str("WARDROBE_ONTOLOGY_MODE", "off").lower()
    if ontology_mode not in _ALLOWED_ONTOLOGY_MODES:
        ontology_mode = "off"
    ontology_allow_legacy = get_env_bool("WARDROBE_ONTOLOGY_ALLOW_LEGACY", "1")
    ontology_fuzzy_threshold = get_env_float("WARDROBE_ONTOLOGY_FUZZY_THRESHOLD", "0.92")
    ontology_suggest_threshold = get_env_float("WARDROBE_ONTOLOGY_SUGGEST_THRESHOLD", "0.78")

    ontology_dir = normalize_env_path(
        get_env_str("WARDROBE_ONTOLOGY_DIR", ""),
        default=BASE_DIR / "ontology",
        base_dir=BASE_DIR,
    )
    ontology_overrides_file = normalize_env_path(
        get_env_str("WARDROBE_ONTOLOGY_OVERRIDES_FILE", ""),
        default=ontology_dir / "ontology_overrides.yaml",
        base_dir=BASE_DIR,
    )
    ontology_color_lexicon_file = normalize_env_path(
        get_env_str("WARDROBE_ONTOLOGY_COLOR_LEXICON_FILE", ""),
        default=ontology_dir / "color_lexicon.yaml",
        base_dir=BASE_DIR,
    )
    tolerant_raw = get_env_str("WARDROBE_ONTOLOGY_TOLERANT_FIELDS", "color_primary")
    ontology_tolerant_fields = {field.strip() for field in tolerant_raw.split(",") if field.strip()}

    host = get_env_str("WARDROBE_HOST", "0.0.0.0")
    port = get_env_int("WARDROBE_PORT", "5002")
    app_import_path = get_env_str("WARDROBE_APP_IMPORT", "src.api_main:app")
    proxy_headers = get_env_bool("WARDROBE_PROXY_HEADERS", "1")
    access_log = get_env_bool("WARDROBE_ACCESS_LOG", "1")

    return RuntimeConfig(
        wardrobe_env=wardrobe_env,
        debug=debug,
        log_level=log_level,
        allow_local_noauth=allow_local_noauth,
        api_key=api_key,
        db_path=db_path,
        img_dir=img_dir,
        trash_dir=trash_dir,
        log_dir=log_dir,
        log_file=log_file,
        max_image_mb=max_image_mb,
        max_image_bytes=max_image_bytes,
        image_max_dim=image_max_dim,
        image_jpeg_quality=image_jpeg_quality,
        store_original=store_original,
        mount_flask=mount_flask,
        ontology_mode=ontology_mode,
        ontology_allow_legacy=ontology_allow_legacy,
        ontology_fuzzy_threshold=ontology_fuzzy_threshold,
        ontology_suggest_threshold=ontology_suggest_threshold,
        ontology_dir=ontology_dir,
        ontology_overrides_file=ontology_overrides_file,
        ontology_color_lexicon_file=ontology_color_lexicon_file,
        ontology_tolerant_fields=ontology_tolerant_fields,
        host=host,
        port=port,
        app_import_path=app_import_path,
        proxy_headers=proxy_headers,
        access_log=access_log,
    )



def to_module_settings(config: RuntimeConfig) -> Dict[str, Any]:
    return {
        "WARDROBE_ENV": config.wardrobe_env,
        "DEBUG": config.debug,
        "LOG_LEVEL": config.log_level,
        "ALLOW_LOCAL_NOAUTH": config.allow_local_noauth,
        "API_KEY": config.api_key,
        "DB_PATH": config.db_path,
        "IMG_DIR": config.img_dir,
        "TRASH_DIR": config.trash_dir,
        "LOG_DIR": config.log_dir,
        "LOG_FILE": config.log_file,
        "MAX_IMAGE_MB": config.max_image_mb,
        "MAX_IMAGE_BYTES": config.max_image_bytes,
        "IMAGE_MAX_DIM": config.image_max_dim,
        "IMAGE_JPEG_QUALITY": config.image_jpeg_quality,
        "STORE_ORIGINAL": config.store_original,
        "MOUNT_FLASK": config.mount_flask,
        "ONTOLOGY_MODE": config.ontology_mode,
        "ONTOLOGY_ALLOW_LEGACY": config.ontology_allow_legacy,
        "ONTOLOGY_FUZZY_THRESHOLD": config.ontology_fuzzy_threshold,
        "ONTOLOGY_SUGGEST_THRESHOLD": config.ontology_suggest_threshold,
        "ONTOLOGY_DIR": config.ontology_dir,
        "ONTOLOGY_OVERRIDES_FILE": config.ontology_overrides_file,
        "ONTOLOGY_COLOR_LEXICON_FILE": config.ontology_color_lexicon_file,
        "ONTOLOGY_TOLERANT_FIELDS": config.ontology_tolerant_fields,
        "FUZZY_THRESHOLD": config.ontology_fuzzy_threshold,
        "SUGGEST_THRESHOLD": config.ontology_suggest_threshold,
        "TRASH_ROOT": config.trash_dir,
        "HOST": config.host,
        "PORT": config.port,
        "APP_IMPORT_PATH": config.app_import_path,
        "PROXY_HEADERS": config.proxy_headers,
        "ACCESS_LOG": config.access_log,
    }



def load_module_settings() -> Dict[str, Any]:
    return to_module_settings(load_runtime_config())



def build_uvicorn_kwargs(config: RuntimeConfig | None = None) -> Dict[str, Any]:
    runtime = config or load_runtime_config()
    return {
        "host": runtime.host,
        "port": runtime.port,
        "reload": runtime.debug,
        "access_log": runtime.access_log,
        "use_colors": False,
        "log_config": None,
        "proxy_headers": runtime.proxy_headers,
    }
