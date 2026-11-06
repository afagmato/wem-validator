---
Document: Architecture Decision Record
Identifier: WEMV-ADR-005
Title: Add Git-aware lifecycle validation
Status: Accepted
Created Date: 2026-11-04
ASI Level: 3
Decision Authority: Project Owner and Final Authority
WEM Reference: WEM 1.2.0 — Released
---

# WEMV-ADR-005 — Add Git-aware lifecycle validation

## Identifier

`WEMV-ADR-005`

## Title

Add Git-aware lifecycle validation

## Status

Accepted

## Created Date

2026-11-04

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-04 | Proposed | Project Owner and Final Authority | Evaluation opened for bounded local Git observation and ADR lifecycle-preservation checks. |
| 2026-11-04 | Accepted | Project Owner and Final Authority | Git-aware lifecycle-validation architecture approved and bounded third-Milestone implementation authorized. |

## Decision Authority

Project Owner and Final Authority

No delegation for this ASI-3 decision has been recorded.

## WEM Reference

WEM 1.2.0 — Released

## ASI Level

ASI-3 — Framework architecture

## Context

The accepted first and second Milestones establish deterministic, provider-independent and read-only validation for explicit files and repository manifest scopes. They validate supported WEM 1.2.0 frontmatter, ADR structure, local Markdown references and machine-readable report conformance.

The current profile cannot verify requirements whose evidence exists across repository history. In particular, it cannot determine whether ADR Status History entries were removed or overwritten, whether a previously maintained ADR disappeared, or whether the current lifecycle state preserves the accepted transition sequence. These limitations are reported explicitly, but they leave an important WEM knowledge-preservation property dependent on manual review.

WEM Validator now has a clean local Git baseline containing the accepted first and second Milestones. A bounded Git-aware vertical slice can therefore be exercised against a real adopting repository without changing the product's read-only responsibility or claiming certification.

The change coordinates repository observation, rule inputs, lifecycle evaluation, report metadata, contract versioning and test fixtures. It is classified as ASI-3 — Framework architecture. The added CLI and report fields remain Draft, have controlled consumers and are inexpensive to reverse, so their ASI-2 interface effect is governed proportionally within this decision.

An ASI-3 decision requires an ADR under WEM 1.2.0 but does not require an Architectural Pause. The Project Owner accepted this ADR and authorized the bounded implementation on 2026-11-04.

## Decision

The decision is to add an explicit, optional and read-only local Git observation adapter and use it to evaluate a bounded set of WEM 1.2.0 ADR lifecycle-preservation rules.

### Architectural boundary

The validation core SHALL consume a provider-independent history observation model. Git command execution, repository discovery and blob retrieval SHALL remain in a boundary adapter and SHALL NOT be embedded in individual rules.

The adapter SHALL:

- operate only on a local repository explicitly selected by the caller;
- use non-interactive, read-only Git operations;
- disable optional Git locks when invoking Git;
- pass command arguments without shell interpolation;
- remain within the resolved target repository and declared validation scope;
- return normalized observations or explicit unavailability reasons;
- apply fixed bounds to commits, paths and retrieved blob bytes;
- avoid checkout, reset, clean, fetch, configuration changes, index refresh and every other target mutation.

The validation core SHALL remain independent of Git executable details. A future history provider MAY implement the same observation contract only through a separately governed change.

### Explicit activation

History evaluation SHALL be opt-in and SHALL NOT be inferred merely because a `.git` directory or worktree is present.

The Draft CLI extension SHALL be equivalent to:

```text
wem-validate validate <repository> --config <manifest> --history git --format text|json
```

When `--history git` is omitted, the existing filesystem validation behavior SHALL remain unchanged and the report SHALL continue to disclose that Git-history-dependent checks were not executed.

When Git history is explicitly requested but the executable, repository observation or required history is unavailable, validation SHALL fail explicitly rather than silently omit the requested checks. Shallow or incomplete history SHALL be reported as insufficient evidence.

The initial Git observation SHALL evaluate the current working-tree documents against the first-parent history reachable from the repository's current `HEAD`. It SHALL NOT inspect remotes, alternate branches, reflogs, unreachable objects or network state.

### Lifecycle rules

The third Milestone SHALL implement rules that can determine, within the observed first-parent history, whether:

- an ADR's current `Status` agrees with the latest entry in its `Status History`;
- previously recorded Status History rows remain present and unchanged in later maintained versions;
- observed lifecycle transitions follow the WEM 1.2.0 ADR lifecycle;
- an ADR that previously formed part of maintained project knowledge has been removed from the current declared scope without an explicit supported outcome;
- a permanent ADR identifier remains associated with one logical decision across supported file movement or renaming.

