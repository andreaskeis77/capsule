#!/usr/bin/env python3
"""
Ontology Runtime Dump
Creates a "resolved" snapshot of the ontology inputs as used by the runtime:
- ontology_overrides.yaml
- color_lexicon.yaml
- ontology_part_*.md (index + optional text)

Outputs:
1) JSON (machine-readable): overrides + color lexicon + parts + file hashes
2) Markdown summary (human-readable)

Safe defaults:
- No secrets
- Includes MD parts text by default (can be disabled)
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_text_robust(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def list_ontology_parts(ontology_dir: Path) -> List[Path]:
    parts = sorted(
        [p for p in ontology_dir.glob("ontology_part_*.md") if p.is_file()],
        key=lambda p: p.name.lower(),
    )
    return parts


def build_parts_index(parts: List[Path], include_text: bool, max_chars: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in parts:
        st = p.stat()
        txt = read_text_robust(p)
        item: Dict[str, Any] = {
            "file": p.name,
            "rel_path": p.name,
            "size": int(st.st_size),
            "mtime_utc": dt.datetime.fromtimestamp(st.st_mtime, tz=dt.timezone.utc).replace(microsecond=0).isoformat(),
            "sha256": sha256_bytes(txt.encode("utf-8", errors="replace")),
            "line_count": txt.count("\n") + (1 if txt else 0),
        }
        if include_text:
            if len(txt) > max_chars:
                item["text"] = txt[:max_chars]
                item["text_note"] = f"TRUNCATED to {max_chars} chars"
            else:
                item["text"] = txt
        out.append(item)
    return out


def summarize_overrides(overrides: Any) -> Dict[str, Any]:
    if overrides is None:
        return {"present": False}

    if isinstance(overrides, dict):
        keys = sorted(list(overrides.keys()), key=lambda s: str(s).lower())
        return {
            "present": True,
            "type": "dict",
            "top_level_keys": keys,
            "top_level_key_count": len(keys),
        }

    # fallback
    return {"present": True, "type": type(overrides).__name__}


def summarize_color_lexicon(lex: Any) -> Dict[str, Any]:
    if lex is None:
        return {"present": False}

    if isinstance(lex, dict):
        keys = sorted(list(lex.keys()), key=lambda s: str(s).lower())
        return {
            "present": True,
            "type": "dict",
            "entries": len(keys),
            "sample_keys": keys[:15],
        }

    if isinstance(lex, list):
        return {
            "present": True,
            "type": "list",
            "entries": len(lex),
        }

    return {"present": True, "type": type(lex).__name__}


def main() -> int:
    ap = argparse.ArgumentParser(description="Create ontology runtime dump (json + summary md).")
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--ontology-dir", default="ontology", help="Ontology directory (relative to root)")
    ap.add_argument("--overrides", default="ontology/ontology_overrides.yaml", help="Overrides YAML (relative to root)")
    ap.add_argument("--color-lexicon", default="ontology/color_lexicon.yaml", help="Color lexicon YAML (relative to root)")
    ap.add_argument("--out-json", required=True, help="Output JSON path")
    ap.add_argument("--out-md", required=True, help="Output Markdown summary path")
    ap.add_argument("--include-part-text", action="store_true", help="Include ontology_part_*.md full text (default off)")
    ap.add_argument("--max-part-chars", type=int, default=250_000, help="Max chars per MD part when included")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    ontology_dir = (root / args.ontology_dir).resolve()
    overrides_path = (root / args.overrides).resolve()
    color_path = (root / args.color_lexicon).resolve()

    out_json = Path(args.out_json).resolve()
    out_md = Path(args.out_md).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    overrides_obj = load_yaml(overrides_path)
    color_obj = load_yaml(color_path)
    parts = list_ontology_parts(ontology_dir)
    parts_index = build_parts_index(parts, include_text=bool(args.include_part_text), max_chars=int(args.max_part_chars))

    payload: Dict[str, Any] = {
        "generated_utc": utc_now_iso(),
        "repo_root": str(root),
        "ontology_dir": str(ontology_dir),
        "inputs": {
            "overrides_file": str(overrides_path),
            "color_lexicon_file": str(color_path),
            "parts_count": len(parts),
            "include_part_text": bool(args.include_part_text),
            "max_part_chars": int(args.max_part_chars),
        },
        "files": {
            "overrides": {
                "exists": overrides_path.exists(),
                "sha256": sha256_file(overrides_path) if overrides_path.exists() else None,
            },
            "color_lexicon": {
                "exists": color_path.exists(),
                "sha256": sha256_file(color_path) if color_path.exists() else None,
            },
            "parts": [
                {
                    "file": p.name,
                    "sha256": sha256_file(p),
                }
                for p in parts
            ],
        },
        # "resolved" content (as used by runtime loaders)
        "resolved": {
            "ontology_overrides": overrides_obj,
            "color_lexicon": color_obj,
            "parts_index": parts_index,  # includes text only if include-part-text
        },
        "summary": {
            "overrides": summarize_overrides(overrides_obj),
            "color_lexicon": summarize_color_lexicon(color_obj),
            "parts": {
                "count": len(parts),
                "files": [p.name for p in parts],
            },
        },
    }

    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    # Markdown summary
    lines: List[str] = []
    lines.append("# Ontology Runtime Dump – Summary\n\n")
    lines.append(f"- generated_utc: {payload['generated_utc']}\n")
    lines.append(f"- ontology_dir: `{ontology_dir}`\n")
    lines.append(f"- overrides: `{overrides_path}`\n")
    lines.append(f"- color_lexicon: `{color_path}`\n")
    lines.append(f"- parts_count: {len(parts)}\n")
    lines.append(f"- include_part_text: {bool(args.include_part_text)}\n\n")
    lines.append("---\n\n")

    lines.append("## Inputs (hashes)\n\n")
    lines.append("| artifact | exists | sha256 |\n|---|:---:|---|\n")
    lines.append(f"| overrides | {'yes' if overrides_path.exists() else 'no'} | `{payload['files']['overrides']['sha256']}` |\n")
    lines.append(f"| color_lexicon | {'yes' if color_path.exists() else 'no'} | `{payload['files']['color_lexicon']['sha256']}` |\n")
    lines.append("\n")

    lines.append("## Color lexicon\n\n")
    cl = payload["summary"]["color_lexicon"]
    lines.append(f"- present: {cl.get('present')}\n")
    if cl.get("present"):
        lines.append(f"- type: {cl.get('type')}\n")
        if "entries" in cl:
            lines.append(f"- entries: {cl.get('entries')}\n")
        if "sample_keys" in cl:
            lines.append(f"- sample_keys: {', '.join(cl.get('sample_keys', []))}\n")
    lines.append("\n")

    lines.append("## Overrides\n\n")
    ov = payload["summary"]["overrides"]
    lines.append(f"- present: {ov.get('present')}\n")
    if ov.get("present"):
        lines.append(f"- type: {ov.get('type')}\n")
        if "top_level_key_count" in ov:
            lines.append(f"- top_level_key_count: {ov.get('top_level_key_count')}\n")
        if "top_level_keys" in ov:
            keys = ov.get("top_level_keys", [])
            lines.append(f"- top_level_keys: {', '.join(keys[:25])}{' ...' if len(keys) > 25 else ''}\n")
    lines.append("\n")

    lines.append("## Ontology parts\n\n")
    lines.append("| file | sha256 |\n|---|---|\n")
    for pinfo in payload["files"]["parts"]:
        lines.append(f"| `{pinfo['file']}` | `{pinfo['sha256']}` |\n")
    lines.append("\n")

    if args.include_part_text:
        lines.append("## Note\n\n")
        lines.append("`parts_index` in JSON includes `text` per file (possibly truncated).\n")

    out_md.write_text("".join(lines), encoding="utf-8", newline="\n")

    print(f"Ontology runtime JSON written to: {out_json}")
    print(f"Ontology summary MD written to: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())