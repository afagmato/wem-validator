---
Document: Validation Architecture
Title: WEM Validator Versioned Read-Only Validation Architecture
Version: 0.4.0
Status: Draft
Type: Architecture
ASI: 4
Language: English
Owner: WEM Validator
Decision Authority: Project Owner and Final Authority
Methodology: WEM
WEM Reference: WEM 1.2.0 — Released
Governing Decision: WEMV-ADR-002
---

# WEM Validator Versioned Read-Only Validation Architecture

## Purpose

This specification defines the maintained product architecture for deterministic structural validation of WEM repositories and adopting-project governance artifacts.

It materializes the architecture accepted in `decisions/WEMV-ADR-002.md`. It does not redefine WEM normative knowledge, certify a project, approve an engineering decision or authorize repository mutation.

## Status and Authority

This specification is Draft and is authorized for controlled application. The Project Owner accepted the first four implementation Milestones with their documented limitations, including the completed fourth Milestone on 2026-11-06. The fifth Milestone defined by `decisions/WEMV-ADR-007.md` is implemented and awaits Project Owner acceptance.

Further product implementation SHALL require a bounded Milestone authorization and every applicable decision gate. First-Milestone acceptance does not release the Draft CLI or JSON interface as a compatibility commitment.

The Released WEM version selected by a validation profile remains authoritative. If a product rule conflicts with its referenced WEM source, the WEM source governs and the product rule is defective.

## Architectural Boundaries

WEM Validator SHALL be:

- provider-independent;
- deterministic for the same profile, target bytes and explicit repository observations;
- local and read-only in its initial architecture;
- explicit about unsupported, incomplete and unavailable validation;
- separate from human architectural review and acceptance.

WEM Validator SHALL NOT:

- execute code from the target repository;
- use network access for canonical validation;
- infer requirements from private conversation;
- mutate, repair, commit, push, tag or publish a target;
- treat successful validation as certification or Project Owner approval;
- select an implicit latest WEM profile.

## Responsibility Model

### Input Boundary

The Input Boundary obtains bounded local document bytes and explicitly requested read-only Git observations.

It SHALL constrain traversal to the authorized target, apply file-size and file-count limits and reject path escape. Symbolic links SHALL NOT be followed by the initial implementation.

### Profile Registry

The Profile Registry resolves one exact profile identifier to an immutable in-process rule inventory.

The initial identifier SHALL represent WEM 1.2.0 — Released. Unsupported profiles SHALL fail explicitly before rule evaluation.

### Document Model

The Document Model represents only the parsed facts needed by implemented rules, including:

- repository-relative path;
- bounded source text;
- frontmatter entries and locations when available;
- Markdown link targets and locations;
- heading names and locations;
- document identity fields required for cross-checks.

Parsing SHALL preserve enough source location information to produce deterministic findings. It SHALL NOT interpret normative prose dynamically.

### ADR Representation Normalization

ADR validation SHALL operate on normalized identity and lifecycle facts rather than require one repository-specific presentation.

The initial normalization boundary supports:

- bounded YAML-like frontmatter;
- bounded leading field preambles;
- canonical ADR sections for missing identity values;
- Status History tables whose recognized columns use canonical or explicitly supported historical labels in any order.

Representation support is product behavior and SHALL NOT be described as a WEM file-format requirement. When required facts cannot be extracted safely, the result SHALL be explicit and unsupported rather than a fabricated missing-frontmatter conformance error.

Rules whose semantics vary by WEM version SHALL use the ADR's normalized WEM Reference. The WEM 1.2.0 profile MAY interpret normalized historical WEM 1.0.0 ADR facts only where the applicable Released requirements are confirmed as shared. That bounded compatibility SHALL NOT be presented as a complete WEM 1.0.0 profile.

### Rule Engine

The Rule Engine evaluates provider-independent rules over the Document Model and explicit repository observations.

Every rule SHALL declare a stable identifier, profile version, authoritative WEM source reference, required inputs and possible finding category. Evaluation order SHALL NOT affect the resulting normalized finding set.

### Finding Model

One internal Finding Model SHALL drive both human-readable and JSON output.

Each finding SHALL contain:

- rule identifier;
- selected profile;
- outcome category;
- affected repository-relative path;
- location when deterministically available;
- bounded explanation;
- authoritative source reference;
- limitations when applicable.

Presentation adapters MAY format or order fields for their medium but SHALL NOT change the represented finding semantics.

### Operational Adapters

Filesystem, Git, command-line and output behavior SHALL remain outside the rule-evaluation core.

No operational adapter may add mutation authority that is absent from the active architecture and authorization.

## Versioned Rule Profiles

A validation profile is a product implementation of a declared subset of requirements from one exact Released WEM version.

