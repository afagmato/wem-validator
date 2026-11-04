---
Document: Architecture Decision Record
Identifier: WEMV-ADR-001
Title: Establish incremental responsibility-based repository governance
Status: Accepted
Created Date: 2026-11-03
ASI Level: 4
Decision Authority: Project Owner and Final Authority
WEM Reference: WEM 1.2.0 — Released
---

# WEMV-ADR-001 — Establish incremental responsibility-based repository governance

## Identifier

`WEMV-ADR-001`

## Title

Establish incremental responsibility-based repository governance

## Status

Accepted

## Created Date

2026-11-03

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-03 | Proposed | Project Owner and Final Authority | ASI-4 Architectural Pause opened to establish repository and decision governance before structural expansion. |
| 2026-11-04 | Accepted | Project Owner and Final Authority | Incremental responsibility-based repository governance approved and architecture materialization authorized. |

## Decision Authority

Project Owner and Final Authority

## WEM Reference

WEM 1.2.0 — Released

## Context

The accepted WEM Validator Foundation Package authorized a local Git repository and one maintained `PROJECT_CHARTER.md`. The repository has no commits, remote, implementation, license or speculative directory structure.

The first Milestone will require durable decisions, product architecture, executable implementation and verification fixtures. Their locations must be predictable without copying the complete WEM repository layout or creating empty structure in advance.

The repository also requires an ADR identifier namespace distinct from WEM and WEM Orchestrator. Repository placement and decision governance are durable structural choices and were therefore classified as ASI-4 — Repository and architectural structure. The Project Owner closed the Architectural Pause on acceptance.

## Decision

The decision is to use an incremental, responsibility-based repository architecture.

### Canonical locations

The repository root SHALL contain only active project-wide entry artifacts and tool configuration whose responsibility genuinely spans the repository.

The initial canonical locations SHALL be:

| Location | Responsibility |
| --- | --- |
| `PROJECT_CHARTER.md` | Project identity, mission, scope and final authority |
| `decisions/` | WEM Validator Architecture Decision Records |
| `specifications/` | Maintained product architecture and public-contract specifications |
| `src/wem_validator/` | Executable product implementation |
| `tests/` | Automated verification, fixtures and architectural checks |

Additional directories such as `documentation/`, `knowledge/`, `scripts/` or provider-specific adapter locations SHALL be introduced only when a current accepted responsibility has its first real artifact.

Acceptance of this ADR SHALL NOT itself create `specifications/`, `src/` or `tests/`. Each directory SHALL be activated with its first authorized artifact in the same structural operation.

### Decision governance

- WEM Validator ADR identifiers SHALL use the permanent sequence `WEMV-ADR-NNN`.
- ADR files SHALL use the exact canonical path `decisions/WEMV-ADR-NNN.md`.
- ADR content, lifecycle and authority SHALL follow the ADR governance applicable under WEM 1.2.0 — Released.
- Historical ADR entries SHALL NOT be overwritten when status changes.
- Accepted decisions SHALL remain historical records when superseded or retired.
- A decision SHALL reference the WEM version and status under which it was governed.

### Repository actions

The initial branch is `main`.

Remote hosting, initial commit, push, merge policy, release tags and publication remain separately authorized repository actions. Accepting this ADR SHALL NOT authorize any of them.

### Provider adapters

Provider-specific repository entry files are not part of the initial structure. They MAY be introduced later when a real participant interface requires them, but SHALL remain non-normative adapters to canonical project knowledge.

### Initial structural application

The accepted bounded PI-5 and PI-6 preparation may:

- retain `PROJECT_CHARTER.md` at the root;
- retain this ADR and subsequent WEM Validator ADRs in `decisions/`;
- create the first architecture specification in `specifications/` only with its authorized content;
- defer product and test directories until the first implementation Milestone is authorized.

No empty directory SHALL be created merely to display the intended final tree.

## Consequences

### Positive Consequences

- every directory corresponds to an active responsibility;
- ADRs remain distinct from specifications and executable product artifacts;
- the repository can grow without an up-front framework skeleton;
- provider-specific files cannot silently become product governance;
- Git history can preserve structural evolution as responsibilities become real.

### Negative Consequences

- the visible tree will remain intentionally incomplete during early initiation;
- contributors cannot assume that conventional directories exist before their first authorized artifact;
- later responsibilities may require separately governed structural additions.

### Risks and Limitations

- a broad root-level configuration file could accumulate unrelated responsibilities;
- directory activation could be mistaken for architecture approval when it is only implementation of an accepted decision;
- naming conventions alone do not prevent duplicated normative content.

### New Responsibilities

- maintain canonical placement as responsibilities evolve;
- preserve ADR identifier uniqueness and status history;
- review new directories against actual responsibility rather than convention.

## Alternatives Considered

### Alternative A — Keep every artifact at the repository root

This minimizes early directories. It makes decisions, specifications, product code and fixtures increasingly difficult to distinguish and does not scale beyond the foundation.

### Alternative B — Create a complete conventional repository skeleton immediately

This makes the eventual shape visible. It creates empty and speculative structure before responsibilities and implementation choices are accepted.

### Alternative C — Activate responsibility-based locations incrementally

This preserves a small initial repository while establishing durable canonical boundaries. Structure appears only with real artifacts. This is the selected alternative.

## ASI Level

ASI-4 — Repository and architectural structure.

The decision establishes durable canonical locations, ADR identity governance and the rules by which future repository structure becomes active. Reversal after implementation would require coordinated file movement and reference migration.

## Related Principles

- `WEM-P-001` — Responsibility Before Structure;
- `WEM-P-002` — Separation of Knowledge and Products;
- `WEM-P-003` — Explicit and Traceable Decisions;
- `WEM-P-004` — Proportional Governance;
- `WEM-P-006` — Canonical Source of Normative Knowledge;
- `WEM-P-008` — Knowledge Preservation Through Evolution.

## Related Specifications and Decisions

- `PROJECT_CHARTER.md` Version 0.1.0 — Draft;
- WEM `specifications/ADR_SPECIFICATION.md` as released with WEM 1.2.0;
- WEM `specifications/REPOSITORY_BLUEPRINT.md` as released with WEM 1.2.0;
- WEM `specifications/PROJECT_INITIATION.md` Version 1.0.0 — Released.

## Implementation Notes

The Project Owner accepted this ADR on 2026-11-04 and closed the Architectural Pause.

The accepted repository architecture authorized controlled materialization without commit, remote, push, publication or product implementation. The first architecture specification activates `specifications/` with real content in the same operation.

---

End of WEMV-ADR-001
