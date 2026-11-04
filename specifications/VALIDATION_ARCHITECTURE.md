---
Document: Validation Architecture
Title: WEM Validator Versioned Read-Only Validation Architecture
Version: 0.1.0
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

This specification is Draft and is authorized for controlled application. The Project Owner accepted the first and second implementation Milestones with their documented limitations on 2026-11-04.

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

## Markdown Links and Heading Fragments

The WEM 1.2.0 profile supports inline and reference-style Markdown links. External targets SHALL NOT be resolved over the network.

Local targets SHALL remain inside the selected repository. Supported heading fragments SHALL use a deterministic normalized anchor derived from Unicode-normalized, case-folded heading text, alphanumeric characters, spaces, hyphens and underscores. Spaces become hyphens and duplicate headings receive a numeric suffix beginning with `-1`.

Raw HTML anchors and ambiguous constructs outside this subset SHALL remain explicit limitations rather than silently accepted targets.

## Draft Report Contract

The canonical Draft report projection is defined structurally by `contracts/finding-report/0.2.0.schema.json` and semantically by this specification.

The report includes the selected profile, WEM Reference, normalized target, explicit scope, findings, limitations and summary counts. Text and JSON projections SHALL continue to represent the same findings.

The JSON Schema SHALL be packaged with the executable wheel and verified byte-for-byte against the repository contract. Draft validation does not establish a Released compatibility commitment.

## Rule Inventory

Every installed profile SHALL expose its rule identifiers, source references, descriptions and limitations without requiring a target validation run.

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
- expose Git-dependent checks as unavailable when the required repository observation is absent;
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

## Verification Responsibilities

Verification SHALL demonstrate:

- deterministic repeated output;
- identical findings represented by text and JSON projections;
- path-boundary and symbolic-link refusal behavior;
- explicit unsupported and malformed-input results;
- no target modification;
- no provider-specific type in the validation core;
- locked dependency and build reproducibility for the selected implementation profile;
- successful validation of the intended WEM `v1.2.0` target within the declared rule coverage.

## Evolution

Changes to source authority, read-only operation, versioned profile semantics, core responsibility boundaries or the distinction between validation and human authority SHALL be classified as ASI-4 or higher.

Changes to cross-component implementation architecture, parsing policy or coordinated rule behavior SHALL be classified according to their scope and cost of reversal.

Public CLI, JSON and rule-identifier compatibility changes SHALL follow applicable ASI-2 or higher governance.

---

End of WEM Validator Versioned Read-Only Validation Architecture
