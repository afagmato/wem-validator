---
Document: Architecture Decision Record
Identifier: WEMV-ADR-002
Title: Establish versioned read-only validation architecture
Status: Accepted
Created Date: 2026-11-03
ASI Level: 4
Decision Authority: Project Owner and Final Authority
WEM Reference: WEM 1.2.0 — Released
---

# WEMV-ADR-002 — Establish versioned read-only validation architecture

## Identifier

`WEMV-ADR-002`

## Title

Establish versioned read-only validation architecture

## Status

Accepted

## Created Date

2026-11-03

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-03 | Proposed | Project Owner and Final Authority | ASI-4 Architectural Pause opened to establish validation boundaries and the rule-source model before product implementation. |
| 2026-11-04 | Accepted | Project Owner and Final Authority | Versioned read-only validation architecture approved and controlled materialization authorized. |

## Decision Authority

Project Owner and Final Authority

## WEM Reference

WEM 1.2.0 — Released

## Context

WEM Validator exists to provide deterministic structural validation for WEM repositories and adopting-project governance artifacts. It must encode executable checks without becoming a competing source of WEM normative knowledge.

The first Milestone needs a narrow vertical slice covering frontmatter, relative links and ADR structure under WEM 1.2.0. A durable architecture is required before selecting implementation technology because rule provenance, version selection, read-only behavior, findings and unsupported cases constrain every later component.

The decision establishes product responsibility boundaries and the relationship between canonical WEM releases and executable rule profiles. It was therefore classified as ASI-4 — Repository and architectural structure. The Project Owner closed the Architectural Pause on acceptance.

## Decision

The decision is to build a provider-independent, deterministic and read-only validation engine around explicitly selected, versioned validation profiles derived from Released WEM sources.

### Authority boundary

Released WEM specifications and decisions remain authoritative. WEM Validator rules SHALL be derived product behavior with traceable source references, not independent normative definitions.

Successful validation SHALL mean only that the supplied inputs satisfy the checks implemented by the selected profile. It SHALL NOT constitute certification, substantive architectural review, human acceptance or release approval.

### Architectural responsibilities

The product SHALL separate these responsibilities:

1. **Input boundary** — obtain bounded local bytes and explicitly authorized Git observations without executing target repository code.
2. **Profile selection** — select one exact supported WEM version and status; no implicit `latest` profile may determine behavior.
3. **Document parsing** — convert supported Markdown, frontmatter and repository observations into a deterministic internal representation.
4. **Rule evaluation** — apply provider-independent rules without network access, current time or hidden process state.
5. **Finding projection** — produce equivalent human-readable and machine-readable findings from the same evaluated result.
6. **Operational adapters** — expose filesystem, Git and command-line effects outside the validation core.

The core SHALL NOT contain AI-provider types, private conversational context, remote-service assumptions or repository mutation capabilities.

### Versioned validation profiles

Every validation run SHALL explicitly select a supported profile associated with one Released WEM version.

Each implemented rule SHALL have:

- a stable product rule identifier;
- the exact validation-profile version;
- a reference to the authoritative WEM document version and applicable requirement or structural contract;
- deterministic inputs and finding conditions;
- valid, invalid and unsupported fixtures where applicable;
- an explicit severity or disposition that does not imply human authority.

Rule identifiers and findings SHALL remain product interfaces. They SHALL NOT replace WEM principle identifiers, ADR identifiers or normative language.

When the product cannot evaluate a required construct safely or completely, it SHALL return an explicit unsupported, unavailable or incomplete finding rather than silently pass it.

### Read-only execution

The initial architecture SHALL:

- read only explicitly selected local targets;
- bound file size, file count and traversal scope;
- reject path escape outside the authorized target;
- avoid symbolic-link traversal unless a later decision defines safe semantics;
- perform no target code execution;
- perform no network request;
- make any Git observation explicit and read-only;
- perform no automatic correction or repository action.

### Findings contract

Every finding SHALL identify at least:

- rule identifier;
- selected validation profile;
- outcome category;
- affected path;
- location when deterministically available;
- bounded explanation;
- authoritative source reference;
- limitations or unavailable context when applicable.

Human-readable and JSON output SHALL be projections of the same finding model. Exit status SHALL distinguish successful evaluation with no findings, successful evaluation with findings and evaluation failure.

The exact JSON Schema and compatibility policy are an ASI-2 or ASI-3 public-interface decision to be proposed after this architectural boundary is accepted.

### First Milestone boundary

