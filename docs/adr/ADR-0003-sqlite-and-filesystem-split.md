# ADR-0003: SQLite and Filesystem Split

Status: Accepted  
Stand: 2026-03-26

## Context
Wardrobe-Items enthalten strukturierte Metadaten und zugehörige Bildordner.
Eine rein datenbankzentrierte oder rein dateibasierte Persistenz wäre unpraktisch.

## Decision
Metadaten werden in SQLite gespeichert.
Bilder werden im Dateisystem gespeichert.
Beide Ebenen zusammen bilden den operativen Zustand.

## Rationale
- SQLite ist für lokale/produktnahe Persistenz leichtgewichtig und gut kontrollierbar
- Bilddateien sind im Filesystem operational einfacher zu handhaben
- Recovery-, trash-, quarantine- und handoff-nahe Prozesse sind dateisystemnah effizienter

## Consequences
- Konsistenz zwischen DB und Filesystem ist architekturkritisch
- Ingestion und Delete/Recovery müssen saga-safe bzw. reparierbar sein
- Schema- und Pfadänderungen sind dokumentations- und testpflichtig
