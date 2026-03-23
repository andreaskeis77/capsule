from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from tools.reporting_common import to_repo_rel, utc_now_iso, write_json, write_markdown
except Exception:  # pragma: no cover
    from reporting_common import to_repo_rel, utc_now_iso, write_json, write_markdown  # type: ignore


COMMON_PATTERNS: list[tuple[str, str, str]] = [
    ("PSSecurityException", "powershell_execution_policy", "PowerShell execution policy blocked script execution."),
    ("UnicodeEncodeError", "encoding", "A Windows console or file encoding mismatch interrupted a tool."),
    ("UnauthorizedAccess", "powershell_execution_policy", "PowerShell refused to run the script because of execution policy."),
    ("Connection refused", "server_connectivity", "The live smoke step could not reach the local server."),
    ("No successful quality gate run found", "missing_quality_gate_history", "Release evidence could not find a prior successful quality gate run."),
    ("AssertionError", "test_assertion", "A regression test assertion failed."),
    ("Traceback", "python_exception", "A Python exception interrupted the step."),
]


def load_summary(run_dir: str | Path) -> dict[str, Any]:
    path = Path(run_dir) / "summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def classify_step_failure(step_name: str, text: str) -> dict[str, str]:
    for needle, code, explanation in COMMON_PATTERNS:
        if needle in text:
            return {
                "step": step_name,
                "category": code,
                "explanation": explanation,
                "matched_on": needle,
            }
    if step_name == "pytest":
        return {
            "step": step_name,
            "category": "test_failure",
            "explanation": "Pytest reported at least one failing or erroring test.",
            "matched_on": "step_name",
        }
    if step_name == "ruff_critical":
        return {
            "step": step_name,
            "category": "lint_or_compile_error",
            "explanation": "Ruff found a critical Python problem such as syntax, name, or compile-time issues.",
            "matched_on": "step_name",
        }
    if step_name == "secret_scan_tracked":
        return {
            "step": step_name,
            "category": "secret_scan_finding",
            "explanation": "The tracked-file secret scan reported at least one finding or scanner failure.",
            "matched_on": "step_name",
        }
    if step_name == "live_smoke":
        return {
            "step": step_name,
            "category": "runtime_smoke_failure",
            "explanation": "The runtime smoke test could not complete successfully.",
            "matched_on": "step_name",
        }
    return {
        "step": step_name,
        "category": "unknown_failure",
        "explanation": "The step failed, but no known failure signature matched the log output.",
        "matched_on": "fallback",
    }


def build_diagnosis(summary: dict[str, Any], *, repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    steps = list(summary.get("steps", []))
    failures: list[dict[str, Any]] = []
    for step in steps:
        if int(step.get("returncode", 0)) == 0:
            continue
        log_rel = str(step.get("log_file", ""))
        log_path = root / log_rel
        text = _read_text(log_path)
        classification = classify_step_failure(str(step.get("name", "unknown")), text)
        failures.append(
            {
                **classification,
                "returncode": int(step.get("returncode", 0)),
                "log_file": to_repo_rel(log_path, root),
                "log_excerpt": text[-1200:] if text else "",
            }
        )

    status = "OK" if not failures else "FAIL"
    return {
        "generated_at_utc": utc_now_iso(),
        "status": status,
        "failed_steps": [f["step"] for f in failures],
        "failure_count": len(failures),
        "failures": failures,
    }


def write_diagnosis(run_dir: str | Path, diagnosis: dict[str, Any]) -> tuple[Path, Path]:
    run_path = Path(run_dir)
    json_path = write_json(run_path / "diagnosis.json", diagnosis)

    lines = [
        "# Quality Gate Diagnosis",
        "",
        f"- Generated (UTC): {diagnosis['generated_at_utc']}",
        f"- Status: {diagnosis['status']}",
        f"- Failure count: {diagnosis['failure_count']}",
        "",
    ]
    if diagnosis["failures"]:
        lines.extend(["## Failed steps", ""])
        for failure in diagnosis["failures"]:
            lines.extend(
                [
                    f"### {failure['step']}",
                    "",
                    f"- Category: `{failure['category']}`",
                    f"- Return code: `{failure['returncode']}`",
                    f"- Log file: `{failure['log_file']}`",
                    f"- Matched on: `{failure['matched_on']}`",
                    f"- Explanation: {failure['explanation']}",
                    "",
                ]
            )
    else:
        lines.extend(["## Failed steps", "", "- None. All required steps passed.", ""])
    md_path = write_markdown(run_path / "diagnosis.md", lines)
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and summarize quality gate failures for a run directory.")
    parser.add_argument("run_dir", help="Path to docs/_ops/quality_gates/run_<timestamp>")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    summary = load_summary(run_dir)
    diagnosis = build_diagnosis(summary, repo_root=run_dir.parents[3])
    json_path, md_path = write_diagnosis(run_dir, diagnosis)
    print(f"[OK] diagnosis written: {json_path}")
    print(f"[OK] diagnosis written: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
