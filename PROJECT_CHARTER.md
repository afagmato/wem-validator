---
Document: Project Charter
Title: WEM Validator Project Charter
Version: 0.1.0
Status: Draft
Type: Foundation
ASI: 5
Language: English
Owner: WEM Validator
Decision Authority: Project Owner and Final Authority
Current Authority Holder: Arç
Methodology: WEM
WEM Reference: WEM 1.2.0 — Released
---

# WEM Validator Project Charter

## Purpose

This Charter establishes the identity, mission, boundaries, authority and initial constraints of WEM Validator.

The Project Owner accepted the Foundation Package on 2026-11-03 and authorized creation of the local repository and this Draft Charter. That authorization does not release the Charter, select implementation technology, authorize product implementation, create a remote repository or authorize commit or push.

## Project Identity

- Project: WEM Validator
- Repository: `wem-validator`
- Type: Executable software product
- Methodology: WEM 1.2.0 — Released

WEM Validator is separate from the Workspace Engineering Method knowledge repository. It implements validation behavior against declared WEM versions but SHALL NOT become an alternative source of WEM normative knowledge.

## Problem Statement

WEM repositories and adopting projects rely on maintained Markdown specifications, ADR metadata, internal references, lifecycle states and cross-document coherence. The current WEM repository has no automated validation of those properties. Manual and agent-assisted review can detect defects, but it is difficult to reproduce consistently and may allow stale wording, malformed records or broken references to reach a release candidate.

## Mission

Provide deterministic, provider-independent and read-only validation of WEM repositories and adopting-project governance artifacts without redefining WEM normative knowledge.

## Intended Users

- maintainers reviewing WEM itself;
- projects that adopt a declared WEM version;
- Architects, Reviewers and Project Owners evaluating governance artifacts;
- local development and continuous-integration environments invoking a stable validator interface.

## Objectives

- validate structural requirements derived from an explicitly declared WEM version;
- identify broken relative references and inconsistent artifact metadata;
- validate required ADR sections, lifecycle values and conditional content;
- provide deterministic human-readable and machine-readable findings;
- operate without AI providers or private conversational context;
- remain read-only unless a future, separately governed responsibility explicitly introduces mutation;
- make unavailable or unsupported validation explicit rather than silently passing it;
- preserve the distinction between structural validation, technical review and human acceptance.

## Expected Outcomes

- a versioned validation profile identifies which WEM release it implements;
- valid and invalid fixtures make each supported rule reproducible;
- a local CLI can validate a target without modifying it;
- findings identify the rule, affected path, location when available and bounded explanation;
- exit status and machine-readable output support CI without becoming certification;
- validation gaps and unsupported constructs remain visible.

## Scope

### Initial Scope In

- YAML-like frontmatter fields used by WEM specifications and ADRs;
- declared document version and lifecycle status;
- relative Markdown links and canonical local paths;
- ADR required sections and allowed lifecycle states;
- Status History presence and preservation checks that can be evaluated from the current repository and Git inputs explicitly supplied to the validator;
- Alternatives Considered applicability by ASI;
- identifier and filename consistency;
- WEM Reference syntax and supported-version selection;
- component version and status matrices;
- deterministic local validation with human-readable and JSON output;
- valid and invalid fixtures for supported rules.

### Initial Scope Out

- automatic correction or file mutation;
- commit, push, merge, tag, publication or release actions;
- certification, compliance guarantees or project-quality scoring;
- deciding whether an engineering decision is substantively correct;
- replacing architectural or human review;
- interpreting private conversation history;
- remote URL availability checks;
- provider-specific AI integration;
- dynamic execution of repository code under validation;
- package publication, hosted service or graphical interface;
- validation of every historical WEM version in the first Milestone.

## Ownership and Authority

Arç is the Project Owner and Final Authority.

The Project Owner retains authority over:

- project foundation and scope;
- ASI-4 and ASI-5 decisions;
- licensing and publication;
- milestone acceptance;
- repository creation, commit, push and release actions when not already covered by an explicit bounded authorization;
- any future mutation or certification responsibility.

Successful validation SHALL NOT constitute human acceptance, release approval or authorization to modify the validated repository.

## Initial Operational Roles

- Arç: Project Owner and Final Authority;
- Codex: Architect and Reviewer;
- Claude Code: Builder.

These are replaceable operational assignments. Providers and models SHALL NOT define the product's foundational architecture or canonical validation semantics.

## Foundational Constraints

- WEM Validator SHALL remain a separate executable product repository.
- WEM normative specifications and Released tags remain the authoritative source of requirements.
- Every implemented rule SHALL identify its source WEM version and authoritative requirement.
- Product code, schemas or rule catalogs SHALL NOT silently strengthen or weaken WEM governance.
- Validation SHALL be deterministic for the same declared profile, target bytes and explicit repository observations.
- The initial product SHALL operate locally and read-only.
- Validation SHALL fail explicitly when a required input is malformed, unavailable or unsupported.
- Findings SHALL be bounded and SHALL NOT reproduce credentials, complete private files or unnecessary sensitive content.
- Human-readable and machine-readable output SHALL represent the same findings.
- Technology, repository architecture and rule-versioning decisions SHALL remain governed by their Accepted ADRs. Licensing and publication remain deferred.

## Preferences and Assumptions

The separate-product boundary and read-only initial behavior are confirmed requirements.

The following directions are now accepted and implemented in Draft form:

