---
Document: Architecture Decision Record
Identifier: WEMV-ADR-003
Title: Select the first validation milestone implementation profile
Status: Accepted
Created Date: 2026-11-04
ASI Level: 3
Decision Authority: Project Owner and Final Authority
WEM Reference: WEM 1.2.0 — Released
---

# WEMV-ADR-003 — Select the first validation milestone implementation profile

## Identifier

`WEMV-ADR-003`

## Title

Select the first validation milestone implementation profile

## Status

Accepted

## Created Date

2026-11-04

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-04 | Proposed | Project Owner and Final Authority | Evaluation opened for the technology, initial CLI contract and bounded execution profile required by the first Milestone. |
| 2026-11-04 | Accepted | Project Owner and Final Authority | First-Milestone implementation profile approved and bounded execution authorized without repository publication actions. |

## Decision Authority

Project Owner and Final Authority

No delegation for this ASI-3 decision has been recorded.

## WEM Reference

WEM 1.2.0 — Released

## Context

WEMV-ADR-001 and WEMV-ADR-002 establish the repository and provider-independent validation architecture. `specifications/VALIDATION_ARCHITECTURE.md` defines a first vertical slice but deliberately leaves implementation technology and the initial public interface unresolved.

The first Milestone cannot receive a self-sufficient Implementation Handoff until the runtime, dependency policy, package layout, verification toolchain, CLI boundary and execution limits are explicit.

The decision coordinates implementation, packaging, tests and two output projections. Under WEM 1.2.0 it is classified as ASI-3 — Framework architecture. The initial CLI and JSON shape remain Draft, have one controlled consumer and are inexpensive to reverse, so their bounded first-Milestone form is governed within this ADR rather than by an additional ASI-2 ADR.

## Decision

The decision is to implement the first Milestone as a standard-library-first Python 3.14 command-line package with a locked `uv` environment and strict local verification.

### Runtime and package profile

- CPython 3.14 SHALL be the initial supported runtime.
- The package SHALL use the `src/wem_validator/` layout.
- `pyproject.toml` SHALL be the canonical project and tool configuration.
- `uv.lock` SHALL preserve the resolved development and build environment.
- The first Milestone SHOULD have no third-party runtime dependency.
- A runtime dependency MAY be added only when the implementation handoff demonstrates that the standard library cannot satisfy an acceptance criterion safely and the dependency remains within the authorized correction boundary.
- Build configuration SHALL produce a source distribution and wheel without publishing them.

### Verification profile

The development profile SHALL use:

- Ruff for formatting and linting;
- mypy in strict mode for static type checking;
- pytest for unit, contract, fixture and integration verification;
- a build backend configured through `pyproject.toml`;
- an installed-wheel smoke test;
- a locked verification command that fails if `uv.lock` is stale.

Exact compatible tool versions SHALL be captured by the lockfile rather than duplicated normatively in this ADR.

### Initial CLI contract

The first Draft command SHALL be equivalent to:

```text
wem-validate validate <target> --profile wem-1.2.0 --format text|json
```

The command SHALL:

- require an explicit target;
- require or deterministically default to the only installed exact profile, while always reporting the selected profile;
- default to human-readable text when format is omitted;
- write findings to standard output;
- write invocation or evaluation failures to standard error without exposing unnecessary target content;
- perform no network access or target mutation.

Initial exit statuses SHALL be:

| Code | Meaning |
| --- | --- |
| 0 | Evaluation completed with no findings at the configured failure threshold |
| 1 | Evaluation completed with one or more findings at the configured failure threshold |
| 2 | Invocation, input, profile or evaluation failure prevented a complete result |

The JSON output SHALL include a format version, selected validation profile, normalized target identity, deterministic findings and explicit limitations. Its exact schema SHALL be Draft for the first Milestone and SHALL be covered by golden fixtures.

### Bounded execution profile

The first Milestone SHALL default to:

