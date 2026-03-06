from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = (
        s.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .replace("Ã¤", "ae")
        .replace("Ã¶", "oe")
        .replace("Ã¼", "ue")
        .replace("ÃŸ", "ss")
    )
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "item"


def _safe_under(base: Path, target: Path) -> bool:
    try:
        base_r = base.resolve()
        targ_r = target.resolve()
        if hasattr(targ_r, "is_relative_to"):
            return targ_r.is_relative_to(base_r)  # type: ignore[attr-defined]
        targ_r.relative_to(base_r)
        return True
    except Exception:
        return False


def _rmtree_robust(path: Path | str, ignore_errors: bool = False) -> None:
    path = Path(path)
    import stat
    import time
    import inspect

    has_onexc = "onexc" in inspect.signature(shutil.rmtree).parameters

    def _make_writable(p) -> None:
        try:
            os.chmod(p, stat.S_IWRITE)
        except Exception:
            pass

    def _onerror(func, p, exc_info):
        _make_writable(p)
        try:
            func(p)
        except Exception:
            pass

    def _onexc(func, p, exc):
        _make_writable(p)
        try:
            func(p)
        except Exception:
            pass

    for attempt in range(3):
        try:
            if not path.exists():
                return
            if has_onexc:
                shutil.rmtree(path, onexc=_onexc)
            else:
                shutil.rmtree(path, onerror=_onerror)
            return
        except Exception:
            if attempt == 2:
                if ignore_errors:
                    return
                raise
            time.sleep(0.2 * (attempt + 1))


@dataclass(frozen=True)
class StoredImage:
    rel_path: str
    abs_dir: Path
    main_path: Path


@dataclass(frozen=True)
class FolderMoveResult:
    old_rel: str
    new_rel: str
    src_dir: Path
    dst_dir: Path
    moved: bool = False
    conflict: bool = False


@dataclass(frozen=True)
class TrashMoveResult:
    image_path: str
    src_dir: Path
    trash_dir: Path
    moved: bool = False


def item_rel_dir(user_id: str, name: str, item_id: int) -> str:
    return str(Path(user_id) / f"{_slugify(name)}_{item_id}").replace("\\", "/")


def create_image_folder_for_item(base_dir: Path, user_id: str, name: str, item_id: int, jpg_bytes: bytes) -> StoredImage:
    rel_dir = item_rel_dir(user_id, name, item_id)
    abs_dir = base_dir / Path(rel_dir)
    abs_dir.mkdir(parents=True, exist_ok=True)
    main_path = abs_dir / "main.jpg"
    main_path.write_bytes(jpg_bytes)
    return StoredImage(rel_path=rel_dir, abs_dir=abs_dir, main_path=main_path)


def move_image_folder_for_item(base_dir: Path, old_rel: str, new_user: str, new_name: str, item_id: int) -> FolderMoveResult:
    new_rel = item_rel_dir(new_user, new_name, item_id)
    src_dir = base_dir / Path(old_rel)
    dst_dir = base_dir / Path(new_rel)

    if not src_dir.exists():
        return FolderMoveResult(old_rel=old_rel, new_rel=new_rel, src_dir=src_dir, dst_dir=dst_dir, moved=False, conflict=False)

    if not _safe_under(base_dir, src_dir) or not _safe_under(base_dir, dst_dir):
        raise RuntimeError("Jail check failed for rename/move")

    if src_dir.resolve() == dst_dir.resolve():
        return FolderMoveResult(old_rel=old_rel, new_rel=new_rel, src_dir=src_dir, dst_dir=dst_dir, moved=False, conflict=False)

    if dst_dir.exists():
        return FolderMoveResult(old_rel=old_rel, new_rel=new_rel, src_dir=src_dir, dst_dir=dst_dir, moved=False, conflict=True)

    dst_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        src_dir.rename(dst_dir)
    except Exception:
        shutil.move(str(src_dir), str(dst_dir))

    return FolderMoveResult(old_rel=old_rel, new_rel=new_rel, src_dir=src_dir, dst_dir=dst_dir, moved=True, conflict=False)


def rollback_moved_image_dir(result: FolderMoveResult) -> None:
    if not result.moved:
        return
    if not result.dst_dir.exists():
        return
    result.src_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        result.dst_dir.rename(result.src_dir)
    except Exception:
        shutil.move(str(result.dst_dir), str(result.src_dir))


def move_item_image_dir_to_trash(base_dir: Path, trash_base_dir: Path, image_path: str, item_id: int, request_id: str) -> TrashMoveResult:
    rel = Path(image_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise RuntimeError("JailCheckFailed")

    src_dir = base_dir / rel
    if not src_dir.exists():
        return TrashMoveResult(image_path=image_path, src_dir=src_dir, trash_dir=trash_base_dir / rel, moved=False)

    if not _safe_under(base_dir, src_dir):
        raise RuntimeError("JailCheckFailed")

    trash_base_dir.mkdir(parents=True, exist_ok=True)
    candidate = trash_base_dir / rel
    if candidate.exists():
        candidate = trash_base_dir / rel.parent / f"{rel.name}__deleted__{item_id}__{request_id[:8]}"
    candidate.parent.mkdir(parents=True, exist_ok=True)

    if not _safe_under(trash_base_dir, candidate):
        raise RuntimeError("JailCheckFailed")

    src_dir.rename(candidate)
    return TrashMoveResult(image_path=image_path, src_dir=src_dir, trash_dir=candidate, moved=True)


def rollback_trashed_image_dir(result: TrashMoveResult) -> None:
    if not result.moved:
        return
    if not result.trash_dir.exists():
        return
    result.src_dir.parent.mkdir(parents=True, exist_ok=True)
    result.trash_dir.rename(result.src_dir)


def cleanup_trashed_image_dir(result: TrashMoveResult) -> None:
    if not result.moved:
        return
    if result.trash_dir.exists():
        _rmtree_robust(result.trash_dir, ignore_errors=True)
