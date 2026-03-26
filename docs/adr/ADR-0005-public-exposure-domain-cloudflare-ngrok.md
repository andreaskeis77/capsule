# ADR-0005: Public Exposure via Domain, Cloudflare and ngrok

Status: Accepted  
Stand: 2026-03-26

## Context
Das Projekt besitzt sowohl lokale Entwicklungs-/Betriebszugriffe als auch Anforderungen an kontrollierte externe Erreichbarkeit.
Dabei existieren mehrere externe Bausteine:
- Domain
- Registrar
- DNS/Proxy Layer
- Tunnel-Lösung
- VPS Hosting

## Decision
Die externe Sicht wird dokumentiert und architektonisch fest verankert:
- Domain: `capsule-studio.de`
- Registrar: INWX
- DNS / Proxy: Cloudflare
- Controlled public tunnel: ngrok
- Hosted target environment: Contabo VPS

## Rationale
- Externe Erreichbarkeit ist kein Nebenaspekt, sondern Teil der Betriebsarchitektur
- Sicherheits-, DNS- und Exposure-Entscheidungen müssen nachvollziehbar bleiben
- Handoffs und Betriebsdokumentation brauchen konkrete Infrastrukturreferenzen

## Consequences
- Änderungen an Domain, DNS, Tunnel oder Proxying sind ARD-/ADR-pflichtig
- Public Exposure muss als Sicherheits- und Betriebsaspekt mitgeführt werden
