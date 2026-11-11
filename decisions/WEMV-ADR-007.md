---
Document: Architecture Decision Record
Identifier: WEMV-ADR-007
Title: Add the WEM 1.3.0 validation profile
Status: Accepted
Created Date: 2026-11-11
ASI Level: 3
Decision Authority: Project Owner and Final Authority
WEM Reference: WEM 1.2.0 — Released
---

# WEMV-ADR-007 — Add the WEM 1.3.0 validation profile

## Identifier

`WEMV-ADR-007`

## Title

Add the WEM 1.3.0 validation profile

## Status

Accepted

## Created Date

2026-11-11

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-11 | Proposed | Project Owner and Final Authority | WEM 1.3.0 is Released and WEM-ADR-013 requires a compatible profile before a new project can receive an `Adopt` disposition. |
| 2026-11-11 | Accepted | Project Owner and Final Authority | The WEM 1.3.0 profile and the bounded fifth Milestone were approved. |

## Decision Authority

Project Owner and Final Authority

No delegation for this ASI-3 decision has been recorded.

## WEM Reference

WEM 1.2.0 — Released

## ASI Level

ASI-3 — Framework architecture

The decision adds a second versioned profile and changes how rule identifiers, sources and supported WEM references are bound to a profile across the profile registry, rule evaluator and lifecycle evaluator. It does not change the read-only boundary, source authority, report Schema or human authority and does not require an Architectural Pause.

## Context

WEM 1.3.0 was Released on 2026-11-07. Its Project Initiation specification requires every new Initiation Run to produce a Validator Adoption Disposition and names WEM Validator as the current reference product.

The validator exposed only the `wem-1.2.0` profile. A project declaring WEM 1.3.0 therefore received an unsupported finding for every ADR that referenced WEM 1.3.0, and `--profile wem-1.3.0` failed. Under WEM-ADR-013 such a project could only receive `Defer`. The WEM 1.3.0 release itself was validated with the WEM 1.2.0 profile.

Canonical-source comparison of `v1.2.0` and `v1.3.0` established that the structural requirements implemented by this product did not change:

- ADR Required Content, ADR Status values, Identifier Governance, Status History and ADR Lifecycle are unchanged between ADR Specification 1.1.0 and 1.2.0;
- ADR Specification 1.2.0 adds project-neutral interpretation of ASI levels, which is classification judgment rather than structure;
- foundation and specification frontmatter fields are unchanged;
- the Validator Adoption Disposition is transient Initiation content and is not a maintained artifact with a defined structure.

## Decision

The decision is to add a `wem-1.3.0` profile that applies the existing structural rule behavior with WEM 1.3.0 sources and supported references.

### Profile identity

The profile SHALL identify:

- profile identifier `wem-1.3.0`;
- WEM Reference `WEM 1.3.0 — Released`;
- independent profile implementation version 0.1.0;
- rule identifiers with prefix `WEMV130`;
- sources citing `ADR_SPECIFICATION.md@1.2.0` where the WEM 1.2.0 profile cites `ADR_SPECIFICATION.md@1.1.0`.

### Shared rule behavior

Both profiles SHALL derive their rules from one shared table of rule keys, sources and descriptions. Evaluators SHALL refer to shared rule keys and SHALL derive the profile-specific identifier from the selected profile.

The WEM 1.2.0 profile SHALL keep its identifiers, sources, limitations, implementation version 0.4.0 and observable output unchanged.

### Supported ADR references

Each profile SHALL declare the ADR WEM References it supports:

- `wem-1.2.0`: WEM 1.0.0 and WEM 1.2.0 — Released;
- `wem-1.3.0`: WEM 1.0.0, WEM 1.2.0 and WEM 1.3.0 — Released.

WEM 1.1.0 and Draft references remain unsupported in both profiles because their compatibility has not been separately confirmed.

### Selection and compatibility

The default profile SHALL remain `wem-1.2.0` so that existing invocations and manifests produce unchanged results. A caller SHALL select `wem-1.3.0` explicitly through `--profile` or a manifest. Implicit configuration discovery remains prohibited by the Validation Architecture.

The finding-report Schema remains Draft 0.3.0. The executable package advances from 0.3.0 to 0.4.0.

### Fifth-Milestone acceptance criteria

The bounded implementation SHALL demonstrate:

- unchanged WEM 1.2.0 profile behavior, including the golden report;
- identical findings, with only the profile prefix differing, for both profiles over the invalid fixture;
- a WEM 1.3.0 ADR reference that is unsupported under `wem-1.2.0` and accepted under `wem-1.3.0`;
- a profile inventory that cites WEM 1.3.0 sources only;
- manifest selection of `wem-1.3.0` and rejection of a conflicting command profile;
- validation of the WEM `v1.3.0` repository with the `wem-1.3.0` profile;
- formatting, linting, strict typing, automated tests, build and installed-wheel verification.

### Out of scope

The fifth Milestone SHALL NOT:

- validate ASI classification judgment, Validator Adoption Dispositions or release assurance content;
- add WEM 1.1.0 or Draft compatibility;
- change the default profile, report Schema or manifest format;
- add implicit configuration discovery, mutation, network access or certification;
- stabilize or release Draft interfaces, license the product or publish a package.

## Consequences

### Benefits

- projects declaring WEM 1.3.0 can validate their ADRs without unsupported findings;
- WEM-ADR-013 `Adopt` recommendations become possible for WEM 1.3.0 projects;
- adding later profiles requires a profile definition rather than duplicated rule code;
- findings remain traceable to the exact WEM version that defines them.

### Costs

- two profiles must be maintained and tested;
- the default profile does not follow the latest WEM release, so callers must select `wem-1.3.0` explicitly.

### Risks and Limitations

- a future WEM release may change structural rules that the shared table cannot express;
- a profile with unchanged rules may be mistaken for validation of WEM 1.3.0 judgment content;
- WEM 1.1.0 references remain unsupported even though their ADR requirements match.

### Mitigations

- declare WEM 1.3.0 judgment content as a profile limitation;
- compare canonical sources before each new profile;
- keep the shared-behavior test so that divergence is deliberate.

## Related Principles

- `WEM-P-003` — Explicit and Traceable Decisions — WEM 1.2.0;
- `WEM-P-004` — Proportional Governance — WEM 1.2.0;
- `WEM-P-006` — Canonical Source of Normative Knowledge — WEM 1.2.0;
- `WEM-P-008` — Knowledge Preservation Through Evolution — WEM 1.2.0.

## Alternatives Considered

### A. Change the existing profile to WEM 1.3.0

This option was rejected because it would change the meaning of existing results and rule identifiers for projects that declare WEM 1.2.0.

### B. Copy the rule evaluator for each profile

This option was rejected because identical behavior would be maintained twice and could diverge silently.

### C. Share rule behavior and bind identifiers, sources and supported references to each profile

This is the selected alternative.

### D. Make WEM 1.3.0 the default profile

This option was rejected for this Milestone because it would change existing invocations without a separate compatibility decision.

## Implementation Notes

The Project Owner accepted this decision and authorized the bounded fifth-Milestone implementation, its commit and push on 2026-11-11 through the instruction to perform all recommended steps with every necessary function. Claude Code performed the Architect and Builder functions.

Human Milestone acceptance remains a separate gate and is not pre-authorized by implementation permission. Claude Code authored this change and therefore is not its independent technical reviewer.

### Implementation Evidence

The bounded fifth-Milestone implementation:

- replaced the single profile definition with one shared rule table and two profiles;
- made rule and lifecycle findings derive identifiers from the selected profile;
- made supported ADR references a profile property;
- added the `wem-1.3.0` profile with implementation version 0.1.0;
- advanced the executable package to 0.4.0 and aligned `__version__`, which previously reported 0.1.0;
- added an ignore rule for Python bytecode caches created by local verification;
- added engine and CLI tests for the WEM 1.3.0 profile and shared behavior.

Verification completed on 2026-11-11:

```text
uv lock: wem-validator 0.3.0 -> 0.4.0
ruff format --check: passed
ruff check: passed
mypy strict: passed for 22 source files
pytest: 54 passed
WEM v1.3.0 repository, wem-1.3.0 profile, Git-aware: 0 errors, 0 warnings, 9 unsupported historical references
WEM Orchestrator, wem-1.3.0 profile, Git-aware: 0 findings
```

The nine unsupported findings are WEM 1.0.0 Draft and WEM 1.1.0 references, which remain outside declared compatibility.
