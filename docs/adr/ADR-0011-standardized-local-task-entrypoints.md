# ADR-0011: Standardized local task entrypoints

## Status
Accepted

## Context
The repository already contains robust operational scripts and quality gates, but local invocation paths are still fragmented across direct Python calls, ad-hoc PowerShell usage, and Windows-specific startup files.

## Decision
Introduce a single lightweight task runner (`tools/task_runner.py`) and a Windows-first wrapper (`capsule.cmd`) as the canonical developer entrypoint surface.

## Consequences
- Common developer actions use one predictable command family.
- VS Code can bind to the same entrypoints without duplicating logic.
- Existing operational scripts remain source-of-truth implementations.
- Future onboarding instructions can reference one command surface instead of many file paths.
