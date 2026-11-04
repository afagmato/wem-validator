---
Document: Architecture Decision Record
Identifier: WEMV-ADR-004
Title: Operationalize repository-scoped validation
Status: Accepted
Created Date: 2026-11-04
ASI Level: 3
Decision Authority: Project Owner and Final Authority
WEM Reference: WEM 1.2.0 — Released
---

# WEMV-ADR-004 — Operationalize repository-scoped validation

## Identifier

`WEMV-ADR-004`

## Title

Operationalize repository-scoped validation

## Status

Accepted

## Created Date

2026-11-04

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-04 | Proposed | Project Owner and Final Authority | Evaluation opened for an explicit repository manifest, complete local Markdown-link semantics and a machine-verifiable Draft report contract. |
| 2026-11-04 | Accepted | Project Owner and Final Authority | Repository-scoped validation milestone approved and bounded implementation authorized without repository publication actions. |

## Decision Authority

Project Owner and Final Authority

No delegation for this ASI-3 decision has been recorded.

## WEM Reference

WEM 1.2.0 — Released

## Context

The accepted first Milestone proves a deterministic, provider-independent and read-only vertical slice. It validates explicit targets and reports its known limitations. WEM tag `v1.2.0` and the maintained WEM Validator foundation validate with zero findings under the implemented subset.

The current CLI cannot yet express which maintained repository scopes belong to one validation run. Validating the WEM Validator root intentionally discovers invalid test fixtures, while validating three separate paths requires orchestration outside the product. Silently ignoring `tests/`, fixture directories or other conventional paths would make coverage depend on hidden heuristics and could conceal real governance artifacts.

The current profile also reports reference-style Markdown links as unsupported and does not validate anchor fragments. The JSON report has a golden fixture but no standalone machine-verifiable Schema or explicit repository-scope projection.

The next useful Milestone is therefore to operationalize one complete repository run without weakening read-only behavior or pretending that the WEM 1.2.0 profile is complete. The change coordinates configuration, discovery, parsing, rule evaluation, CLI behavior and report compatibility. Under WEM 1.2.0 it is classified as ASI-3 — Framework architecture.

## Decision

The decision is to add one explicit, versioned repository-validation manifest and complete bounded local Markdown-link evaluation within the existing WEM 1.2.0 profile.

### Explicit repository manifest

The product SHALL support an explicit TOML manifest named by the caller. The initial conventional filename SHALL be `wem-validator.toml`, but the CLI SHALL NOT search for or activate it implicitly.

The command SHALL be equivalent to:

```text
wem-validate validate <repository> --config <manifest> --format text|json
```

The manifest SHALL declare:

- manifest format version;
- exact validation profile;
- one or more repository-relative include patterns;
- zero or more repository-relative exclude patterns.

The initial manifest MAY declare lower discovery limits than the product defaults. It SHALL NOT raise a product safety limit without a later governed decision.

Manifest paths and patterns SHALL:

- use normalized forward-slash repository-relative form;
- be evaluated against the resolved repository root;
- use one documented, deterministic glob grammar;
- reject absolute paths and parent traversal;
- never follow symbolic links;
- produce an error when an include pattern matches no supported input;
- preserve every include and exclude pattern in the machine-readable run metadata.

Exclusion SHALL be explicit evidence, not an invisible pass. The report SHALL identify excluded path counts by pattern without reproducing excluded file content.

Direct single-target validation without a manifest SHALL remain supported for focused checks. A manifest profile and a separately supplied `--profile` value SHALL NOT conflict silently.

### Manifest activation in WEM Validator

The Milestone SHALL add a root `wem-validator.toml` that includes maintained project governance and product source documentation while explicitly excluding generated caches and intentionally invalid or unsupported test fixtures from the repository-conformance run.

Fixture exclusions SHALL NOT affect the independent test suite that proves the corresponding invalid and unsupported outcomes.

### Local Markdown-link completion

The WEM 1.2.0 profile SHALL add bounded support for:

