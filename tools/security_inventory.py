from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SECURITY_DIR = REPO_ROOT / "docs" / "_ops" / "security"
BRANCH_PROTECTION_CONTRACT = REPO_ROOT / ".github" / "branch-protection.required-checks.json"

RE_PINNED = re.compile(r"^[A-Za-z0-9_.\-]+(?:\[[A-Za-z0-9_,.\-]+\])?==[^\s]+$")
RE_REQUIREMENT = re.compile(r"^[A-Za-z0-9_.\-]+(?:\[[A-Za-z0-9_,.\-]+\])?(?:[<>=!~].+)?$")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_requirements_text(text: str) -> list[str]:
    requirements: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if " #" in line:
            line = line.split(" #", 1)[0].rstrip()
        if not line:
            continue
        parts = [part.strip() for part in line.split() if part.strip() and not part.startswith("#")]
        requirements.extend(parts)
    return requirements


def parse_requirements_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path.relative_to(REPO_ROOT)) if path.is_absolute() and path.is_relative_to(REPO_ROOT) else str(path),
            "exists": False,
            "total": 0,
            "pinned": 0,
            "unpinned": 0,
            "invalid": [],
            "entries": [],
        }

    entries = _parse_requirements_text(path.read_text(encoding="utf-8"))
    pinned = [entry for entry in entries if RE_PINNED.match(entry)]
    valid = [entry for entry in entries if RE_REQUIREMENT.match(entry)]
    invalid = [entry for entry in entries if entry not in valid]
    return {
        "path": str(path.relative_to(REPO_ROOT)) if path.is_absolute() and path.is_relative_to(REPO_ROOT) else str(path),
        "exists": True,
        "total": len(entries),
        "pinned": len(pinned),
        "unpinned": len(valid) - len(pinned),
        "invalid": invalid,
        "entries": entries,
    }


def _control(path: Path, label: str, required: bool = True) -> dict[str, Any]:
    exists = path.exists()
    try:
        rel_path = str(path.relative_to(REPO_ROOT))
    except ValueError:
        rel_path = str(path)
    return {
        "label": label,
        "path": rel_path,
        "required": required,
        "present": exists,
    }


def gather_security_inventory(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    requirements = parse_requirements_file(repo_root / "requirements.txt")
    controls = [
        _control(repo_root / ".env.example", "Environment example without checked-in secrets"),
        _control(repo_root / "tools" / "secret_scan.py", "Tracked secret scan tool"),
        _control(repo_root / ".github" / "workflows" / "quality-gates.yml", "Required quality gates workflow"),
        _control(repo_root / ".github" / "workflows" / "security-hygiene-nightly.yml", "Nightly security hygiene workflow", required=False),
        _control(repo_root / ".github" / "dependabot.yml", "Dependabot configuration", required=False),
        _control(repo_root / "docs" / "SECURITY.md", "Security operations documentation", required=False),
    ]
    branch_contract: dict[str, Any] = {
        "exists": False,
        "required_status_checks": [],
        "required_review_count": None,
    }
    contract_path = repo_root / ".github" / "branch-protection.required-checks.json"
    if contract_path.exists():
        contract = _load_json(contract_path)
        branch_contract = {
            "exists": True,
            "required_status_checks": contract.get("required_status_checks", []),
            "required_review_count": contract.get("required_review_count"),
            "require_code_owner_reviews": bool(contract.get("require_code_owner_reviews")),
            "require_conversation_resolution": bool(contract.get("require_conversation_resolution")),
        }

    required_controls = [item for item in controls if item["required"]]
    optional_controls = [item for item in controls if not item["required"]]
    required_ok = all(item["present"] for item in required_controls)
    optional_present = sum(1 for item in optional_controls if item["present"])

    return {
        "generated_at": _utc_now_iso(),
        "repo_root": str(repo_root),
        "requirements": requirements,
        "controls": controls,
        "required_controls_present": required_ok,
        "optional_controls_present": optional_present,
        "optional_controls_total": len(optional_controls),
        "branch_protection_contract": branch_contract,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    req = payload["requirements"]
    lines = [
        "# Security Inventory",
        "",
        f"Generated at: {payload['generated_at']}",
        "",
        "## Requirements",
        "",
        f"- File: `{req['path']}`",
        f"- Total entries: {req['total']}",
        f"- Pinned entries: {req['pinned']}",
        f"- Unpinned entries: {req['unpinned']}",
        f"- Invalid entries: {len(req['invalid'])}",
        "",
        "## Controls",
        "",
    ]
    for control in payload["controls"]:
        state = "present" if control["present"] else "missing"
        required = "required" if control["required"] else "optional"
        lines.append(f"- [{state}] {control['label']} — `{control['path']}` ({required})")
    bp = payload["branch_protection_contract"]
    lines.extend([
        "",
        "## Branch Protection Contract",
        "",
        f"- Contract file present: {bp['exists']}",
        f"- Required status checks: {len(bp['required_status_checks'])}",
        f"- Required review count: {bp['required_review_count']}",
    ])
    if bp["required_status_checks"]:
        for check in bp["required_status_checks"]:
            lines.append(f"  - `{check}`")
    return "\n".join(lines) + "\n"


def write_inventory(payload: dict[str, Any], output_dir: Path = SECURITY_DIR) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "security_inventory_latest.json"
    md_path = output_dir / "security_inventory_latest.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a lightweight security inventory for the repository.")
    parser.add_argument("--write", action="store_true", help="Write the inventory into docs/_ops/security.")
    args = parser.parse_args()
    payload = gather_security_inventory()
    if args.write:
        json_path, md_path = write_inventory(payload)
        print(f"[OK] wrote security inventory: {json_path}")
        print(f"[OK] wrote security inventory: {md_path}")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
