---
Document: Architecture Decision Record
Identifier: WEMV-ADR-006
Title: Make ADR validation format-independent and WEM-reference-aware
Status: Accepted
Created Date: 2026-11-06
ASI Level: 3
Decision Authority: Project Owner and Final Authority
WEM Reference: WEM 1.2.0 — Released
---

# WEMV-ADR-006 — Make ADR validation format-independent and WEM-reference-aware

## Identifier

`WEMV-ADR-006`

## Title

Make ADR validation format-independent and WEM-reference-aware

## Status

Accepted

## Created Date

2026-11-06

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-06 | Proposed | Project Owner and Final Authority | The first external adoption pilot exposed invalid format assumptions and cascading historical false positives. |
| 2026-11-06 | Accepted | Project Owner and Final Authority | Format-independent ADR normalization, WEM-reference-aware evaluation and the bounded fourth Milestone were approved. |

## Decision Authority

Project Owner and Final Authority

No delegation for this ASI-3 decision has been recorded.

## WEM Reference

WEM 1.2.0 — Released

## ASI Level

ASI-3 — Framework architecture

## Context

The accepted third Milestone was tested read-only against WEM Orchestrator, the first external adopting project. The filesystem run produced ten findings and the Git-aware run produced eighty-nine findings while leaving target files, Git references and repository status unchanged.

Audit against the canonical WEM 1.0.0 and WEM 1.2.0 ADR specifications established that WEM requires ADR content and lifecycle semantics but does not require a particular file format. WEM Orchestrator ADRs 001 through 009 contain the required content in a maintained field preamble and canonical sections under their historical WEM 1.0.0 references. The validator incorrectly required YAML-like frontmatter and the history evaluator consequently reported seventy-nine identity failures for records whose identities were present but encoded differently.

One independent finding was valid: WEMO-ADR-010 is an ASI-5 decision governed by WEM 1.2.0 and lacks the required `Alternatives Considered` section.

The correction changes coordinated parsing, normalized document identity, rule evaluation, history observation and profile behavior. It is therefore classified ASI-3. It does not change the read-only boundary, human authority, WEM source authority or public release status and does not require an Architectural Pause.

## Decision

The decision is to normalize ADR identity and lifecycle facts from supported document representations before applying provider-independent WEM rules.

### Normalized ADR model

The parser SHALL support equivalent ADR facts obtained from:

- bounded YAML-like frontmatter;
- a bounded leading field preamble terminated before document content;
- canonical ADR sections when a required identity value is not available in another supported representation.

Supported representation syntax is product behavior, not WEM normative knowledge. The validator SHALL NOT report missing frontmatter as a WEM conformance error when equivalent required content is available through another supported representation.

An unrecognized representation SHALL produce an explicit unsupported result when required facts cannot be extracted. It SHALL NOT be silently accepted and SHALL NOT be misreported as a missing WEM requirement that the source specification does not impose.

### WEM Reference dispatch

Every ADR SHALL be evaluated according to its extracted `WEM Reference` when a rule depends on versioned semantics.

The WEM 1.2.0 profile MAY normalize historical WEM 1.0.0 ADR identity and lifecycle facts only for requirements confirmed as shared by both Released specifications. That compatibility does not constitute a complete WEM 1.0.0 validation profile.

Unsupported, malformed or ambiguous WEM references SHALL remain explicit. Historical ADRs SHALL NOT be retroactively required to adopt the physical representation used by later WEM repository artifacts.

### Status History normalization

Status History tables SHALL be normalized by recognized column meaning rather than one fixed column order. The initial implementation SHALL recognize:

- `Date`;
- `Status`;
- `Decision Authority` or the historical alias `Authority`;
- `Reason`.

Column order MAY vary. Missing, duplicate or unknown required columns SHALL make lifecycle extraction unsupported or invalid as applicable. Row preservation SHALL continue to compare normalized semantic entries.

### Compatibility and reporting