- repository-local traversal only;
- no symbolic-link following;
- UTF-8 input without silent replacement;
- deterministic lexicographic path ordering;
- an explicit per-file byte limit;
- an explicit maximum discovered-file count;
- no wall-clock timestamps in canonical output;
- no absolute target path in canonical findings.

Exact numeric limits SHALL be fixed in the Implementation Handoff after focused tests establish values that cover WEM `v1.2.0` with margin.

### First Milestone outcome

Deliver one installable, read-only CLI vertical slice that implements the WEM 1.2.0 profile subset defined by `specifications/VALIDATION_ARCHITECTURE.md` and proves it against valid, invalid and unsupported fixtures plus a read-only WEM `v1.2.0` checkout.

The Milestone SHALL expose its rule inventory and coverage gaps. It SHALL stop before any requirement for mutation, network access, another WEM profile, Git-history interpretation or certification semantics.

### Authorization boundary

The authorized implementation may create only:

- `pyproject.toml` and `uv.lock`;
- `src/wem_validator/` with the first real package artifacts;
- `tests/` with the first real verification and fixture artifacts;
- bounded updates to this ADR and `specifications/VALIDATION_ARCHITECTURE.md` when needed to record implementation evidence without changing the accepted decision.

The Milestone SHALL NOT create a remote, license, README, provider adapter, CI configuration, hosted service, release, commit, push, tag or publication.

## Consequences

### Positive Consequences

- Python's standard library is sufficient for a dependency-light initial parser, filesystem boundary and JSON projection;
- one locked toolchain supports deterministic local and future CI verification;
- the implementation profile aligns operationally with the existing WEM Orchestrator environment without coupling product architecture to it;
- text and JSON behavior can share one typed Finding Model;
- no runtime framework is introduced before its need is demonstrated.

### Negative Consequences

- Python 3.14 narrows execution to environments that provide the selected runtime;
- a standard-library Markdown scanner must maintain an explicit supported syntax boundary;
- strict typing and packaging verification add initial setup work;
- the Draft CLI may require a future compatibility decision before public release.

### Risks and Limitations

- a custom bounded Markdown scanner may mishandle syntax outside the declared subset;
- absence of a YAML dependency requires a deliberately narrow frontmatter grammar;
- Windows and POSIX path behavior require dedicated tests;
- toolchain similarity with WEM Orchestrator could conceal assumptions unless architectural tests enforce product independence.

### New Responsibilities

- maintain the locked Python toolchain;
- define and test the supported Markdown and frontmatter syntax subset;
- preserve text and JSON finding equivalence;
- verify source and wheel artifacts without publishing them;
- classify future public-interface compatibility before release.

## Alternatives Considered

### Alternative A — TypeScript and Node.js

This offers mature Markdown tooling and a straightforward JSON ecosystem. It introduces a runtime and packaging model not otherwise used by the current WEM product projects and does not improve the provider-independent boundary.

### Alternative B — Rust

This offers strong static guarantees and a single-binary path. It adds compilation and cross-platform packaging complexity disproportionate to the initial read-only vertical slice.

### Alternative C — Standard-library-first Python with a locked strict toolchain

This provides the smallest implementation path compatible with deterministic local validation, typed boundaries, packaging verification and the current execution environment. This is the selected alternative.

## ASI Level

ASI-3 — Framework architecture under WEM 1.2.0 terminology.

The decision coordinates runtime, package structure, parsing implementation, verification, CLI behavior and output projection while preserving the Accepted ASI-4 product boundaries and human authority.

## Related Principles

- `WEM-P-001` — Responsibility Before Structure;
- `WEM-P-003` — Explicit and Traceable Decisions;
- `WEM-P-004` — Proportional Governance;
- `WEM-P-005` — Technology-Independent Method;
- `WEM-P-006` — Canonical Source of Normative Knowledge;
- `WEM-P-007` — Human Accountability;
- `WEM-P-008` — Knowledge Preservation Through Evolution.