The first implementation Milestone SHALL target only WEM 1.2.0 — Released and SHALL provide one read-only vertical slice that:

1. selects the exact WEM 1.2.0 profile;
2. parses bounded local Markdown inputs;
3. validates required frontmatter presence and supported lifecycle values;
4. validates relative Markdown links without network access;
5. validates required ADR sections and conditional Alternatives Considered applicability;
6. emits deterministic human-readable and JSON findings;
7. verifies each implemented rule with valid, invalid and unsupported fixtures;
8. runs against a read-only checkout of the WEM `v1.2.0` tag without modifying it.

The Milestone SHALL NOT claim complete WEM conformity and SHALL expose the implemented-rule inventory and known gaps.

### Deferred decisions

This decision does not select:

- implementation language or dependency policy;
- CLI syntax or final JSON Schema;
- packaging or distribution mechanism;
- license;
- remote hosting or CI provider;
- support for WEM 1.0.0, 1.1.0 or Draft 1.3.0;
- automatic correction, certification or hosted-service responsibilities.

Those decisions SHALL be classified and governed before their affected implementation begins.

## Consequences

### Positive Consequences

- validation behavior is reproducible and tied to an exact Released method version;
- canonical WEM authority remains outside the executable product;
- provider-independent rules can run locally and in future CI environments;
- unsupported coverage remains visible;
- one finding model prevents drift between human and JSON output;
- read-only operation limits the impact of validator defects.

### Negative Consequences

- each supported WEM version requires maintained profiles and fixtures;
- source references can require deliberate migration when canonical documents evolve;
- strict bounds may reject very large or unusual repositories;
- structural validation cannot determine whether an engineering decision is substantively good.

### Risks and Limitations

- derived rules may accidentally strengthen or weaken canonical requirements;
- permissive Markdown parsing may hide malformed inputs while overly strict parsing may reject intended forms;
- filesystem and symbolic-link behavior differs across platforms;
- Git history-dependent checks cannot run from every exported directory;
- dogfooding against WEM remains self-referential without unrelated adopting projects.

### New Responsibilities

- maintain rule provenance and profile compatibility;
- review every rule against its authoritative Released source;
- preserve deterministic fixtures and findings;
- disclose unsupported checks and validation gaps;
- prevent adapters from introducing mutation or provider coupling into the core.

## Alternatives Considered

### Alternative A — Encode checks directly against the current WEM repository shape

This is quick to implement. It couples behavior to one evolving working tree, obscures version support and risks treating incidental repository state as normative.

### Alternative B — Interpret normative prose dynamically at validation time

This reduces explicit rule maintenance. It is not deterministic, cannot provide stable compatibility and risks delegating normative interpretation to an AI provider or heuristic parser.

### Alternative C — Maintain explicit versioned profiles with authoritative source traceability

This requires deliberate profile and fixture maintenance. It preserves deterministic behavior, exact version selection and the distinction between canonical norms and executable product rules. This is the selected alternative.

## ASI Level

ASI-4 — Repository and architectural structure.

The decision establishes durable product boundaries, source authority, rule-profile architecture and mutation constraints. Reversal after implementation would affect every parser, rule, adapter, fixture and public finding.

## Related Principles

- `WEM-P-001` — Responsibility Before Structure;
- `WEM-P-002` — Separation of Knowledge and Products;
- `WEM-P-003` — Explicit and Traceable Decisions;
- `WEM-P-004` — Proportional Governance;
- `WEM-P-005` — Technology-Independent Method;
- `WEM-P-006` — Canonical Source of Normative Knowledge;
- `WEM-P-007` — Human Accountability;
- `WEM-P-008` — Knowledge Preservation Through Evolution.

## Related Specifications and Decisions

- `PROJECT_CHARTER.md` Version 0.1.0 — Draft;
- `decisions/WEMV-ADR-001.md` — Accepted;
- WEM `WEM.md` Version 1.2.0 — Released;
- WEM `ENGINEERING_PRINCIPLES.md` Version 1.0.0 — Released;
- WEM `specifications/ADR_SPECIFICATION.md` Version 1.1.0 — Released;
- WEM `specifications/PROJECT_INITIATION.md` Version 1.0.0 — Released.

## Implementation Notes

The Project Owner accepted this ADR on 2026-11-04 and closed the Architectural Pause.

The accepted decision authorizes controlled materialization of its Draft architecture specification and preparation of the first Milestone. It does not select an implementation language or authorize product code, test fixtures, licensing, a remote, commit, push or publication.

---

End of WEMV-ADR-002