The WEM 1.2.0 profile implementation version SHALL advance from 0.3.0 to 0.4.0 because observable rule behavior changes. The executable package SHALL advance from 0.2.0 to 0.3.0.

The finding-report Schema remains Draft 0.3.0 because its structure does not change. Existing rule identifiers SHALL be preserved where their responsibility remains compatible. Rule descriptions and limitations SHALL be corrected to remove the invalid frontmatter assumption.

### Fourth-Milestone acceptance criteria

The bounded implementation SHALL demonstrate:

- zero frontmatter or history-identity findings for valid supported field-preamble ADRs;
- preservation of existing frontmatter validation behavior;
- normalized Status History evaluation across both supported column orders;
- explicit unsupported results for ADR facts that cannot be extracted safely;
- continued detection of the missing `Alternatives Considered` section in WEMO-ADR-010;
- a repeated read-only pilot against WEM Orchestrator with exactly the independently verified material finding and no cascading identity findings;
- unchanged target files, Git status and Git references during the pilot;
- formatting, linting, strict typing, automated tests, build and installed-wheel verification.

### Out of scope

The fourth Milestone SHALL NOT:

- implement arbitrary Markdown or every possible decision-record format;
- claim a complete WEM 1.0.0 profile;
- rewrite historical adopting-project ADRs solely to match WEM repository presentation;
- modify WEM Orchestrator except for the separately authorized WEMO-ADR-010 documentation remediation;
- add mutation, repair, remote access, provider integration or certification;
- stabilize or release Draft interfaces;
- create a remote, push, tag, license, publication, release or distribution.

## Consequences

### Benefits

- WEM conformance is separated from repository-specific presentation;
- external adopting projects can retain valid historical representations;
- history findings reflect missing knowledge rather than parser coupling;
- the first real pilot becomes reproducible evidence instead of a false-positive cascade;
- the actual WEMO-ADR-010 defect remains visible.

### Costs

- parsing and tests must cover multiple bounded representations;
- version-aware dispatch requires explicit compatibility knowledge;
- ambiguous metadata must be handled without silently guessing;
- rule documentation and profile versioning require coordinated updates.

### Risks and Limitations

- normalization may still reject valid representations not yet supported;
- section-derived values can be ambiguous when prose precedes the canonical value;
- historical compatibility can be mistaken for full validation of an older WEM version;
- aliases can expand without control unless each is deliberately bounded and tested.

### Mitigations

- maintain a small explicit representation registry;
- prefer unsupported findings over guessed values;
- expose the exact profile and compatibility limitation;
- test every supported representation with valid and invalid fixtures;
- keep Released WEM specifications authoritative over product behavior.

## Related Principles

- `WEM-P-002` — Separation of Knowledge and Products — WEM 1.2.0;
- `WEM-P-003` — Explicit and Traceable Decisions — WEM 1.2.0;
- `WEM-P-004` — Proportional Governance — WEM 1.2.0;
- `WEM-P-005` — Technology-Independent Method — WEM 1.2.0;
- `WEM-P-006` — Canonical Source of Normative Knowledge — WEM 1.2.0;
- `WEM-P-008` — Knowledge Preservation Through Evolution — WEM 1.2.0.

## Alternatives Considered

### A. Require every adopting project to migrate ADRs to WEM repository frontmatter

This option was rejected because WEM explicitly does not require a particular file format, and WEMO-ADR-010 preserves valid historical work without retroactive representation changes.

### B. Configure every metadata field through a repository manifest

This option would support arbitrary formats but would shift ordinary canonical-section interpretation into per-project configuration and increase adoption cost. It remains a possible future extension for genuinely custom systems.

### C. Normalize a bounded set of representations into one internal ADR model

This is the selected alternative. It corrects the invalid assumption, supports the real pilot formats and preserves deterministic bounded parsing.

### D. Treat all non-frontmatter ADRs as opaque and skip them

This option would remove false errors but lose useful lifecycle and preservation validation even when the required facts are explicit. It was rejected as unnecessarily weak.

## Implementation Notes

