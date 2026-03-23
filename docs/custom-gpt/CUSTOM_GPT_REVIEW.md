# CUSTOM_GPT_REVIEW.md

**Projekt:** Capsule Wardrobe Architect  
**Stand:** 2026-03-23  
**Status:** Review v4 / operative Soll-Konfiguration  
**Ziel:** Repo-taugliches Review des aktuellen Custom GPT inklusive Builder-Felder, Knowledge-Abgrenzung, Actions/OpenAPI und Test-/Freigabelogik.

---

## 1. Zielbild

Der Custom GPT **Capsule Wardrobe Architect** soll als produktionsnaher Assistent für zwei klar getrennte Modi arbeiten:

1. **Capsule-Planung aus realem Bestand**
2. **gezielte CRUD-Interaktion mit dem Wardrobe-Backend**

Standardnutzer ist **Karen**. **Andreas** wird nur bei expliziter Nennung oder tatsächlicher Unklarheit als alternativer Nutzerkontext behandelt.

Der GPT ist Teil des Zielbetriebsmodells, in dem der produktive Backend-Zugriff zentral über den VPS und die öffentliche Domain erfolgt, nicht mehr über lokale Laptop-Runtime.

---

## 2. Harte Review-Ergebnisse

### 2.1 Was bereits stark ist
- klare fachliche Rolle
- gute Missing-Info-Logik
- sinnvolle Trennung zwischen Planung und CRUD
- sauberes Magic-Link-Konzept
- gutes Zusammenspiel aus kurzem Hinweistext und Langkontext

### 2.2 Hauptprobleme
1. **Instructions und Knowledge sind nicht vollständig synchron**
2. **Health-/Auth-Semantik ist nicht sauber dokumentiert**
3. **Builder-Felder sind noch nicht vollständig ausgereift**
4. **OpenAPI-Schema ist funktional brauchbar, aber formal nachschärfbar**

---

## 3. Präzise Konsistenzkonflikte

### 3.1 Nutzer-Default
**Aktueller Builder-Hinweistext:** Karen ist Default.  
**Knowledge v6:** Vor Planungsbeginn immer zuerst fragen: Andreas oder Karen.

**Bewertung:** Verhaltenskonflikt.  
**Soll-Entscheidung:** Der Builder-Hinweistext ist führend. Knowledge muss angepasst werden.

### 3.2 Health-Endpunkte
**Handoff / produktiver Betrieb:** `/healthz` ist der maßgebliche Runtime-Smoke-Test.  
**Actions / Knowledge:** `/api/v2/health` wird als GPT-/API-Diagnose-Endpunkt geführt.

**Bewertung:** Nicht zwingend technisch falsch, aber dokumentarisch unsauber.  
**Soll-Entscheidung:** Beide Pfade getrennt dokumentieren:
- `/healthz` = externer Runtime-/Liveness-Endpunkt
- `/api/v2/health` = optionaler API-/GPT-Diagnose-Endpunkt

### 3.3 Auth für `/api/v2/health`
**Knowledge:** ohne Auth  
**Schema:** derzeit mit API-Key abgesichert

**Bewertung:** Konflikt.  
**Soll-Entscheidung:** Eine Wahrheit festlegen und dann Schema + Knowledge synchronisieren.

---

## 4. Builder-Review – Sollbild

Die operative Soll-Konfiguration besteht aus:
- präziser Name
- nicht-leere Beschreibung
- stabiler Hinweistext
- hochwertige Conversation Starters
- empfohlener Modellwert nur nach Action-Livetest
- klar getrennte Knowledge-Rolle
- gehärtete Actions

Siehe dazu auch `CUSTOM_GPT_FIELD_SPEC.md`.

---

## 5. Modell- und Produktlage (OpenAI)

Aktuelle OpenAI-Hilfeseiten bestätigen:
- GPTs werden über Instructions, Conversation Starters, Knowledge, Capabilities, Apps/Actions und Versionsverwaltung konfiguriert.
- Vor dem Teilen oder Veröffentlichen soll der GPT im Preview mit realen Prompts getestet werden.
- Actions benötigen saubere externe API-Konfiguration; bei öffentlicher Freigabe ist für öffentliche Actions eine gültige Privacy Policy URL erforderlich.
- Die Modelllandschaft in ChatGPT ist 2026 in Bewegung; Model-Picker, Retirements und Action-Kompatibilität müssen deshalb praktisch getestet und nicht nur angenommen werden.

Diese Punkte sind für dieses Projekt **betriebsrelevant**, nicht nur theoretisch.

---

## 6. Empfohlene unmittelbare Maßnahmen

### A – jetzt umsetzen
1. Beschreibung ergänzen
2. Conversation Starters finalisieren
3. Knowledge/Instructions-Konflikte dokumentieren
4. Health-/Auth-Semantik entscheiden
5. OpenAPI-Schema schärfen

### B – direkt danach
6. Preview-Testmatrix ausführen
7. Modell mit aktivierten Actions praktisch testen
8. Privacy-/Sharing-Readiness dokumentieren

### C – danach
9. Knowledge-Datei in „Regeln“ und „Referenzwissen“ entflechten
10. Hinweistext nur minimal und gezielt überarbeiten

---

## 7. Konkretes Soll-Ergebnis für den Builder

Die repo-fähige Soll-Konfiguration ist in diesen Dateien abgelegt:
- `CUSTOM_GPT_FIELD_SPEC.md`
- `CUSTOM_GPT_TEST_PLAN.md`
- `CUSTOM_GPT_ACTIONS_OPENAPI_PROPOSED.yaml`
- `CUSTOM_GPT_BUILDER_TEXTS.md`

---

## 8. Freigabekriterien

Der GPT gilt erst dann als „sauber reviewt“, wenn:

- die Builder-Felder final gepflegt sind
- das OpenAPI-Schema formal bereinigt ist
- Nutzer-Default, Health und Auth konsistent dokumentiert sind
- Preview-Tests für Planung und CRUD dokumentiert bestanden wurden
- Model-/Action-Verhalten praktisch gegengeprüft wurde
- Privacy-/Sharing-Relevanz festgehalten ist

---

## 9. Gesamturteil

Der GPT ist **fachlich gut** und **nah an produktiv brauchbar**, aber noch nicht vollständig gehärtet.  
Der größte Hebel liegt derzeit **nicht** in einer kreativen Neuschreibung des Hinweistexts, sondern in:

- Builder-Härtung
- Schema-Schärfung
- Konsistenzbereinigung
- dokumentierter Testbarkeit
