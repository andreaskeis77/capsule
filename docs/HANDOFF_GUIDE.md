# Handoff Guide

## Ziel

Ein Handoff muss reproduzierbar zeigen:
- welchen Stand das Repo hat
- welche Gates zuletzt grün waren
- welche Artefakte vorliegen
- welcher nächste Arbeitsschritt offen ist

## Minimaler Handoff-Ablauf

1. Repo aufräumen
2. Quality Gates ausführen
3. Handoff-/Snapshot-Artefakte erzeugen
4. `latest.md`, `HANDOFF_MANIFEST.md`, `runtime_state.md` und relevante `_ops`-Artefakte zusammenstellen
5. offenen nächsten Schritt dokumentieren

## Pflichtbelege

- letzter erfolgreicher Quality-Gate-Lauf
- aktueller Project State
- aktueller Runtime State
- Handoff Manifest
- nächste Tranche / nächster Task

## Lesereihenfolge für den Übernehmer

1. `docs/PROJECT_STATE.md`
2. `docs/HANDOFF_MANIFEST.md`
3. `docs/RUNBOOK.md`
4. `docs/ARCHITECTURE.md`
5. `docs/DEVELOPER_WORKFLOW.md`
