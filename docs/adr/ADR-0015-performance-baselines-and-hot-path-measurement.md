# ADR-0015: Performance baselines and hot-path measurement

## Status
Accepted

## Kontext

Nach Tranche A-N sind Struktur, Testarchitektur, Runtime-Pfade und Release-Governance deutlich robuster. Der nächste sinnvolle Reifeschritt ist eine reproduzierbare, billige Performance-Basis.

## Entscheidung

Wir führen eine kleine Performance-Schicht ein:

1. strukturierte Baseline-Artefakte unter `docs/_ops/performance/baselines/`
2. Import-Hotpaths als erste Messdomäne
3. separates Vergleichswerkzeug mit Toleranzschwelle
4. Nightly-Workflow für wiederkehrende Baselines

## Konsequenzen

### Positiv
- Performance wird messbar statt anekdotisch
- günstiger Einstieg ohne instabile End-to-End-Benchmarks
- spätere Erweiterung auf API-, DB- und Ontology-Hotpaths möglich

### Negativ
- noch keine harten Performance-Fail-Gates
- Importzeit ist nur ein Teil der Laufzeitrealität
