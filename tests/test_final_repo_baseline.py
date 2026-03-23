from pathlib import Path

import tools.final_repo_baseline as baseline


def test_build_baseline_payload_collects_expected_sections(tmp_path):
    repo = tmp_path
    for name in ["docs", "src", "tests", "tools", "ontology", "templates"]:
        (repo / name).mkdir(parents=True, exist_ok=True)
    for name in ["README.md", "pytest.ini", "requirements.txt", "pyproject.toml"]:
        (repo / name).write_text("", encoding="utf-8")

    adr = repo / "docs" / "adr"
    adr.mkdir(parents=True)
    (adr / "ADR-0001-test.md").write_text("# ADR\n", encoding="utf-8")
    (adr / "ADR-INDEX.md").write_text("# Index\n", encoding="utf-8")
    (repo / "tests" / "test_alpha.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    payload = baseline.build_baseline_payload(repo)

    assert payload["repo_name"] == repo.name
    assert payload["top_level_contract"]["src"] is True
    assert payload["adr"]["count"] == 1
    assert payload["adr"]["index_present"] is True
    assert payload["tests"]["count"] == 1


def test_write_baseline_report_writes_json(tmp_path):
    payload = {"ok": True}
    target = tmp_path / "docs" / "_ops" / "baseline" / "out.json"

    written = baseline.write_baseline_report(payload, target, tmp_path)

    assert written == target
    assert target.exists()
    assert '"ok": true' in target.read_text(encoding="utf-8").lower()