Rules SHALL identify ADRs by their permanent identifier rather than filename alone. A finding SHALL identify the current artifact when available, the relevant observed revision and the authoritative WEM source requirement without reproducing unnecessary historical content.

The Milestone SHALL NOT infer decision authority from Git authorship, signatures, timestamps or commit messages. It SHALL NOT claim that an allowed state transition proves valid human approval.

### Report contract evolution

The machine-readable report format SHALL advance from Draft version `0.2.0` to Draft version `0.3.0` when it adds history-observation metadata.

The `0.3.0` report and Schema SHALL represent at least:

- requested history mode;
- observation availability and completeness;
- normalized current revision identity when available;
- evaluated history boundary and counts;
- deterministic history findings and explicit limitations.

The maintained `0.2.0` Schema SHALL remain in the repository as historical contract knowledge. The executable MAY emit only the current Draft format, provided that the version change is explicit and golden fixtures are updated coherently.

The `0.3.0` Schema SHALL be packaged with the wheel and verified byte-for-byte against its maintained repository source.

### Determinism and safety

The same filesystem content, selected profile and normalized Git observation SHALL produce the same ordered findings independent of machine-specific absolute paths.

Validation SHALL NOT modify target files, Git references, the index, the object database, configuration or working-tree metadata. Verification SHALL compare target and Git state before and after representative runs.

History limits SHALL produce explicit bounded-execution results. Reaching a limit SHALL NOT be reported as successful complete lifecycle validation.

### Third-Milestone acceptance criteria

The Milestone SHALL demonstrate:

- unchanged results for existing non-history validation when history is not requested;
- zero lifecycle findings for the maintained WEM Validator repository at the accepted baseline;
- deterministic findings for temporary repositories containing removed or rewritten Status History entries, invalid transitions, removed ADRs and identifier reuse;
- explicit failure for non-repositories, unavailable Git and shallow or otherwise insufficient history when history was requested;
- path, commit-count and blob-size boundary enforcement;
- identical finding semantics in text and JSON projections;
- validation of emitted reports against the packaged Draft `0.3.0` Schema;
- no target-file or Git-state mutation;
- formatting, linting, strict typing, automated tests, build and installed-wheel verification.

### Out of scope

The third Milestone SHALL NOT add:

- remote or network inspection;
- branch-policy, pull-request or hosting-provider integration;
- cryptographic signature or human-identity verification;
- release-tag integrity or provenance certification;
- automatic repair or target mutation;
- a second WEM profile;
- YAML-general frontmatter parsing;
- raw HTML anchor interpretation;
- quality scoring or WEM adoption certification;
- a remote repository, CI service, license, README, release, tag, publication or product distribution.

## Consequences

### Benefits

- one documented WEM knowledge-preservation limitation becomes executable and reproducible;
- current content and historical evidence remain separated through an explicit adapter boundary;
- filesystem-only users retain the existing behavior and dependency profile;
- lifecycle findings become traceable to exact local revisions without network access;
- the product is exercised against its own real Git history as an adopting project.

### Costs

- verification now requires temporary Git repositories and a compatible local Git executable;
- first-parent history semantics and bounded traversal require careful documentation;
- the report contract and golden fixtures require a Draft version increment;
- rule maintenance must distinguish structural evidence from proof of human authority.

### Risks and Limitations

- first-parent history does not describe every branch, discarded proposal or unreachable object;
- shallow clones and exported directories cannot provide complete lifecycle evidence;
- Git history may contain sensitive content, so findings must minimize reproduced blob data;
- rename and identifier matching can be ambiguous when historical documents are malformed;
- a zero-finding history run remains structural validation, not certification or approval evidence;
- reliance on the Git executable adds an optional local operational dependency.

### Mitigations

- require explicit activation and report the exact observation boundary;
- reject insufficient evidence instead of implying completeness;
- compare normalized parsed lifecycle facts rather than arbitrary full-file diffs;
- retain fixed traversal and content limits;
- keep Git invocation in one testable adapter;
- preserve non-certification and human-authority boundaries in every projection.

## Related Principles

- `WEM-P-002` — Separation of Knowledge and Products — WEM 1.2.0;
- `WEM-P-003` — Explicit and Traceable Decisions — WEM 1.2.0;
- `WEM-P-004` — Proportional Governance — WEM 1.2.0;
- `WEM-P-006` — Canonical Source of Normative Knowledge — WEM 1.2.0;
- `WEM-P-007` — Human Accountability — WEM 1.2.0;
- `WEM-P-008` — Knowledge Preservation Through Evolution — WEM 1.2.0.

## Alternatives Considered

### A. Keep lifecycle preservation entirely manual