## Related Specifications and Decisions

- `PROJECT_CHARTER.md` Version 0.1.0 — Draft;
- `decisions/WEMV-ADR-001.md` — Accepted;
- `decisions/WEMV-ADR-002.md` — Accepted;
- `specifications/VALIDATION_ARCHITECTURE.md` Version 0.1.0 — Draft.

## Implementation Notes

The Project Owner accepted this ADR on 2026-11-04 and authorized the bounded first Milestone implementation.

The authorization excludes a remote, commit, push, tag, license, publication and product release. Build artifacts MAY be created transiently for verification and SHALL NOT be published or retained as maintained repository knowledge.

The implementation profile was checked against current official Python 3.14, uv, Ruff and mypy documentation on 2026-11-04. Exact tool versions remain intentionally non-normative until locked by an accepted implementation.

### Implemented scope

The bounded Milestone implementation created:

- `pyproject.toml` and `uv.lock`;
- the standard-library-only `src/wem_validator/` runtime package;
- exact WEM 1.2.0 profile and rule inventory;
- bounded read-only Markdown discovery without symbolic-link traversal;
- flat WEM frontmatter, heading and inline-link parsing;
- frontmatter, lifecycle, local-link, ADR-section, Alternatives Considered and identifier-consistency rules;
- deterministic Finding Model with equivalent text and JSON projections;
- the `wem-validate validate` CLI and three documented exit states;
- valid, invalid, unsupported and golden-output fixtures;
- unit and integration verification under `tests/`.

No third-party runtime dependency was introduced. Development and build dependencies are locked by `uv.lock`.

### Corrections during implementation

Initial end-to-end verification exposed and corrected:

1. an empty target directory incorrectly produced a successful empty report after a failed temporary archive setup; empty targets now fail explicitly with exit status 2;
2. Windows emitted the WEM status separator through its local console encoding; CLI streams now use explicit UTF-8;
3. `specifications/VALIDATION_ARCHITECTURE.md` lacked the `Methodology` frontmatter field required by the implemented document profile;
4. symbolic-link refusal was initially operating-system dependent in tests; deterministic adapter-boundary verification now covers it without requiring local symbolic-link privileges.

### Verification evidence

The final local profile completed successfully on 2026-11-04:

```text
uv lock --check: passed
ruff format --check: passed
ruff check: passed
mypy strict: passed for 15 source files
pytest: 18 passed
source distribution build: passed
wheel build: passed
installed-wheel import: passed
installed wem-validate CLI smoke: passed
```

The installed CLI validated a temporary archive of the exact WEM `v1.2.0` tag with zero findings and without modifying the WEM repository. The temporary archive, build distributions and isolated verification environment were removed after verification.

The validator also reported zero findings for the maintained WEM Validator Charter, Accepted decisions and Draft validation architecture when evaluated separately from intentionally invalid fixtures.

### Known limitations

- only inline Markdown links are evaluated;
- anchor fragments are not evaluated;
- the frontmatter parser supports the flat key-value form used by WEM 1.2.0;
- Git-history-dependent lifecycle preservation remains outside this profile subset;
- the JSON and CLI contracts remain Draft and have not been publicly released;
- the Milestone validates structural conformance only and does not certify WEM adoption or engineering correctness.

### Review Result

`Accepted for the next authorized gate`.

Codex performed the Architect, bounded Builder and Reviewer functions because Claude Code was unavailable. The logical scope, verification and review contracts remained explicit.

The Project Owner explicitly accepted the first Milestone with its documented limitations on 2026-11-04. This completes the required human acceptance gate without changing the Draft status of the CLI, JSON interface or architecture specification.

The accepted Initialization Baseline is the verified local working tree described by this implementation evidence. Repository actions remain intentionally deferred: no commit, remote, push, tag, license, publication or product release has been performed or inferred from Milestone acceptance.

---

End of WEMV-ADR-003
