# CUSTOM_GPT_IMPLEMENTATION_SEQUENCE_V6.md

## Ziel
Saubere Reihenfolge für die praktische Umsetzung ohne Hin-und-Her zwischen Builder, Knowledge und Actions.

## Reihenfolge
1. Builder-Hinweistext gegen `CUSTOM_GPT_HINTTEXT_PROPOSED.md` prüfen und übernehmen
2. Description und Conversation Starters setzen
3. OpenAPI gegen `CUSTOM_GPT_ACTIONS_OPENAPI_PROPOSED.yaml` prüfen
4. Health-/Auth-Entscheidung treffen
5. Knowledge über `KNOWLEDGE_CapsuleWardrobeArchitect_v7_PROPOSED.md` synchronisieren
6. Preview-Testmatrix durchführen
7. Ergebnis und Abweichungen im Changelog / Review ergänzen

## Entscheidungstore
### Gate 1 – Builder sauber
- Hinweistext final
- Description final
- Starters final

### Gate 2 – Actions sauber
- Schema formal korrekt
- Health/Auth entschieden
- DELETE-Parameter sauber
- enum-Felder geprüft

### Gate 3 – Knowledge sauber
- Karen-Default synchron
- keine starre Vier-Fragen-Logik mehr
- API-/Health-Aussagen konsistent

### Gate 4 – Test bestanden
- Planungslogik
- CRUD
- Magic Link
- Modell/Actions
