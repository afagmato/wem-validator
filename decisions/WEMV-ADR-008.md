---
Document: Architecture Decision Record
Identifier: WEMV-ADR-008
Title: License WEM Validator under Apache-2.0
Status: Accepted
Created Date: 2026-11-12
ASI Level: 4
Decision Authority: Project Owner and Final Authority
WEM Reference: WEM 1.2.0 — Released
---

# WEMV-ADR-008 — License WEM Validator under Apache-2.0

## Identifier

`WEMV-ADR-008`

## Title

License WEM Validator under Apache-2.0

## Status

Accepted

## Created Date

2026-11-12

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-12 | Proposed | Project Owner and Final Authority | The repository became public, but without a license it grants no permission to use, copy or modify the product. |
| 2026-11-12 | Accepted | Project Owner and Final Authority | Apache-2.0 was selected after evaluation of Apache-2.0, MIT and continued absence of a license. |

## Decision Authority

Project Owner and Final Authority

## WEM Reference

WEM 1.2.0 — Released

## ASI Level

ASI-4 — Repository and architectural structure

Licensing governs every artifact, every future contribution and the conditions under which other projects can adopt the product. Reversal would require relicensing published content. WEM classified its own licensing decision, WEM-ADR-004, as ASI-4.

## Context

The Project Owner authorized public visibility of `afagmato/wem-validator` on 2026-11-12 so that projects outside the Project Owner's control can evaluate an `Adopt` disposition under WEM-ADR-013. A public repository without a license grants no permission to use, copy, modify or distribute its content. Visibility alone therefore did not make adoption possible.

The Charter reserves licensing to the Project Owner. WEM itself is licensed under CC BY-SA 4.0, which suits documentation but is not intended for software.

The Architectural Pause for this decision consisted of the Project Owner evaluating three alternatives with their consequences before selecting one.

## Decision

The decision is to license all WEM Validator repository content under the Apache License, Version 2.0.

- The root `LICENSE` file SHALL contain the unmodified official license text from `https://www.apache.org/licenses/LICENSE-2.0.txt`.
- Package metadata SHALL declare the SPDX expression `Apache-2.0` and include the license file in source and wheel distributions.
- The license applies to the current content and to all published history.
- The license does not authorize package publication, a product release or stabilization of the Draft CLI, manifest or JSON interfaces. Those remain separate Project Owner decisions.

## Consequences

### Positive Consequences

- other projects may use, modify and redistribute the validator, so an `Adopt` disposition becomes legally possible;
- Apache-2.0 includes an explicit patent grant and a contribution clause;
- the license is widely recognized by organizations and tooling.

### Negative Consequences

- redistributors must preserve the license and notices, and state significant changes;
- the product license differs from the CC BY-SA 4.0 license of the WEM method.

### Risks and Limitations

- the license does not make the Draft interfaces stable; adopters must still treat them as Draft;
- the decision does not cover third-party content, of which the repository currently has none.

## Related Principles

- `WEM-P-002` — Separation of Knowledge and Products — WEM 1.2.0;
- `WEM-P-003` — Explicit and Traceable Decisions — WEM 1.2.0;
- `WEM-P-007` — Human Accountability — WEM 1.2.0.

## Alternatives Considered

### A. Apache-2.0

Permissive, with an explicit patent grant and contribution terms. This is the selected alternative.

### B. MIT

Permissive and minimal, but without a patent grant. Not selected.

### C. No license for now

Keeps all rights reserved, but leaves the public repository unusable by other projects. Not selected.

## Implementation Notes

The Project Owner selected Apache-2.0 on 2026-11-12 and authorized its implementation, commit and push. Claude Code implemented it.

The official text was downloaded from `https://www.apache.org/licenses/LICENSE-2.0.txt` on 2026-11-12. It has 202 lines and SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
