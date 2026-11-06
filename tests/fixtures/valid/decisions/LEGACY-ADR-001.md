Document: Architecture Decision Record

Identifier: LEGACY-ADR-001

Title: Preserve a valid historical ADR representation

Status: Accepted

Created Date: 2026-01-01

ASI Level: ASI-4

Decision Authority: Project Owner

WEM Reference: WEM 1.0.0 — Released

---

# LEGACY-ADR-001 — Preserve a valid historical ADR representation

## Identifier

LEGACY-ADR-001

## Title

Preserve a valid historical ADR representation

## Status

Accepted

## Created Date

2026-01-01

## Status History

| Status | Date | Authority | Reason |
| --- | --- | --- | --- |
| Proposed | 2026-01-01 | Project Owner | Evaluation opened. |
| Accepted | 2026-01-02 | Project Owner | Decision approved. |

## Decision Authority

Project Owner

## WEM Reference

WEM 1.0.0 — Released

## Context

Historical adopting projects may use a maintained field preamble instead of frontmatter.

## Decision

Preserve the representation while normalizing its ADR facts for validation.

## Consequences

The validator must separate WEM content requirements from presentation syntax.

## ASI Level

ASI-4 — Repository and architectural structure

## Related Principles

- `WEM-P-005` — Technology-Independent Method — WEM 1.0.0.
- `WEM-P-008` — Knowledge Preservation Through Evolution — WEM 1.0.0.

## Alternatives Considered

### Rewrite the historical artifact

Rejected because the original representation remains valid.

### Normalize supported facts in the validator

Selected because it preserves knowledge without imposing presentation syntax.
