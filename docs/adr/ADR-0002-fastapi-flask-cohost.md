# ADR-0002: FastAPI and Flask Co-Hosting

Status: Accepted  
Stand: 2026-03-26

## Context
Das Projekt besitzt sowohl eine API-Schicht als auch eine HTML-basierte Dashboard-/Admin-Oberfläche.
Statt zwei vollständig getrennte Deployments zu betreiben, werden beide Teile in einer gemeinsamen Runtime betrieben.

## Decision
FastAPI bleibt die primäre API-Schicht.
Flask bleibt als Dashboard-/Template-Schicht bestehen und wird in die gemeinsame Runtime integriert.

## Rationale
- Praktischer Betrieb mit einer lokalen Base URL
- Gemeinsame Nutzung von Datenbasis und Laufzeitkontext
- Geringere Betriebs- und Deploy-Komplexität
- Dashboard kann API v2 als Source of Truth nutzen

## Consequences
- UI/API-Kohärenz muss aktiv gesichert werden
- Legacy v1 bleibt nur soweit nötig erhalten
- Änderungen an Auth, Routing oder Error Contracts müssen beide Schichten berücksichtigen