- reference-style link definitions and uses;
- local reference targets;
- same-document and cross-document heading fragments;
- deterministic heading-anchor normalization for the Markdown subset documented by the product;
- explicit unsupported findings for raw HTML anchors or ambiguous constructs outside that subset.

External URLs SHALL remain syntactically observable but SHALL NOT be resolved over the network.

A missing reference definition, local target or supported anchor SHALL produce a deterministic error finding with source location when available.

### Draft report contract

The Milestone SHALL create the first real `contracts/` artifact: a JSON Schema for the complete Draft report projection.

The report contract SHALL include:

- format version;
- selected profile and WEM Reference;
- normalized target identity;
- manifest identity and normalized include/exclude scope when applicable;
- deterministic findings;
- excluded-path counts;
- limitations;
- summary counts.

The schema and golden fixtures SHALL describe the same projection. The format SHALL remain Draft and SHALL NOT become a public compatibility commitment merely because it is structurally validated.

### Rule inventory

The CLI SHALL expose the installed rule inventory for one exact profile without executing a target validation. The projection SHALL identify rule IDs, authoritative source references, descriptions and profile limitations.

### Second Milestone acceptance criteria

The Milestone SHALL demonstrate:

1. one explicit root-manifest run over WEM Validator with zero unintended findings;
2. continued zero-finding validation of an exact WEM `v1.2.0` archive;
3. no implicit directory or fixture exclusions;
4. path-escape, unmatched-include and conflicting-profile failures;
5. deterministic reference-style and heading-anchor validation;
6. equivalent text and JSON findings;
7. JSON Schema validation of success and finding reports;
8. visible excluded-path counts;
9. unchanged target bytes before and after validation;
10. locked format, lint, strict type, test, build and installed-wheel verification.

### Authorization boundary

The bounded implementation may create or modify only:

- root `wem-validator.toml`;
- the first JSON Schema under `contracts/`;
- `src/wem_validator/` implementation within the Accepted architecture;
- `tests/` fixtures and verification;
- `pyproject.toml` and `uv.lock` only when the accepted implementation requires a compatible development or build dependency;
- bounded implementation evidence in this ADR and `specifications/VALIDATION_ARCHITECTURE.md`.

The Milestone SHALL NOT add a second WEM profile, Git-history evaluation, target mutation, automatic repair, network resolution, AI-provider integration, CI service, remote, license, README, commit, push, tag, publication or product release.

## Consequences

### Positive Consequences

- one invocation can validate an explicitly bounded repository scope;
- exclusions become reviewable configuration rather than hidden conventions;
- WEM Validator can validate its own maintained repository surface without treating invalid fixtures as production defects;
- local Markdown-link coverage becomes substantially more complete;
- consumers can validate the Draft JSON projection structurally;
- rule coverage and limitations become directly inspectable.

### Negative Consequences

- the manifest and JSON Schema add two Draft interfaces that must evolve coherently;
- deterministic glob and anchor behavior require careful cross-platform tests;
- repository owners must maintain explicit include and exclude patterns;
- reporting exclusions adds output and test complexity.

### Risks and Limitations

- broad exclude patterns could conceal relevant knowledge even when reported;
- Markdown heading-anchor algorithms differ between renderers;
- a manifest can become stale as repository responsibilities evolve;
- Draft interface users may still assume compatibility that has not been released;
- structural repository validation remains distinct from substantive engineering review.

### New Responsibilities

- maintain manifest-format and report-schema versions;
- keep root manifest scope aligned with repository responsibilities;
- preserve deterministic glob and anchor semantics;
- verify excluded-path accounting;
- prevent configuration from weakening hard safety limits;
- classify future interface stabilization or incompatible changes before release.

## Alternatives Considered

### Alternative A — Continue requiring callers to invoke each scope separately

This preserves the smallest product surface. It moves repository coverage and exclusions into external scripts or undocumented operator knowledge, preventing one reproducible validation result.

### Alternative B — Ignore conventional test, fixture and generated directories automatically

This makes root validation convenient. It creates hidden behavior, can omit real maintained knowledge and conflicts with explicit traceability.

### Alternative C — Use an explicit versioned manifest and report its scope

