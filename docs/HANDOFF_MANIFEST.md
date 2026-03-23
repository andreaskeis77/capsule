# HANDOFF_MANIFEST – Capsule

## 1. Zweck

Ein Handoff muss so geschrieben sein, dass ein neuer Chat oder ein anderer Bearbeiter ohne Rekonstruktion aus diffusen Einzelständen weiterarbeiten kann.

## 2. Pflichtinhalt jedes Handoffs

Jedes Handoff enthält mindestens:

1. **Ziel / Kontext**
   - woran wird gearbeitet?
   - warum ist das relevant?

2. **Ist-Stand**
   - Commit / Branch
   - relevanter technischer Stand
   - relevante Betriebsannahmen

3. **Letzter validierter Zustand**
   - letzter erfolgreicher Gate-Lauf
   - relevante Artefaktpfade
   - besondere Warnungen / bekannte Grenzen

4. **Änderungsumfang**
   - betroffene Dateien / Module
   - Doku-Änderungen
   - Deploy-Impact

5. **Offene Punkte**
   - Fehler
   - Entscheidungen
   - Risiken
   - nächste Blocker

6. **Nächster konkreter Schritt**
   - genau ein robuster Startpunkt
   - kein allgemeines „weitermachen“, sondern ein umsetzbarer Folgebefehl oder Arbeitsschritt

## 3. Qualitätsregeln

- Keine unpräzisen Zustandsbehauptungen
- Keine unbelegten „sollte gehen“-Formulierungen
- Keine Handoffs nur als Chat-Roman
- Immer mit einem technisch belastbaren Einstiegspunkt enden

## 4. Artefaktquellen

Falls vorhanden, sollen Handoffs auf folgende Artefaktgruppen verweisen:

- `docs/PROJECT_STATE.md`
- `docs/RUNBOOK.md`
- letzte Quality-Gate-Artefakte
- Release-Evidence / Readiness-Reports
- relevante ADRs

## 5. Projektbezogene Zusatzregel

Für Capsule muss im Handoff klar stehen:

- ob Karen lokal hosten muss oder nicht
- welcher Zugriffspfad aktuell maßgeblich ist:
  - lokales Dashboard
  - VPS-URL
  - ChatGPT Custom GPT
  - Website
- ob der aktuelle Stand bereits auf dem VPS deployed wurde oder nur lokal / im Repo vorliegt