Profiles SHALL:

- identify the WEM version and Released status;
- expose an independent profile implementation version for the executable rule coverage;
- enumerate every implemented rule;
- expose known gaps and unsupported constructs;
- preserve rule identifiers across compatible corrections;
- use a new profile version when observable rule behavior changes;
- include valid, invalid and unsupported fixtures for each applicable rule family.

Profiles SHALL NOT copy complete WEM specifications into product code or documentation. Source references and concise rule behavior are sufficient.

## Explicit Repository Manifest

Repository-scoped validation SHALL require a caller-selected manifest. The CLI SHALL NOT discover or activate configuration implicitly.

The Draft manifest format SHALL identify:

- exact manifest-format version;
- exact WEM validation profile;
- repository-relative include patterns;
- repository-relative exclude patterns;
- optional safety limits that may only lower product hard limits.

Manifest selection SHALL reject path escape, absolute patterns, unmatched includes, symbolic-link traversal and conflicting profile selection. Reports SHALL preserve normalized include and exclude patterns plus excluded-path counts.

Direct target validation SHALL remain available for focused checks without inventing implicit repository exclusions.

## Explicit Git History Observation

Git-dependent validation SHALL require explicit caller activation. Repository presence SHALL NOT enable history evaluation implicitly.

The local Git adapter SHALL remain outside the rule-evaluation core and provide a normalized provider-independent observation. Its initial boundary is the first-parent history reachable from the current local `HEAD` plus the selected working-tree documents.

The adapter SHALL:

- require the selected target to be the resolved Git repository root;
- use non-interactive read-only commands with optional Git locks disabled;
- pass arguments without shell interpolation;
- apply commit, artifact and blob-size limits;
- reject shallow or otherwise insufficient history as incomplete evidence;
- avoid checkout, index refresh, reference mutation, network access and repository configuration changes;
- expose availability, completeness, revision identity, boundary and observation counts.

The initial history rules evaluate current Status coherence, append-only Status History preservation, supported ADR lifecycle transitions, maintained-ADR presence and permanent identifier continuity. Git authorship, timestamps, signatures and commit messages SHALL NOT be interpreted as decision authority or human approval.

First-parent evaluation does not represent alternate branches, discarded proposals, reflogs, unreachable objects or remote state. That boundary SHALL remain visible in every completed history report.

## Markdown Links and Heading Fragments

The WEM 1.2.0 profile supports inline and reference-style Markdown links. External targets SHALL NOT be resolved over the network.

Local targets SHALL remain inside the selected repository. Supported heading fragments SHALL use a deterministic normalized anchor derived from Unicode-normalized, case-folded heading text, alphanumeric characters, spaces, hyphens and underscores. Spaces become hyphens and duplicate headings receive a numeric suffix beginning with `-1`.

Raw HTML anchors and ambiguous constructs outside this subset SHALL remain explicit limitations rather than silently accepted targets.

## Draft Report Contract

The current canonical Draft report projection is defined structurally by `contracts/finding-report/0.3.0.schema.json` and semantically by this specification. The earlier `contracts/finding-report/0.2.0.schema.json` remains maintained historical contract knowledge.

The report includes the selected profile, independent profile implementation version, WEM Reference, normalized target, explicit scope, history-observation metadata, findings, limitations and summary counts. Text and JSON projections SHALL continue to represent the same findings.

The JSON Schema SHALL be packaged with the executable wheel and verified byte-for-byte against the repository contract. Draft validation does not establish a Released compatibility commitment.

## Rule Inventory

Every installed profile SHALL expose its rule identifiers, source references, descriptions, profile implementation version and limitations without requiring a target validation run. The initial history-capable inventory projection uses Draft format 0.2.0.

## Determinism and Normalization

Canonical validation SHALL NOT depend on:

- current time;
- network state;
- AI-provider output;
- locale-dependent sorting;
- absolute machine-specific paths in findings;
- nondeterministic filesystem enumeration.

Repository paths SHALL be normalized to forward-slash relative form in the Finding Model. Finding ordering SHALL use a documented stable key.

## Initial Safety Model

The initial implementation SHALL:

- open files read-only;
- reject inputs outside the resolved target root;
- reject unsupported encoding rather than replace undecodable bytes silently;
- bound individual files and total traversal;
- avoid remote Markdown-link resolution;
- expose explicitly requested Git-dependent checks as failed when the required observation is unavailable or insufficient;
- avoid target-file, Git-reference, index, object-database and configuration mutation;
- redact or omit unnecessary file content from findings.

## First Milestone Architecture

The first Milestone is one vertical slice for WEM 1.2.0 — Released.

It SHALL include:

