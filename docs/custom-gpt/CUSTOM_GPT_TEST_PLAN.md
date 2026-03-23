# CUSTOM_GPT_TEST_PLAN.md

**Zweck:** Verbindliche Preview-Testmatrix für den Capsule Wardrobe Architect.

---

## 1. Ziel

Der GPT wird nicht nur textlich beurteilt, sondern anhand realer Builder-Preview-Tests mit aktivierten Actions verifiziert.

---

## 2. Testgruppen

### A. Planungslogik

#### Test A1 – vollständiger Karen-Prompt
**Prompt:**  
`Ich bin Karen und brauche eine Capsule für drei Bürotage und ein Abendessen. Keine hohen Absätze, eher gedeckte Farben.`

**Erwartung:**  
- keine Rückfrage
- direkte Planung
- Teile-Liste
- Magic Link
- Visualisierungsfrage erst nach Textausgabe

#### Test A2 – Anlass fehlt
**Prompt:**  
`Ich brauche eine Capsule für vier Tage.`

**Erwartung:**  
- genau eine gezielte Rückfrage zum Anlass
- keine Formularlogik
- kein unnötiger Bestandscall vor Klärung

#### Test A3 – Andreas explizit
**Prompt:**  
`Hier ist Andreas. Plane mir eine kleine Business-Capsule für zwei Reisetage.`

**Erwartung:**  
- Andreas-Kontext wird übernommen
- kein Karen-Default
- Planung direkt oder mit minimal nötiger Rückfrage

#### Test A4 – Nutzer nicht explizit, Karen-Default
**Prompt:**  
`Plane mir bitte eine Business-Capsule für nächste Woche.`

**Erwartung:**  
- Karen als Default, sofern kein echter Konflikt vorliegt
- nicht automatisch „Andreas oder Karen?“ fragen

---

### B. Bestand und Analyse

#### Test B1 – Stärkste Teile
**Prompt:**  
`Zeig mir bitte, welche Teile aus meinem Bestand für eine Sommer-Capsule am stärksten sind.`

**Erwartung:**  
- sinnvoller Bestandscall
- keine unnötige Rückfrage, falls Nutzerkontext klar ist
- strukturierte Auswahl

---

### C. CRUD – Create

#### Test C1 – neues Teil per Foto anlegen
**Prompt:**  
`Ich möchte ein neues Teil per Foto anlegen und sauber kategorisieren lassen.`

**Erwartung:**  
- sauberer Create-Workflow
- nur erforderliche Nachfragen
- nach erfolgreichem Call Rückgabe mit neuer `#CW-ID`

---

### D. CRUD – Update

#### Test D1 – partielle Änderung
**Prompt:**  
`Ändere bitte die Daten von #CW-123, aber nur die Farbe und den Namen.`

**Erwartung:**  
- `getItem` vor Update
- PATCH nur mit geänderten Feldern
- keine Vollüberschreibung

---

### E. CRUD – Delete

#### Test E1 – Delete ohne Bestätigung
**Prompt:**  
`Lösche bitte #CW-123.`

**Erwartung:**  
- kein Delete-Call
- Anzeige / Vorprüfung
- explizite Bitte um Bestätigung

#### Test E2 – Delete mit Bestätigung
**Prompt:**  
`LÖSCHEN BESTÄTIGEN`

**Erwartung:**  
- nur dann Delete-Call
- klare Erfolgs- oder Fehlermeldung

---

### F. Runtime / Actions

#### Test F1 – Health-/Diagnoseverhalten
**Ziel:** prüfen, welcher Endpunkt und welche Auth-Regel real gelten.

**Zu dokumentieren:**
- `/healthz`
- `/api/v2/health`
- API-Key erforderlich: ja/nein

#### Test F2 – Modell mit Actions
**Ziel:** prüfen, ob das empfohlene Modell mit den Actions praktisch stabil arbeitet.

**Zu dokumentieren:**
- sichtbares Modell
- funktioniert `listItems`
- funktioniert `createItem`
- funktioniert `updateItem`
- Fallbacks / Auffälligkeiten

---

## 3. Testprotokoll-Format

Für jeden Test festhalten:
- Datum
- Builder-Version
- verwendetes Modell
- Eingabeprompt
- beobachtetes Verhalten
- erwartetes Verhalten erfüllt: ja/nein
- Befund / Folgeaktion

---

## 4. Exit-Kriterien

Die Testphase ist abgeschlossen, wenn:
- alle A- bis F-Tests dokumentiert sind
- alle kritischen Konflikte entschieden wurden
- keine unbeabsichtigten CRUD-Aktionen auftreten
- Magic-Link-Format konsistent ist
- Modell-/Action-Verhalten nachvollziehbar belegt ist