The Project Owner accepted this decision and authorized the bounded fourth-Milestone implementation on 2026-11-06 through the instruction to execute all four recommended remediation steps without pausing.

The implementation MAY update the Charter, validation architecture, parser, rules, lifecycle evaluator, profile metadata, package metadata, fixtures and tests within their active responsibilities. It SHALL preserve report Schema 0.3.0 and every earlier maintained contract.

Codex MAY perform the Architect, bounded Builder and Reviewer functions while Claude Code remains unavailable. Human Milestone acceptance remains a separate post-review gate and is not pre-authorized by implementation permission.

No commit, remote, push, tag, license, publication, release or distribution is authorized for the fourth-Milestone implementation.

### Implementation Evidence

The bounded fourth-Milestone implementation:

- added normalized ADR identity extraction from frontmatter, field preambles and canonical sections;
- normalized canonical and historical Status History column labels independently of column order;
- preserved existing rule identifiers while correcting the invalid frontmatter requirement;
- added explicit unsupported behavior for required ADR facts that cannot be extracted safely;
- added bounded compatibility for historical WEM 1.0.0 ADR facts shared with WEM 1.2.0;
- advanced the Draft profile implementation to 0.4.0 and the executable package to 0.3.0;
- preserved finding-report Schema 0.3.0 and all historical contracts;
- added a valid historical field-preamble fixture and focused parsing, lifecycle and unsupported-input tests;
- updated the Charter and validation architecture coherently with this decision.

The initial read-only WEM Orchestrator pilot produced:

```text
WEMV120-FM-001: 9 findings
WEMV120-HISTORY-005: 79 findings
WEMV120-ADR-002: 1 finding
total: 89 findings
```

Canonical-source review established that the first eighty-eight findings were representation-driven false positives. After implementation, the repeated pilot produced only the independent `WEMV120-ADR-002` finding for missing `Alternatives Considered` in WEMO-ADR-010.

The Project Owner separately authorized remediation of that historical documentation defect. WEMO-ADR-010 now records the two alternatives already evidenced by its original Context: continuing under WEM 1.0.0 or adopting WEM 1.2.0 while preserving valid historical work. The remediation records its date and authority and does not change the decision, lifecycle status or effective date.

Final verification completed on 2026-11-06:

```text
uv lock --check: passed
ruff format --check: passed
ruff check: passed
mypy strict: passed for 14 source files
pytest: 48 passed
WEM Validator filesystem validation: 0 findings
WEM Validator Git-aware validation: 0 findings
WEM Orchestrator filesystem validation after authorized remediation: 0 findings
WEM Orchestrator Git-aware validation after authorized remediation: 0 findings
WEM Orchestrator target status, refs and file hashes during validation: unchanged
source distribution and wheel build: passed
installed package version: 0.3.0
packaged report Schema byte comparison: passed
installed-wheel external pilot: passed with 0 findings
```

### Known Limitations

- supported representation normalization is deliberately bounded and does not cover arbitrary decision-record formats;
- historical WEM 1.0.0 compatibility covers only normalized ADR requirements confirmed as shared with WEM 1.2.0;
- general YAML frontmatter and raw HTML anchors remain outside the supported subset;
- Git lifecycle coverage remains limited to explicitly requested local first-parent history;
- only the WEM 1.2.0 profile is selectable;
- CLI, manifest, profile and JSON contracts remain Draft;
- structural validation does not certify WEM adoption or substantive engineering quality.

### Review Result

`Accepted for the next authorized gate`.

Codex performed the Architect, bounded Builder and Reviewer functions while Claude Code remained unavailable. The logical decision, implementation, pilot, remediation and review evidence remain explicit.

The Project Owner explicitly accepted the fourth Milestone with its documented limitations on 2026-11-06. This completes the required human acceptance gate without releasing the Draft CLI, manifest, profile or JSON contracts.

The accepted fourth-Milestone extension is preserved through the dedicated local commit authorized on 2026-11-06. No remote, push, tag, license, publication, release or distribution was authorized or inferred from Milestone acceptance.

---
