# RUNBOOK – Capsule / Wardrobe Studio

## 1. Zweck

Dieses Runbook beschreibt den praktischen Arbeits- und Betriebsmodus für Capsule:

- lokale Entwicklung
- Quality Gates
- Release-/Push-Rhythmus
- Handoff
- VPS-Deployment-Vorbereitung
- Störungsdiagnose

## 2. Lokale Standardbefehle

### 2.1 Umgebung aktivieren

```powershell
cd C:\CapsuleWardrobeRAG
.\.venv\Scripts\Activate.ps1
```

### 2.2 Quality Gates

```powershell
python .\tools\run_quality_gates.py
```

Dieser Befehl ist der lokale Standard-Gate-Lauf.

### 2.3 Lokaler App-Start

```powershell
python -m src.server_entry
```

### 2.4 Wichtige lokale Prüfpfade

- Weboberfläche: `http://127.0.0.1:5002/?user=karen`
- API Health: `http://127.0.0.1:5002/api/v2/health`

## 3. Standard-Entwicklungsablauf

1. Branch / Arbeitsstand klären
2. Änderung implementieren
3. Tests / Gates laufen lassen
4. Doku aktualisieren, wenn:
   - Architektur geändert wurde
   - Runtime-/Deploy-Konzept geändert wurde
   - Handoff-relevante Zustände geändert wurden
   - neue Tranche / neuer Meilenstein abgeschlossen wurde
5. Commit
6. Push

## 4. Handoff-Regel

Bei Meilensteinen oder Übergaben müssen mindestens aktualisiert werden:

- `docs/PROJECT_STATE.md`
- Handoff-Artefakte / Handoff-Zusammenfassung
- relevante ADR(s), falls Entscheidungen verändert wurden

## 5. Release-/Push-Regel

Vor Push auf `main` mindestens:

```powershell
python .\tools\run_quality_gates.py
git status --short
git commit -m "<saubere Nachricht>"
git push origin main
```

## 6. Lokale Diagnose

### 6.1 Wenn Gates fehlschlagen

Die Artefakte liegen unter:

```text
docs\_ops\quality_gates\run_<timestamp>\
```

Relevante Dateien:

- `summary.md`
- `step_compileall.log`
- `step_ruff_critical.log`
- `step_pytest.log`
- `step_secret_scan_tracked.log`
- `step_live_smoke.log`

### 6.2 Wenn der Server nicht startet

Prüfen:

- `.env`
- Ports / Host-Konfiguration
- `src/server_entry.py`
- `src/runtime_config.py`
- `src/runtime_env.py`
- Pfade zur DB / Datenablage

## 7. Workspace Cleanup

Für lokale Inventur / Cleanup stehen bereit:

- `tools/workspace_inventory.py`
- `tools/workspace_cleanup_apply.py`
- `tools/workspace_cleanup_apply_safe.py`

Wichtig:
- `docs/_ops/`, `docs/_archive/`, `docs/_notebooklm/` bleiben lokal und sind in `.gitignore`
- Cleanup-Werkzeuge sind vorsichtig einzusetzen; Standard ist zuerst Inventur / Dry-Run

## 8. VPS-Betrieb – Zielzustand

Der Zielzustand ist:

- App läuft auf Windows-VPS
- ngrok läuft ebenfalls auf dem VPS
- Karen braucht lokal keinen Server
- ChatGPT Custom GPT und Website gehen gegen denselben VPS-Backend-Stand

Siehe dazu zusätzlich:

- `docs/DEPLOYMENT_TARGET_STATE.md`
- `docs/VPS_DEPLOYMENT_RUNBOOK.md`
