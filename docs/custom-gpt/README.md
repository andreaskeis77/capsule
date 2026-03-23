# README.md

Diese Ablage enthält den Review- und Soll-Stand für den Custom GPT **Capsule Wardrobe Architect**.

## Dateien
- `CUSTOM_GPT_REVIEW.md` – Gesamtreview
- `CUSTOM_GPT_FIELD_SPEC.md` – Builder-Felder als Soll-Spezifikation
- `CUSTOM_GPT_TEST_PLAN.md` – Preview-Testmatrix
- `CUSTOM_GPT_BUILDER_TEXTS.md` – konkrete Builder-Texte
- `CUSTOM_GPT_ACTIONS_OPENAPI_PROPOSED.yaml` – vorgeschlagenes gehärtetes OpenAPI
- `CUSTOM_GPT_HINTTEXT_PROPOSED.md` – minimale Soll-Fassung des Hinweistexts
- `CUSTOM_GPT_CHANGELOG.md` – Änderungsprotokoll
- `CUSTOM_GPT_REVIEW_DELTA_V5.md` – neue Erkenntnisse in v5

## Reihenfolge für die Umsetzung
1. Builder-Felder prüfen und Description/Conversation Starters setzen
2. Hinweistext gegen `CUSTOM_GPT_HINTTEXT_PROPOSED.md` prüfen
3. OpenAPI gegen `CUSTOM_GPT_ACTIONS_OPENAPI_PROPOSED.yaml` abgleichen
4. Health/Auth-Semantik entscheiden
5. Preview-Testplan durchführen
6. Knowledge-Datei an finalen Builder-Stand anpassen