- explicit profile selection;
- bounded local Markdown discovery and parsing;
- required frontmatter checks for supported WEM documents and ADRs;
- relative Markdown-link existence checks;
- required ADR-section checks;
- conditional Alternatives Considered checks by ASI;
- deterministic human-readable and JSON findings;
- valid, invalid and unsupported fixtures;
- a read-only run against a checkout of WEM tag `v1.2.0`;
- focused, complete-Milestone and package verification profiles.

It SHALL exclude:

- target mutation or automatic correction;
- network links;
- Git-history-dependent lifecycle preservation checks;
- profiles other than WEM 1.2.0;
- certification or quality scoring;
- hosted execution, service, database or graphical interface;
- AI-provider integration.

The exact implementation technology, CLI syntax, JSON compatibility boundary and execution limits require the separately governed first-Milestone implementation decision.

## Second Milestone Architecture

The second Milestone operationalizes one repository-scoped run through an explicit manifest, completes supported local Markdown reference and heading-fragment evaluation, packages the Draft report Schema and exposes the profile rule inventory.

It SHALL preserve the first Milestone's provider-independent, deterministic and read-only boundaries. It does not add Git-history analysis, another WEM profile, target mutation, network resolution, certification or public release authority.

## Third Milestone Architecture

The third Milestone adds one optional local Git observation adapter behind a provider-independent history model and evaluates a bounded set of WEM 1.2.0 ADR lifecycle-preservation rules.

It SHALL preserve filesystem-only behavior when history is not requested. When history is requested, unavailable, shallow or over-limit evidence SHALL fail explicitly rather than silently reduce coverage.

The Milestone advances the Draft report contract to 0.3.0, retains the 0.2.0 Schema as historical knowledge and preserves all non-certification and human-authority boundaries. It does not add remote inspection, branch-policy enforcement, identity verification, release provenance, target mutation, another WEM profile or public release authority.

The third-Milestone implementation identified the WEM 1.2.0 profile coverage as Draft profile implementation version 0.3.0 and the executable package as version 0.2.0.

## Fourth Milestone Architecture

The fourth Milestone introduces the normalized ADR representation boundary and WEM-reference-aware compatibility defined above. It preserves rule identifiers and report Schema 0.3.0 while advancing the observable profile implementation to 0.4.0 and the package to 0.3.0.

The Milestone SHALL eliminate representation-driven false positives for the supported WEM Orchestrator historical ADR form, retain current frontmatter behavior and continue to expose genuinely missing normative content. It does not implement arbitrary decision-record formats or a complete WEM 1.0.0 profile.

## Fifth Milestone Architecture

The fifth Milestone adds the `wem-1.3.0` profile under `decisions/WEMV-ADR-007.md`. Both profiles derive their rules from one shared table of rule keys, sources and descriptions. Each profile binds its own rule-identifier prefix, WEM sources and supported ADR WEM References.

The `wem-1.2.0` profile keeps its identifiers, sources, implementation version 0.4.0 and output. The `wem-1.3.0` profile starts at implementation version 0.1.0, uses the `WEMV130` prefix and cites ADR Specification 1.2.0. The default profile remains `wem-1.2.0`. The package advances to 0.4.0 and report Schema 0.3.0 is unchanged.

WEM 1.3.0 project-neutral ASI semantics and Validator Adoption Dispositions are judgment or transient initiation content and remain outside structural validation.

## Verification Responsibilities

Verification SHALL demonstrate:

- deterministic repeated output;
- identical findings represented by text and JSON projections;
- path-boundary and symbolic-link refusal behavior;
- explicit unsupported and malformed-input results;
- no target modification;
- no target Git-state modification during history evaluation;
- deterministic lifecycle findings over temporary Git repositories;
- explicit history-unavailable, shallow and bounded-execution outcomes;
- equivalent ADR findings across supported frontmatter and field-preamble representations;
- WEM-reference-aware preservation of valid historical ADR knowledge;
- no provider-specific type in the validation core;
- locked dependency and build reproducibility for the selected implementation profile;
- successful validation of the intended WEM `v1.2.0` target within the declared rule coverage;
- successful validation of the WEM `v1.3.0` target with the `wem-1.3.0` profile within the declared rule coverage.

## Evolution

Changes to source authority, read-only operation, versioned profile semantics, core responsibility boundaries or the distinction between validation and human authority SHALL be classified as ASI-4 or higher.

Changes to cross-component implementation architecture, parsing policy or coordinated rule behavior SHALL be classified according to their scope and cost of reversal.

Public CLI, JSON and rule-identifier compatibility changes SHALL follow applicable ASI-2 or higher governance.

---

End of WEM Validator Versioned Read-Only Validation Architecture
