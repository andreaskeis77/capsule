# CUSTOM_GPT_KNOWLEDGE_SYNC_REVIEW.md

**Zweck:** Review und Synchronisationsvorschlag für `KNOWLEDGE_CapsuleWardrobeArchitect_v6.md`  
**Problem:** Das Knowledge-Dokument enthält noch alte Verhaltenslogik, die dem aktuellen Builder-Hinweistext widerspricht.

---

## 1. Hauptkonflikt

### Aktueller Knowledge-Stand
Unter **Phase 1 — Iteratives Briefing (zwingend)** steht derzeit sinngemäß:

1. „Für wen darf ich heute planen – Andreas oder Karen?“
2. Anlass
3. Tage
4. Präferenzen / No-Gos

Außerdem gilt dort:
- vor Vorschlägen oder API-Abfragen immer zuerst alle 4 Punkte klären

### Aktueller Builder-Sollstand
Der Builder-Hinweistext soll dagegen festhalten:
- Karen ist Default
- Andreas nur bei expliziter Nennung oder echter Unklarheit
- nur gezielt fehlende Informationen nachfragen
- keine starre Vierer-Formularlogik

### Bewertung
Das ist kein kosmetischer Unterschied, sondern ein echter Verhaltenskonflikt.  
Wenn das Knowledge unverändert bleibt, besteht das Risiko, dass der GPT je nach Retrieval oder Promptlage wieder in die alte starre Nutzerabfrage zurückfällt.

---

## 2. Welche Teile im Knowledge gut sind und bleiben sollen

Diese Inhalte des aktuellen Knowledge-Dokuments sind weiterhin wertvoll:
- Rolle und Mission
- Action-Namen und API-Bezug
- Magic-Link-Format
- harte CRUD-Prinzipien
- strukturierte Ausgaberegeln
- Visualisierungsstil
- CRUD-Workflows
- Debug-/Fehlerdiagnose
- Tonfall

Der Änderungsbedarf liegt **nicht** im gesamten Dokument, sondern primär in der Planungslogik und in der Health/Auth-Semantik.

---

## 3. Präzise Änderungsziele

### A. Nutzer-Default synchronisieren
Statt einer verpflichtenden Erstfrage nach Andreas/Karen soll gelten:
- Karen ist Standardnutzerin
- Andreas nur bei expliziter Nennung oder echter Unklarheit

### B. Missing-Info-Logik modernisieren
Statt:
- immer 4 Fragen
soll gelten:
- Prompt zuerst analysieren
- nur fehlende oder unklare Informationen nachfragen
- maximal 1–2 kurze Rückfragen
- Priorität: Anlass → Umfang → Präferenzen

### C. Bestandscalls nur bei Bedarf
Im Knowledge sollte klarer stehen:
- Bestand nur abrufen, wenn für die Aufgabe wirklich nötig
- kein reflexhaftes `listItems`, wenn der Prompt noch nicht planungsreif ist

### D. Health/Auth offen, aber sauber markieren
Im aktuellen Knowledge steht:
- `/api/v2/health` ohne Auth

Da Schema und Betriebsdoku dazu nicht vollständig synchron sind, sollte das Knowledge bis zur finalen Entscheidung nicht überhart eine Falschwahrheit behaupten.

---

## 4. Konkrete Soll-Änderungen im bestehenden Dokument

### 4.1 Abschnitt „2.1 API v2 (FastAPI, CRUD)“

**Aktuell problematisch:**  
`GET /api/v2/health → health (ohne Auth; Diagnose)`

**Soll-Ersatz:**  
`GET /api/v2/health → health (Diagnose-Endpunkt; Auth-Regel gemäß finaler Action-Konfiguration dokumentieren)`

---

### 4.2 Abschnitt „Phase 1 — Iteratives Briefing (zwingend)“

**Aktueller Abschnitt sollte vollständig ersetzt werden.**

**Soll-Inhalt:**
- Prompt zuerst analysieren
- Karen als Default
- Andreas nur bei expliziter Nennung oder echter Unklarheit
- für Planung werden Anlass, Umfang und ggf. Präferenzen benötigt
- nur fehlende Informationen gezielt nachfragen
- maximal 1–2 kurze Rückfragen
- keine starre Formularlogik
- bei expliziter CRUD-Anweisung direkt in CRUD-Workflow

---

## 5. Empfohlene Ersatzfassung für den Planungsabschnitt

```text
### Phase 1 — Iteratives Briefing (zwingend)

Bevor du eine Capsule planst oder den Bestand abrufst, analysierst du zuerst den Nutzerprompt.

Regeln:
- Karen ist der Standardnutzer.
- Andreas verwendest du nur dann als Nutzerkontext, wenn er explizit genannt wird oder der Prompt sonst wirklich unklar wäre.
- Wenn relevante Informationen bereits im Prompt enthalten sind, übernimmst du sie und fragst sie nicht erneut ab.
- Für eine belastbare Capsule brauchst du Anlass, Umfang (Tage oder Anzahl Outfits) und bei Bedarf Präferenzen oder No-Gos.
- Wenn genau eine entscheidende Information fehlt oder unklar ist, fragst du gezielt genau diese nach.
- Stelle maximal 1–2 kurze, dialogische Rückfragen.
- Verwende keine starre Formularlogik.

Priorität der Rückfragen:
1. Anlass
2. Umfang
3. Präferenzen / No-Gos

Ausnahme:
Bei expliziter CRUD-Anweisung (z. B. „Lege neu an“, „Ändere #CW-…“, „Lösche #CW-…“) gehst du direkt in den passenden CRUD-Workflow.
```

---

## 6. Empfehlung zur Struktur des nächsten Knowledge-Stands

Für die nächste offizielle Knowledge-Version sollte die Datei nicht komplett neu erfunden werden.  
Es reicht, sie kontrolliert zu synchronisieren:

1. Rolle & Mission
2. Actions / API
3. Harte Prinzipien
4. Capsule-Planung mit aktualisierter Missing-Info-Logik
5. Visualisierung
6. CRUD
7. Debug
8. Tonfall

Optional später:
- technische Betriebsdetails stärker auslagern
- Verhaltenslogik weiter in den Builder verlagern
- Knowledge stärker als Referenzwissen ausrichten
