# ENGINEERING_GUIDELINES â€“ Wardrobe Studio (AI-assisted Engineering)

Stand: 2026-02-15  
Scope: Dieses Dokument definiert verbindlich, wie wir am Repo arbeiten, damit Ã„nderungen reproduzierbar, Ã¼berprÃ¼fbar und chat-Ã¼bergreifend stabil bleiben.

---

## 1) Arbeitsmodus (verbindlich)

### 1.1 Schritt-fÃ¼r-Schritt (Single Step Rule)
- Pro Runde wird **genau ein** klarer Schritt ausgefÃ¼hrt (ein Test oder eine Ã„nderung).
- Keine Mehrfach-Aufgaben in einem Rutsch (â€žmach mal A, B, Câ€œ).
- Nach jedem Schritt: **Output/Logs zeigen**, dann erst weiter.

### 1.2 Keine Vermutungsfixes
- Keine â€žich glaube, das ist esâ€œ-Ã„nderungen ohne Messung.
- Erst **Beobachtung â†’ Hypothese â†’ minimaler Fix â†’ Verifikation**.

### 1.3 VollstÃ¤ndige Datei-Ausgabe bei Ã„nderungen
- Wenn eine Datei geÃ¤ndert werden soll: es wird **immer der vollstÃ¤ndige neue Dateiinhalt** geliefert (nicht nur Diff-Fragmente).
- Nach Ã„nderung: lokaler Run/Test + `git diff` PrÃ¼fung.

---

## 2) Definition of Done (DoD) pro Ã„nderung

Eine Ã„nderung gilt erst als â€ždoneâ€œ, wenn:

1. **Reproduzierbarkeit:** Schritte sind in RUNBOOK/Projektstatus nachvollziehbar.
2. **Test/Run:** Ã„nderung lokal ausgefÃ¼hrt und erwartetes Verhalten bestÃ¤tigt.
3. **Diff geprÃ¼ft:** `git diff` ist gelesen und plausibel.
4. **Keine Artefakte:** logs, snapshots, venv etc. sind nicht versehentlich im Repo.
5. **Commit sauber:** sinnvoller Commit-Text, kleiner Scope.

---

## 3) Debugging-Protokoll (Root Cause First)

### 3.1 Standard-Vorgehen
1. **Reproduzieren** (minimaler Fall).
2. **Eingrenzen** (welches Modul / welche Datei / welcher Layer).
3. **Beobachten** (Logs, Exceptions, Exit Codes).
4. **Hypothese** (1 Hypothese zur Zeit).
5. **Minimaler Fix** (kleinste mÃ¶gliche Ã„nderung).
6. **Verifizieren** (Run + erwartetes Ergebnis).
7. **Dokumentieren** (PROJECT_STATE / RUNBOOK wenn relevant).

### 3.2 PowerShell-spezifisch (PS 5.1)
Wenn PowerShell-Skripte zicken:
- **Parser/Token prÃ¼fen** statt blind â€ž-replaceâ€œ.
- Bei String/Quote-Problemen: **Script-Teil isolieren** oder **neu schreiben**.
- Keine â€žSmart Quotesâ€œ (Unicode AnfÃ¼hrungszeichen).
- String-Interpolation beachten:
  - `"$var:"` ist gefÃ¤hrlich â†’ verwende `"{0}:" -f $var` oder `${var}`.
- Encoding konsistent: UTF-8 (ohne exotische Zeichen, wenn mÃ¶glich).

### 3.3 Encoding-Regeln
- Repo-Standard: UTF-8.
- Keine gemischten Zeilenenden absichtlich; CRLF unter Windows ist ok.
- Bei merkwÃ¼rdigem Verhalten: Datei auf â€žSmart Quotesâ€œ / versteckte Unicode-Zeichen prÃ¼fen.

---

## 4) Git-Regeln (Governance)

### 4.1 Commits
- Kleine, thematisch saubere Commits.
- Commit-Message: **Imperativ + klarer Scope**, z. B.  
  - `Fix snapshot generator for PS 5.1`
  - `Improve dashboard filtering UI`
- Kein â€žWIPâ€œ-Commit im Hauptzweig (main) auÃŸer im Ausnahmefall.

### 4.2 Repo-Hygiene
Diese Dinge gehÃ¶ren **nicht** ins Repo:
- `.venv/`, `.venv_*`, `.venv_broken_*`
- `logs/`
- `docs/_snapshot/`
- `__pycache__/`, `*.pyc`
- groÃŸe lokale Artefakte/Exports (auÃŸer bewusst versioniert)

---

## 5) Handoff / Chat-Umzug Standard

Ziel: Chatwechsel ohne Kontextverlust.

### 5.1 Vor dem Umzug
1. Snapshot erzeugen:
   - `.\tools\handoff_snapshot.ps1`
   - optional: `.\tools\handoff_snapshot.ps1 -IncludeLogs`
2. `docs/PROJECT_STATE.md` kurz aktualisieren (Stand, nÃ¤chste Schritte).
3. `git status` muss sauber sein (oder bewusst nur die beabsichtigten Ã„nderungen).

### 5.2 Startprompt im neuen Chat
- Kurzbeschreibung Ziel + aktueller Fokus
- Snapshot aus `docs/_snapshot/latest.md` in den Chat kopieren
- Hinweis: â€žSingle Step Ruleâ€œ gilt

---

## 6) Lessons Learned (aus konkreten VorfÃ¤llen)

### 6.1 Snapshot-Script/PowerShell
- Regex-â€žHotfixesâ€œ auf Skripte sind riskant (Parser kann trotzdem brechen).
- Bei Parserfehlern: lieber **strukturierter Neuaufbau** als 10 kleine Replacements.
- Token/AST-Analyse ist schneller und verlÃ¤sslicher als Trial-and-Error.

### 6.2 AI-Assist Regeln
- Keine Scheinsicherheit: wenn unklar â†’ explizit sagen, was unklar ist.
- Bei fehlendem Kontext: gezielt **eine** Info anfordern, nicht 5 Fragen.
- Ã„nderungen immer so klein wie mÃ¶glich halten und sofort verifizieren.

---

## 7) Praktische Standardbefehle

### 7.1 Status
- `git status`
- `git diff`
- `git log --oneline -n 5`

### 7.2 Snapshot
- `.\tools\handoff_snapshot.ps1`
- `.\tools\handoff_snapshot.ps1 -IncludeLogs`

### 7.3 Server (manuell)
- `.venv\Scripts\python.exe -m src.server_entry`

### 7.4 Health Checks
- `http://127.0.0.1:5002/healthz`
- `http://127.0.0.1:5002/api/v2/health`

---
