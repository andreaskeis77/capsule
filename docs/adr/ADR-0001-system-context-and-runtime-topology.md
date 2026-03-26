# ADR-0001: System Context and Runtime Topology

Status: Accepted  
Stand: 2026-03-26

## Context
Capsule Studio besteht nicht nur aus einer einzelnen API oder einer Template-Sammlung, sondern aus mehreren kooperierenden Laufzeit- und Betriebsbausteinen:
- API
- Dashboard/UI
- Persistence
- Filesystem
- Ontology Runtime
- Tooling / Handoff / Run Registry
- External Exposure / DNS / Hosting

Diese Zusammenhänge müssen als verbindlicher Systemkontext beschrieben werden.

## Decision
Das Projekt führt ein formales ARD ein und dokumentiert dort die Runtime-Topologie als verbindlichen Architekturrahmen.

Die Zieltopologie umfasst:
- FastAPI API v2
- Flask Dashboard, in FastAPI gemountet
- SQLite
- Dateisystem für Bilder
- Ontology Runtime
- Run Registry
- Handoff-/Snapshot-Tooling
- externe Komponenten: GitHub, Contabo, Cloudflare, INWX, ngrok

## Consequences
- Architektur ist nicht mehr implizit, sondern dokumentiert.
- Änderungen an Runtime, Exposure oder Infrastruktur werden ARD-/ADR-pflichtig.