This option would preserve the current implementation and avoid a Git dependency. It was not selected because one of the product's most important documented gaps would remain non-reproducible even though the required evidence is locally available.

### B. Execute Git directly from lifecycle rules

This option would minimize initial abstraction. It was not selected because it would couple normative rule behavior to process execution, complicate deterministic tests and make another history provider unnecessarily expensive.

### C. Add a bounded local Git adapter behind a provider-independent observation contract

This is the selected alternative. It preserves the core boundary, makes unavailability explicit and supports deterministic fixtures while adding only the history capability required by the Milestone.

### D. Use a third-party Git object-model library

This option could avoid subprocess calls and expose richer history traversal. It was not selected for this Milestone because it would add a runtime dependency and a larger security and compatibility surface before the bounded semantics are proven.

## Implementation Notes

The bounded implementation MAY modify only the existing Charter, validation architecture, product package, tests, manifest and report-contract responsibilities, plus this ADR. It MAY add real source and fixture files within the already active directories and a `contracts/finding-report/0.3.0.schema.json` artifact.

The implementation SHALL update `PROJECT_CHARTER.md` and `specifications/VALIDATION_ARCHITECTURE.md` so the third-Milestone scope and authoritative behavior remain coherent with this decision. It SHALL preserve `0.2.0.schema.json` as historical maintained knowledge.

Codex MAY perform the bounded Builder function while Claude Code remains unavailable, provided that the logical implementation, verification and review contracts remain explicit and the Project Owner retains every required decision and acceptance gate.

Acceptance of this ADR authorizes preparation and execution of only the bounded third Milestone described here. It does not authorize commit, push, remote creation, tag, license, publication, release or distribution. Each repository action remains subject to separate explicit authorization.

Implementation evidence and review results SHALL be added after the bounded Milestone has been executed and verified.

### Implementation Evidence

The bounded third-Milestone implementation created or changed only the authorized responsibilities:

- added a provider-independent `HistoryObservation` model and normalized report projection;
- added a bounded local Git adapter using non-interactive commands, disabled optional locks, fixed limits and no shell interpolation;
- added lifecycle rules for current Status coherence, append-only Status History, supported transitions, ADR preservation and identifier continuity;
- added the explicit Draft `--history git` CLI mode while preserving existing behavior when history is omitted;
- advanced the Draft report contract to 0.3.0 and retained the 0.2.0 Schema as historical knowledge;
- exposed independent Draft profile implementation version 0.3.0 through inventory format 0.2.0 and advanced the executable package to version 0.2.0;
- added temporary-repository tests for valid history, rewritten rows, invalid transitions, removed ADRs, identifier reuse, unavailable Git, root boundaries, execution limits and shallow history;
- updated the Charter and validation architecture coherently with this Accepted decision.

Verification completed on 2026-11-04:

```text
uv lock --check: passed
ruff format --check: passed
ruff check: passed
mypy strict: passed for 14 source files
pytest: 45 passed
maintained repository filesystem validation: passed with 0 findings
maintained repository Git-aware validation: passed with 0 findings
repeated installed-wheel Git-aware JSON output: deterministic
Draft 0.3.0 Schema meta-validation and report validation: passed
source distribution and wheel build: passed
installed-wheel import and packaged-Schema byte comparison: passed
wheel contains historical 0.2.0 and current 0.3.0 Schemas: passed
exact WEM v1.2.0 archive filesystem validation: passed with 0 findings
```

No selected target files, Git references, index state, object database or configuration were modified by representative Git-aware runs. Temporary repositories, archives, environments, caches and build products were removed after verification.

### Known Limitations

- lifecycle evaluation is intentionally limited to current `HEAD` first-parent history and selected working-tree documents;
- shallow repositories, exported directories and bounded observations cannot provide complete lifecycle evidence;
- Git authorship, timestamps, signatures and commit messages are not treated as proof of human authority;
- raw HTML anchors and general YAML frontmatter remain outside the supported subset;
- only WEM 1.2.0 is implemented;
- CLI, manifest, profile and JSON contracts remain Draft;
- structural validation does not certify WEM adoption or substantive engineering quality.

### Review Result

`Accepted for the next authorized gate`.

Codex performed the Architect, bounded Builder and Reviewer functions while Claude Code remained unavailable. Scope, implementation, correction, verification and limitations remain explicit.

The Project Owner explicitly accepted the third Milestone with its documented limitations on 2026-11-06. This completes the required human acceptance gate without releasing the Draft CLI, manifest, profile or JSON contracts.

The accepted third-Milestone extension remains an uncommitted local working tree. No commit, remote, push, tag, license, publication, release or distribution has been performed or inferred from Milestone acceptance.

---
