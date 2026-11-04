"""WEM 1.2.0 structural rule evaluation."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import unquote, urlsplit

from wem_validator.discovery import DiscoveredFile
from wem_validator.model import Finding, Outcome
from wem_validator.parsing import ParsedMarkdown, heading_anchors
from wem_validator.profiles import ValidationProfile

_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_ADR_STATUSES = {"Proposed", "Accepted", "Rejected", "Withdrawn", "Superseded", "Retired"}
_DOCUMENT_STATUSES = {"Draft", "Released", "Retired"}
_ADR_FIELDS = {
    "Document",
    "Identifier",
    "Title",
    "Status",
    "Created Date",
    "ASI Level",
    "Decision Authority",
    "WEM Reference",
}
_DOCUMENT_FIELDS = {
    "Document",
    "Title",
    "Version",
    "Status",
    "Type",
    "ASI",
    "Language",
    "Owner",
    "Methodology",
}
_ADR_SECTIONS = {
    "Identifier",
    "Title",
    "Status",
    "Created Date",
    "Status History",
    "Decision Authority",
    "WEM Reference",
    "Context",
    "Decision",
    "Consequences",
    "ASI Level",
    "Related Principles",
}


def evaluate_document(
    item: DiscoveredFile,
    parsed: ParsedMarkdown | None,
    *,
    root: Path,
    profile: ValidationProfile,
    documents: Mapping[Path, ParsedMarkdown],
) -> tuple[Finding, ...]:
    if item.issue is not None:
        return (
            _finding(
                profile,
                "WEMV120-INPUT-001",
                Outcome.UNSUPPORTED,
                item.relative_path,
                item.issue,
            ),
        )
    if parsed is None:
        raise ValueError("parsed document is required for readable input")

    findings: list[Finding] = []
    frontmatter = parsed.frontmatter
    values = frontmatter.values
    is_decision_path = item.relative_path.startswith("decisions/")
    is_adr = values.get("Document") == "Architecture Decision Record" or is_decision_path

    if is_decision_path and not frontmatter.present:
        findings.append(
            _finding(
                profile,
                "WEMV120-FM-001",
                Outcome.ERROR,
                item.relative_path,
                "ADR files require frontmatter at the start of the document.",
                line=1,
            )
        )
    if frontmatter.present and not frontmatter.closed:
        findings.append(
            _finding(
                profile,
                "WEMV120-FM-001",
                Outcome.ERROR,
                item.relative_path,
                "Frontmatter is not closed by a second delimiter.",
                line=1,
            )
        )
    for key in frontmatter.duplicate_keys:
        findings.append(
            _finding(
                profile,
                "WEMV120-FM-001",
                Outcome.ERROR,
                item.relative_path,
                f"Frontmatter key is duplicated: {key}.",
                line=frontmatter.lines.get(key),
            )
        )
    for line in frontmatter.malformed_lines:
        findings.append(
            _finding(
                profile,
                "WEMV120-FM-001",
                Outcome.ERROR,
                item.relative_path,
                "Frontmatter line is not a supported non-empty key-value pair.",
                line=line,
            )
        )

    if frontmatter.present and frontmatter.closed:
        required = _ADR_FIELDS if is_adr else _DOCUMENT_FIELDS
        for field in sorted(required - values.keys()):
            findings.append(
                _finding(
                    profile,
                    "WEMV120-FM-002",
                    Outcome.ERROR,
                    item.relative_path,
                    f"Required frontmatter field is missing: {field}.",
                    line=1,
                )
            )
        findings.extend(_validate_identity_fields(item, profile, is_adr, parsed))

    if is_adr:
        findings.extend(_validate_adr(item, profile, parsed))
    findings.extend(_validate_links(item, profile, parsed, root, documents))

    for line in parsed.duplicate_reference_lines:
        findings.append(
            _finding(
                profile,
                "WEMV120-LINK-002",
                Outcome.ERROR,
                item.relative_path,
                "Reference-style Markdown link label is defined more than once.",
                line=line,
            )
        )
    for line in parsed.raw_html_anchor_lines:
        findings.append(
            _finding(
                profile,
                "WEMV120-INPUT-001",
                Outcome.UNSUPPORTED,
                item.relative_path,
                "Raw HTML anchors are outside the supported heading-fragment subset.",
                line=line,
                limitations=("Links to this raw HTML anchor cannot be verified.",),
            )
        )
    return tuple(findings)


def _validate_identity_fields(
    item: DiscoveredFile,
    profile: ValidationProfile,
    is_adr: bool,
    parsed: ParsedMarkdown,
) -> list[Finding]:
    findings: list[Finding] = []
    values = parsed.frontmatter.values
    status = values.get("Status")
    allowed = _ADR_STATUSES if is_adr else _DOCUMENT_STATUSES
    if status is not None and status not in allowed:
        findings.append(
            _finding(
                profile,
                "WEMV120-FM-003",
                Outcome.ERROR,
                item.relative_path,
                f"Unsupported lifecycle status for this document kind: {status}.",
                line=parsed.frontmatter.lines.get("Status"),
            )
        )
    version = values.get("Version")
    if not is_adr and version is not None and not _SEMVER.fullmatch(version):
        findings.append(
            _finding(
                profile,
                "WEMV120-FM-002",
                Outcome.ERROR,
                item.relative_path,
                "Version must use semantic version form X.Y.Z.",
                line=parsed.frontmatter.lines.get("Version"),
            )
        )
    asi_member = "ASI Level" if is_adr else "ASI"
    asi = values.get(asi_member)
    if asi is not None and asi not in {"1", "2", "3", "4", "5"}:
        findings.append(
            _finding(
                profile,
                "WEMV120-FM-002",
                Outcome.ERROR,
                item.relative_path,
                f"{asi_member} must be an integer from 1 through 5.",
                line=parsed.frontmatter.lines.get(asi_member),
            )
        )
    return findings


def _validate_adr(
    item: DiscoveredFile,
    profile: ValidationProfile,
    parsed: ParsedMarkdown,
) -> list[Finding]:
    findings: list[Finding] = []
    for section in sorted(_ADR_SECTIONS - parsed.headings.keys()):
        findings.append(
            _finding(
                profile,
                "WEMV120-ADR-001",
                Outcome.ERROR,
                item.relative_path,
                f"Required ADR section is missing: {section}.",
            )
        )
    asi = parsed.frontmatter.values.get("ASI Level")
    if asi in {"4", "5"} and "Alternatives Considered" not in parsed.headings:
        findings.append(
            _finding(
                profile,
                "WEMV120-ADR-002",
                Outcome.ERROR,
                item.relative_path,
                "ASI-4 and ASI-5 ADRs require Alternatives Considered.",
            )
        )
    identifier = parsed.frontmatter.values.get("Identifier")
    if identifier is not None:
        if Path(item.relative_path).stem != identifier:
            findings.append(
                _finding(
                    profile,
                    "WEMV120-ADR-003",
                    Outcome.ERROR,
                    item.relative_path,
                    "ADR filename stem does not match its Identifier.",
                    line=parsed.frontmatter.lines.get("Identifier"),
                )
            )
        level_one = tuple(name for name in parsed.headings if name.startswith(identifier))
        if not level_one:
            findings.append(
                _finding(
                    profile,
                    "WEMV120-ADR-003",
                    Outcome.ERROR,
                    item.relative_path,
                    "ADR title heading does not begin with its Identifier.",
                )
            )
    return findings


def _validate_links(
    item: DiscoveredFile,
    profile: ValidationProfile,
    parsed: ParsedMarkdown,
    root: Path,
    documents: Mapping[Path, ParsedMarkdown],
) -> list[Finding]:
    findings: list[Finding] = []
    parent = item.absolute_path.parent
    root_resolved = root.resolve()
    for link in parsed.links:
        if link.target is None:
            findings.append(
                _finding(
                    profile,
                    "WEMV120-LINK-002",
                    Outcome.ERROR,
                    item.relative_path,
                    f"Reference-style Markdown link has no definition: {link.reference_label}.",
                    line=link.line,
                )
            )
            continue
        try:
            split = urlsplit(link.target)
        except ValueError:
            findings.append(
                _finding(
                    profile,
                    "WEMV120-LINK-001",
                    Outcome.ERROR,
                    item.relative_path,
                    "Markdown link target is malformed.",
                    line=link.line,
                )
            )
            continue
        if split.scheme or split.netloc:
            continue
        relative = unquote(split.path)
        resolved = (parent / relative).resolve(strict=False) if relative else item.absolute_path
        if not resolved.is_relative_to(root_resolved):
            explanation = "Relative Markdown link escapes the selected target."
        elif not resolved.exists():
            explanation = f"Relative Markdown link target does not exist: {relative}."
        else:
            explanation = ""
        if explanation:
            findings.append(
                _finding(
                    profile,
                    "WEMV120-LINK-001",
                    Outcome.ERROR,
                    item.relative_path,
                    explanation,
                    line=link.line,
                )
            )
            continue
        if not split.fragment:
            continue
        parsed_target = documents.get(resolved.resolve())
        if parsed_target is None:
            findings.append(
                _finding(
                    profile,
                    "WEMV120-INPUT-001",
                    Outcome.UNSUPPORTED,
                    item.relative_path,
                    "Heading fragment target is outside the evaluated Markdown scope.",
                    line=link.line,
                    limitations=("The local target exists but its headings were not evaluated.",),
                )
            )
            continue
        fragment = unquote(split.fragment).casefold()
        if fragment not in heading_anchors(parsed_target):
            findings.append(
                _finding(
                    profile,
                    "WEMV120-LINK-003",
                    Outcome.ERROR,
                    item.relative_path,
                    f"Markdown heading fragment does not exist: #{split.fragment}.",
                    line=link.line,
                )
            )
    return findings


def _finding(
    profile: ValidationProfile,
    rule_id: str,
    outcome: Outcome,
    path: str,
    explanation: str,
    *,
    line: int | None = None,
    limitations: tuple[str, ...] = (),
) -> Finding:
    definition = next(item for item in profile.rules if item.identifier == rule_id)
    return Finding.create(
        rule_id=rule_id,
        profile=profile.identifier,
        outcome=outcome,
        path=path,
        line=line,
        explanation=explanation,
        source=definition.source,
        limitations=limitations,
    )