This adds a bounded configuration interface while making inclusion, exclusion and profile selection reviewable. It supports reproducible repository runs without silent heuristics. This is the selected alternative.

## ASI Level

ASI-3 — Framework architecture under WEM 1.2.0 terminology.

The decision coordinates configuration, repository discovery, Markdown parsing, rule evaluation, CLI behavior, report projection and contract verification. It preserves the Accepted ASI-4 authority, provider-independence and read-only boundaries.

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
- `decisions/WEMV-ADR-003.md` — Accepted;
- `specifications/VALIDATION_ARCHITECTURE.md` Version 0.1.0 — Draft.

## Implementation Notes

The Project Owner accepted this ADR on 2026-11-04 and authorized the bounded second Milestone implementation.

The authorization excludes a remote, commit, push, tag, license, publication and product release. Build artifacts MAY be created transiently for verification and SHALL NOT be retained as maintained repository knowledge.

The accepted first Milestone remains the historical Initialization Baseline. This implementation extends the current local working tree without rewriting that earlier acceptance evidence.

### Implemented scope

The bounded second Milestone implementation added:

- root `wem-validator.toml` with explicit WEM 1.2.0 profile, includes, excludes and hard-limit bounds;
- strict UTF-8 TOML ingestion with unknown-member, unsafe-pattern, path-escape, duplicate-pattern, unmatched-include, profile-conflict and limit-escalation failures;
- deterministic manifest selection and visible excluded-path counts;
- reference-style link definitions and full, collapsed and shortcut uses;
- same-document and cross-document heading-fragment validation with deterministic duplicate-heading anchors;
- explicit raw-HTML-anchor limitations without network resolution;
- Draft finding-report JSON Schema 0.2.0 under `contracts/`;
- packaged Schema resources with source-to-wheel byte verification;
- `profile inspect` rule-inventory output;
- expanded valid, invalid, unsupported, manifest, anchor and contract verification.

The root manifest includes `**/*.md` and explicitly excludes only the intentionally invalid and unsupported fixture scopes. Its verified report records one excluded path for each pattern and zero unintended findings.

### Dependency disposition

No runtime dependency was added. `jsonschema` and its type information were added only to the locked development profile to validate the Draft report Schema and generated reports.

### Verification evidence

The final local profile completed successfully on 2026-11-04:

```text
uv lock --check: passed
ruff format --check: passed
ruff check: passed
mypy strict: passed for 19 source files
pytest: 37 passed
root manifest validation: passed with 0 findings
rule inventory projection: passed
WEM v1.2.0 archive validation: passed with 0 findings
Draft report Schema meta-validation: passed
success, finding and manifest reports validated against Schema: passed
source distribution build: passed
wheel build: passed
installed-wheel import and packaged-Schema digest comparison: passed
installed wem-validate manifest run: passed with 0 findings
```

The WEM `v1.2.0` archive, build distributions and isolated installed-wheel environment were temporary and were removed after verification. No target bytes were modified by validation.

### Known limitations

- raw HTML anchors and ambiguous Markdown constructs remain outside the supported subset;
- frontmatter remains limited to the flat key-value form used by WEM 1.2.0;
- Git-history-dependent lifecycle preservation remains outside the profile;
- manifest, CLI and JSON report contracts remain Draft;
- the product still provides only the WEM 1.2.0 profile;
- structural validation remains distinct from certification and substantive engineering review.

### Review Result

`Accepted for the next authorized gate`.

Codex performed the Architect, bounded Builder and Reviewer functions because Claude Code remained unavailable. Scope, corrections, verification and limitations remain explicit.

The Project Owner explicitly accepted the second Milestone with its documented limitations on 2026-11-04. This completes the required human acceptance gate without releasing the Draft manifest, CLI or JSON contracts.

The current accepted local baseline extends the first Milestone with the manifest, complete supported local-link behavior, rule inventory and packaged report Schema described by this evidence. Repository actions remain intentionally deferred: no commit, remote, push, tag, license, publication or product release has been performed or inferred from Milestone acceptance.

---

End of WEMV-ADR-004
