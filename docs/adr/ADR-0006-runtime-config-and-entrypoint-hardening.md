# ADR-0006: Runtime-Config- und Entrypoint-Härtung

## Status
Accepted

## Kontext
Nach den Tranches A-E sind die größten Fach-Hotspots bereits modularisiert. Ein verbleibender technischer Hotspot liegt jedoch in den Start- und Konfigurationspfaden:

- `src/server_entry.py` lädt `.env`, repariert `sys.path` und baut Uvicorn-Parameter inline zusammen.
- `src/settings.py` liest Umgebungsvariablen direkt und exponiert Kompatibilitäts-Globals.
- Start- und Laufzeitparameter sind damit funktional, aber noch verteilt.

Das erhöht Drift-Risiko bei lokalen Starts, Smoke-Runs und späteren Deploy-/Automationspfaden.

## Entscheidung
Tranche F trennt die technische Runtime-Verantwortung in drei klarere Ebenen:

1. `src/runtime_env.py`
   - Repo-Root
   - `.env`-Laden
   - `sys.path`-Bootstrap
   - generische Env-Getter und Pfad-Normalisierung

2. `src/runtime_config.py`
   - kanonisches Laden der Laufzeitkonfiguration
   - zentrale `RuntimeConfig`-Dataclass
   - Uvicorn-Parameter aus einer Stelle
   - Weitergabe als bestehende module-level Settings-Dict

3. Fassade/Kompatibilität
   - `src/settings.py` bleibt kompatibler Importpunkt
   - `src/server_entry.py` bleibt kompatibler Entrypoint

## Konsequenzen
### Positiv
- Weniger implizite Kopplung zwischen Startpfad und Settings-Modul
- Deterministischere Runtime-Parameter für lokale Starts und Gate-Smoke-Runs
- Relative Pfade werden weiterhin repo-root-stabil aufgelöst
- Bestehende Importpfade bleiben erhalten

### Negativ / Trade-offs
- Zwei zusätzliche Runtime-Module
- Start- und Konfigurationslogik ist expliziter, also etwas verteilter, dafür klarer getrennt

## Guardrails
- Kein Verhaltenswechsel an bestehenden Defaults
- `python -m src.server_entry` und `python src/server_entry.py` bleiben unterstützt
- `src.settings.reload_settings()` bleibt erhalten
- Gates bleiben Abnahmekriterium
