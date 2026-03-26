# ADR-0004: Ontology Runtime and Soft Validation

Status: Accepted  
Stand: 2026-03-26

## Context
Die Ontologie ist ein zentrales fachliches Steuerungsmodell für Kategorien, Attribute, Value Sets und Mapping-Logik.
Bestandsdaten und Legacy-Daten machen jedoch ein hartes Enforcement in allen Pfaden kurzfristig riskant.

## Decision
Die Ontologie wird als First-Class-Architekturbaustein behandelt.
Aktuell wird ein Soft-Validation-/Normalisierungsmodell betrieben, ergänzt um Legacy-/Alias-Mapping.

## Rationale
- Fachliche Konsistenz wird erhöht
- Bestandskompatibilität bleibt erhalten
- Review-/Nacharbeitsprozesse werden unterstützt
- Runtime-Enforcement kann später schrittweise verschärft werden

## Consequences
- Ontologie-Änderungen sind architekturwirksam
- Mapping-/Validation-Verhalten muss dokumentiert und getestet werden
- Das ARD muss die Ontologie ausdrücklich als Architekturbaustein führen
