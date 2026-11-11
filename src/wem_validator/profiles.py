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
    rule_prefix: str
    supported_adr_references: frozenset[str]
    rules: tuple[RuleDefinition, ...]
    limitations: tuple[str, ...]


_RULES: tuple[tuple[str, str, str], ...] = (
    (
        "FM-001",
        "WEMV-ADR-006#Normalized ADR model",
        "Supported document metadata representations are bounded and parseable.",
    ),
    (
        "FM-002",
        "ADR_SPECIFICATION.md@1.1.0#Required Content",
        "Supported frontmatter contains its required identity fields.",
    ),
    (
        "FM-003",
        "ADR_SPECIFICATION.md@1.1.0#ADR Status",
        "Lifecycle status is allowed for the detected document kind.",
    ),
    (
        "LINK-001",
        "WEM-P-008 — Knowledge Preservation Through Evolution",
        "Local Markdown link targets exist inside the selected target.",
    ),
    (
        "LINK-002",
        "WEM-P-008 — Knowledge Preservation Through Evolution",
        "Reference-style Markdown links resolve to one local or external definition.",
    ),
    (
        "LINK-003",
        "WEM-P-008 — Knowledge Preservation Through Evolution",
        "Supported local Markdown heading fragments resolve deterministically.",
    ),
    (
        "ADR-001",
        "ADR_SPECIFICATION.md@1.1.0#Required Content",
        "ADRs contain every required maintained section.",
    ),
    (
        "ADR-002",
        "ADR_SPECIFICATION.md@1.1.0#Required Content",
        "ASI-4 and ASI-5 ADRs contain Alternatives Considered.",
    ),
    (
        "ADR-003",
        "ADR_SPECIFICATION.md@1.1.0#Identifier Governance",
        "ADR identifier, heading and filename remain consistent.",
    ),
    (
        "INPUT-001",
        "WEMV-ADR-002#Read-only execution",
        "Unsupported or unsafe local input is reported explicitly.",
    ),
    (
        "MANIFEST-001",
        "WEMV-ADR-004#Explicit repository manifest",
        "Repository validation scope is explicit, bounded and path-safe.",
    ),
    (
        "HISTORY-001",
        "WEMV-ADR-005#Explicit activation",
        "Requested local Git history is available, complete and bounded.",
    ),
    (
        "HISTORY-002",
        "ADR_SPECIFICATION.md@1.1.0#Status History",
        "Current ADR status agrees with a valid maintained Status History.",
    ),
    (
        "HISTORY-003",
        "ADR_SPECIFICATION.md@1.1.0#Traceability and Preservation",
        "Maintained ADR lifecycle history is append-only and remains present.",
    ),
    (
        "HISTORY-004",
        "ADR_SPECIFICATION.md@1.1.0#ADR Lifecycle",
        "Observed ADR lifecycle transitions follow the canonical lifecycle.",
    ),
    (
        "HISTORY-005",
        "ADR_SPECIFICATION.md@1.1.0#Identifier Governance",
        "Permanent ADR identifiers preserve one continuous decision identity.",
    ),
)
"""Rule key, WEM 1.2.0 source and behavior shared by every supported profile."""

_ADR_SPECIFICATION_1_1 = "ADR_SPECIFICATION.md@1.1.0"


def _rules(prefix: str, adr_specification: str) -> tuple[RuleDefinition, ...]:
    return tuple(
        RuleDefinition(
            f"{prefix}-{key}",
            source.replace(_ADR_SPECIFICATION_1_1, adr_specification),
            description,
        )
        for key, source, description in _RULES
    )


_SHARED_LIMITATIONS = (
    "Raw HTML anchors and ambiguous Markdown constructs remain outside the supported subset.",
    "Git lifecycle coverage is limited to explicitly requested local first-parent history.",
)

WEM_120 = ValidationProfile(
    identifier="wem-1.2.0",
    version="0.4.0",
    wem_reference="WEM 1.2.0 — Released",
    rule_prefix="WEMV120",
    supported_adr_references=frozenset({"WEM 1.0.0 — Released", "WEM 1.2.0 — Released"}),
    rules=_rules("WEMV120", _ADR_SPECIFICATION_1_1),
    limitations=(
        _SHARED_LIMITATIONS[0],
        "Frontmatter supports the flat key-value form used by WEM 1.2.0.",
        _SHARED_LIMITATIONS[1],
        (
            "Historical WEM 1.0 ADR compatibility is limited to normalized requirements "
            "shared with WEM 1.2."
        ),
    ),
)

WEM_130 = ValidationProfile(
    identifier="wem-1.3.0",
    version="0.1.0",
    wem_reference="WEM 1.3.0 — Released",
    rule_prefix="WEMV130",
    supported_adr_references=frozenset(
        {"WEM 1.0.0 — Released", "WEM 1.2.0 — Released", "WEM 1.3.0 — Released"}
    ),
    rules=_rules("WEMV130", "ADR_SPECIFICATION.md@1.2.0"),
    limitations=(
        _SHARED_LIMITATIONS[0],
        "Frontmatter supports the flat key-value form used by WEM 1.2.0 and WEM 1.3.0.",
        _SHARED_LIMITATIONS[1],
        (
            "Historical WEM 1.0 ADR compatibility is limited to normalized requirements "
            "shared with WEM 1.3."
        ),
        (
            "WEM 1.3.0 project-neutral ASI semantics and Validator Adoption Dispositions are "
            "judgment or transient initiation content and are not structurally validated."
        ),
    ),
)

_PROFILES = {profile.identifier: profile for profile in (WEM_120, WEM_130)}


def resolve_profile(identifier: str) -> ValidationProfile:
    try:
        return _PROFILES[identifier]
    except KeyError as error:
        raise ValueError(f"unsupported validation profile: {identifier}") from error


def rule_identifier(profile: ValidationProfile, key: str) -> str:
    """Return the profile-specific identifier for a shared rule key such as ``ADR-001``."""

    return f"{profile.rule_prefix}-{key}"


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
