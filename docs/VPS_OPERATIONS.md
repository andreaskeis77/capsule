# VPS Operations

## Standardbetrieb
Normaler Alltag:
1. lokal entwickeln
2. lokal Quality Gates grün
3. commit + push
4. auf dem VPS `vps_update_from_git.ps1`
5. `vps_smoke_test.ps1`

## Keine lokalen Server mehr für Karen
Karen soll nur noch:
- den Custom GPT verwenden
- oder die Website verwenden

Nicht mehr:
- lokalen ngrok-Tunnel starten
- lokalen Python-Server starten

## Sicherheitsprinzip
- API bindet lokal auf `127.0.0.1`
- externer Zugriff nur über ngrok
- OpenAI-Schlüssel nur serverseitig
- `.env` bleibt VPS-lokal und wird nicht ins Repo committed

## Betriebsregeln
- Keine Hotfixes direkt auf dem VPS ohne Git
- Keine manuellen Änderungen im laufenden Repo ohne Commit
- Updates nur über `main`
- Vor jedem VPS-Update lokal grüne Gates
