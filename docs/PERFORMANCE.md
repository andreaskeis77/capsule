# Performance

## Ziel

Tranche O führt eine schlanke, reproduzierbare Basis für Performance-Messung ein, ohne die Fachlogik zu destabilisieren.

## Enthaltene Werkzeuge

- `tools/perf_baseline.py` erstellt strukturierte Baseline-Artefakte unter `docs/_ops/performance/baselines/`
- `tools/perf_compare.py` vergleicht zwei Baselines und markiert Regressionen über einer Toleranz
- `tools/perf_hotpaths.py` misst zunächst Import-Hotpaths als stabile, günstige Baseline

## Warum Import-Hotpaths zuerst

Import- und Bootstrap-Zeiten sind in frühen Reifephasen ein guter erster Indikator:

- billig messbar
- deterministischer als End-to-End-Responsezeiten
- hilfreich für Startpfade, CLI-Tasks und lokale Entwicklerzyklen

## Standardablauf lokal

```powershell
python .\tools\perf_hotpaths.py
```

Danach liegt ein neuer Lauf unter:

```text
/docs/_ops/performance/baselines/run_<timestamp>_import_hotpaths/
```

## Vergleich zweier Baselines

```powershell
python .\tools\perf_compare.py --baseline <path-to-old-summary.json> --candidate <path-to-new-summary.json> --tolerance-pct 10
```

## Leitplanken

- keine harten Performance-Fail-Gates in `run_quality_gates.py`
- erst Baselines sammeln, dann Grenzwerte definieren
- Messungen als Evidenz behandeln, nicht als Bauchgefühl
