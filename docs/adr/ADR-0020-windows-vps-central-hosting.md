# ADR-0020: Windows VPS as central Capsule hosting target

## Status
Accepted

## Context
Capsule soll zentral betrieben werden, damit Karen keinen lokalen Server und keinen lokalen ngrok-Tunnel mehr braucht.  
Das Repo ist Windows-first geprägt und enthält bereits PowerShell-Entrypoints sowie einen lokalen `server_entry`-Pfad.

## Decision
Capsule wird zentral auf einem Windows-VPS betrieben.
- API/Web-App laufen lokal auf dem VPS
- Bind nur auf `127.0.0.1`
- Öffentliche Erreichbarkeit ausschließlich über ngrok auf dem VPS
- Betrieb über Windows Scheduled Tasks
- Updates über Git + Bootstrap + Restart

## Consequences
Vorteile:
- ein zentraler Laufzeitstand
- Karen braucht keinen Laptop-Server mehr
- klarer Update- und Diagnosepfad

Nachteile:
- VPS wird kritischer Single Runtime Point
- ngrok bleibt Bestandteil des Betriebsmodells