- a command-line interface suitable for local and CI execution;
- offline operation for canonical local validation;
- implementation-language selection based on deterministic parsing, packaging and cross-platform support;
- incremental delivery beginning with frontmatter, relative links and ADR structure.

The following remain unresolved material decisions:

- public compatibility and release status for the CLI, manifest and JSON interfaces;
- Git-history-dependent lifecycle validation;
- profiles for WEM versions other than 1.2.0;
- licensing;
- remote hosting and publication.

## Initial Decision Skeleton

| Decision | Provisional ASI | Authority | State |
| --- | --- | --- | --- |
| Project foundation | ASI-5 | Project Owner | Accepted through Foundation Package; Draft Charter materialized |
| Repository and ADR governance | ASI-4 | Project Owner | Accepted through WEMV-ADR-001 |
| Validation responsibility boundaries and rule-source model | ASI-4 | Project Owner | Accepted through WEMV-ADR-002 |
| Versioned rule profile and CLI architecture | ASI-3 | Project Owner | Accepted through WEMV-ADR-003 |
| Machine-readable findings interface | ASI-2 within the first Milestone boundary | Project Owner | Draft implementation authorized by WEMV-ADR-003 |
| Implementation language and libraries | ASI-3 | Project Owner | Accepted through WEMV-ADR-003 |
| Repository-scoped manifest and extended link semantics | ASI-3 | Project Owner | Accepted and implemented through WEMV-ADR-004 |
| Licensing and publication | Human-reserved | Project Owner | Deferred |

## First Milestone

Establish the minimum accepted architecture and one read-only validation vertical slice that can:

1. select a WEM 1.2.0 validation profile;
2. parse bounded local Markdown inputs without executing target code;
3. validate required frontmatter, relative links and ADR structure;
4. report deterministic findings in human-readable and JSON forms;
5. verify behavior with valid and invalid fixtures;
6. run against the WEM 1.2.0 tag without modifying it.

The required ASI-4 and ASI-3 decisions were accepted through WEMV-ADR-001, WEMV-ADR-002 and WEMV-ADR-003. The bounded implementation completed its local verification and the Project Owner accepted the Milestone with its documented limitations on 2026-11-04.

## Initialization Baseline

The accepted Initialization Baseline consists of:

- this Draft Charter;
- Accepted WEMV-ADR-001, WEMV-ADR-002 and WEMV-ADR-003;
- Draft `specifications/VALIDATION_ARCHITECTURE.md`;
- the locked Python 3.14 project configuration;
- the standard-library-only WEM 1.2.0 validation package;
- valid, invalid, unsupported and golden-output fixtures;
- the verification evidence and known limitations recorded by WEMV-ADR-003.

At first-Milestone acceptance, the baseline remained an uncommitted local working tree because commit, remote and publication actions were explicitly excluded from that authorization. It was later incorporated into the current accepted baseline and preserved by the separately authorized initial local commit. Milestone acceptance SHALL NOT be interpreted as authorization for repository actions or for a subsequent Milestone.

## Second Milestone

The second Milestone operationalizes a single repository-scoped validation run through an explicit manifest, validates supported reference-style links and heading fragments, packages a Draft report Schema and exposes the WEM 1.2.0 rule inventory.

WEMV-ADR-004 authorized its bounded implementation. Local verification completed and the Project Owner accepted the Milestone with the limitations recorded by that ADR on 2026-11-04.

## Current Accepted Baseline

The current accepted local baseline extends the Initialization Baseline with:

- explicit repository-scoped manifest validation;
- supported inline, reference-style and heading-fragment link evaluation;
- Draft finding-report JSON Schema 0.2.0;
- packaged Schema resources and rule-inventory projection;
- 37 passing automated tests and installed-wheel verification;
- zero-finding validation of both the WEM Validator manifest scope and WEM `v1.2.0` archive.

This baseline is preserved by initial local Git commit `6659dbd`, created under separate explicit repository-action authorization. The repository has no configured remote, and no push, tag, license, publication or product release has been performed.

## Foundation Acceptance Criteria

- the project identity and separate-product responsibility are explicit;
- WEM 1.2.0 — Released is declared;
- Arç's final authority is preserved;
- initial operational participants are replaceable;
- read-only validation and non-certification boundaries are explicit;
- no implementation technology, license or public interface is silently selected;
- no artifact other than this Charter and repository metadata is created before the next governed decision.

## Major Risks and Limitations

- encoded rules may drift from their canonical WEM version;
- structural validation may be mistaken for substantive correctness or conformity;
- permissive Markdown or frontmatter parsing may hide malformed input;
- strict parsing may reject documents WEM intended to permit;
- cross-document checks may require Git history or context not present in an exported directory;
- supporting multiple WEM versions can multiply rule and fixture maintenance;
- validation of WEM by a WEM-derived product can remain self-referential without external adoption.

## WEM Adoption

WEM Validator adopts WEM 1.2.0 — Released for its own engineering governance. It does not automatically adopt the Draft WEM 1.3.0 work in the methodology repository.

Applicable Engineering Principles SHALL be interpreted from the declared WEM version. The product will define its own repository architecture, decision authorities, licensing and implementation through separately governed decisions.

## Evolution

This Charter remains Draft until it completes technical review and the Project Owner separately authorizes its release. Changes to mission, product responsibility, final authority or read-only foundational boundary require ASI-5 governance.

## End of Charter
