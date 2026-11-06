"""Exact versioned validation-profile registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    identifier: str
    source: str
    description: str


@dataclass(frozen=True, slots=True)
class ValidationProfile:
    identifier: str
    version: str
    wem_reference: str
    rules: tuple[RuleDefinition, ...]
    limitations: tuple[str, ...]


WEM_120 = ValidationProfile(
    identifier="wem-1.2.0",
    version="0.4.0",
    wem_reference="WEM 1.2.0 — Released",
    rules=(
        RuleDefinition(
            "WEMV120-FM-001",
            "WEMV-ADR-006#Normalized ADR model",
            "Supported document metadata representations are bounded and parseable.",
        ),
        RuleDefinition(
            "WEMV120-FM-002",
            "ADR_SPECIFICATION.md@1.1.0#Required Content",
            "Supported frontmatter contains its required identity fields.",
        ),
        RuleDefinition(
            "WEMV120-FM-003",
            "ADR_SPECIFICATION.md@1.1.0#ADR Status",
            "Lifecycle status is allowed for the detected document kind.",
        ),
        RuleDefinition(
            "WEMV120-LINK-001",
            "WEM-P-008 — Knowledge Preservation Through Evolution",
            "Local Markdown link targets exist inside the selected target.",
        ),
        RuleDefinition(
            "WEMV120-LINK-002",
            "WEM-P-008 — Knowledge Preservation Through Evolution",
            "Reference-style Markdown links resolve to one local or external definition.",
        ),
        RuleDefinition(
            "WEMV120-LINK-003",
            "WEM-P-008 — Knowledge Preservation Through Evolution",
            "Supported local Markdown heading fragments resolve deterministically.",
        ),
        RuleDefinition(
            "WEMV120-ADR-001",
            "ADR_SPECIFICATION.md@1.1.0#Required Content",
            "ADRs contain every required maintained section.",
        ),
        RuleDefinition(
            "WEMV120-ADR-002",
            "ADR_SPECIFICATION.md@1.1.0#Required Content",
            "ASI-4 and ASI-5 ADRs contain Alternatives Considered.",
        ),
        RuleDefinition(
            "WEMV120-ADR-003",
            "ADR_SPECIFICATION.md@1.1.0#Identifier Governance",
            "ADR identifier, heading and filename remain consistent.",
        ),
        RuleDefinition(
            "WEMV120-INPUT-001",
            "WEMV-ADR-002#Read-only execution",
            "Unsupported or unsafe local input is reported explicitly.",
        ),
        RuleDefinition(
            "WEMV120-MANIFEST-001",
            "WEMV-ADR-004#Explicit repository manifest",
            "Repository validation scope is explicit, bounded and path-safe.",
        ),
        RuleDefinition(
            "WEMV120-HISTORY-001",
            "WEMV-ADR-005#Explicit activation",
            "Requested local Git history is available, complete and bounded.",
        ),
        RuleDefinition(
            "WEMV120-HISTORY-002",
            "ADR_SPECIFICATION.md@1.1.0#Status History",
            "Current ADR status agrees with a valid maintained Status History.",
        ),
        RuleDefinition(
            "WEMV120-HISTORY-003",
            "ADR_SPECIFICATION.md@1.1.0#Traceability and Preservation",
            "Maintained ADR lifecycle history is append-only and remains present.",
        ),
        RuleDefinition(
            "WEMV120-HISTORY-004",
            "ADR_SPECIFICATION.md@1.1.0#ADR Lifecycle",
            "Observed ADR lifecycle transitions follow the canonical lifecycle.",
        ),
        RuleDefinition(
            "WEMV120-HISTORY-005",
            "ADR_SPECIFICATION.md@1.1.0#Identifier Governance",
            "Permanent ADR identifiers preserve one continuous decision identity.",
        ),
    ),
    limitations=(
        "Raw HTML anchors and ambiguous Markdown constructs remain outside the supported subset.",
        "Frontmatter supports the flat key-value form used by WEM 1.2.0.",
        "Git lifecycle coverage is limited to explicitly requested local first-parent history.",
        (
            "Historical WEM 1.0 ADR compatibility is limited to normalized requirements "
            "shared with WEM 1.2."
        ),
    ),
)

_PROFILES = {WEM_120.identifier: WEM_120}


def resolve_profile(identifier: str) -> ValidationProfile:
    try:
        return _PROFILES[identifier]
    except KeyError as error:
        raise ValueError(f"unsupported validation profile: {identifier}") from error


def profile_inventory(identifier: str) -> dict[str, object]:
    profile = resolve_profile(identifier)
    return {
        "formatVersion": "0.2.0",
        "profile": profile.identifier,
        "profileVersion": profile.version,
        "wemReference": profile.wem_reference,
        "rules": [
            {
                "ruleId": rule.identifier,
                "source": rule.source,
                "description": rule.description,
            }
            for rule in profile.rules
        ],
        "limitations": list(profile.limitations),
    }
