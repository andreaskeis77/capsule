from pathlib import Path


def test_vps_deployment_files_exist():
    required = [
        Path("deploy/windows-vps/example.vps-settings.ps1"),
        Path("deploy/windows-vps/vps_bootstrap.ps1"),
        Path("deploy/windows-vps/vps_install_tasks.ps1"),
        Path("deploy/windows-vps/vps_run_api.ps1"),
        Path("deploy/windows-vps/vps_run_ngrok.ps1"),
        Path("deploy/windows-vps/vps_smoke_test.ps1"),
        Path("deploy/windows-vps/vps_update_from_git.ps1"),
        Path("deploy/windows-vps/ngrok.template.yml"),
        Path("docs/VPS_DEPLOYMENT_RUNBOOK.md"),
        Path("docs/VPS_CUTOVER_CHECKLIST.md"),
        Path("docs/VPS_OPERATIONS.md"),
    ]
    for path in required:
        assert path.exists(), f"missing deployment file: {path}"


def test_vps_settings_contract_contains_core_variables():
    content = Path("deploy/windows-vps/example.vps-settings.ps1").read_text(encoding="utf-8")
    for token in [
        "$CapsuleRepoRoot",
        "$CapsulePythonExe",
        "$CapsuleBindHost",
        "$CapsuleBindPort",
        "$NgrokExe",
        "$NgrokConfigPath",
        "$NgrokAuthtoken",
        "$CapsuleApiTaskName",
        "$CapsuleNgrokTaskName",
    ]:
        assert token in content
