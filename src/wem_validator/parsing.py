"""Bounded parsing for the explicit Markdown subset used by WEM profiles."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_REFERENCE_DEFINITION = re.compile(r'^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))(?:\s+["\'(].*)?$')
_FULL_REFERENCE = re.compile(r"!?\[([^\]]*)\]\[([^\]]*)\]")
_SHORTCUT_REFERENCE = re.compile(r"!?\[([^\]\n]+)\](?![\[(])")
_RAW_HTML_ANCHOR = re.compile(r"<a\s+[^>]*(?:id|name)\s*=", re.IGNORECASE)
_ADR_IDENTITY_FIELDS = {
    "Document",
    "Identifier",
    "Title",
    "Status",
    "Created Date",
    "ASI Level",
    "Decision Authority",
    "WEM Reference",
}


@dataclass(frozen=True, slots=True)
class Frontmatter:
    values: dict[str, str]
    lines: dict[str, int]
    present: bool
    closed: bool
    duplicate_keys: tuple[str, ...]
    malformed_lines: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class MarkdownLink:
    target: str | None
    line: int
    reference_label: str | None = None


@dataclass(frozen=True, slots=True)
class ParsedMarkdown:
    frontmatter: Frontmatter
    metadata: Frontmatter
    headings: dict[str, tuple[int, ...]]
    links: tuple[MarkdownLink, ...]
    duplicate_reference_lines: tuple[int, ...]
    raw_html_anchor_lines: tuple[int, ...]


def parse_markdown(text: str) -> ParsedMarkdown:
    lines = text.splitlines()
    frontmatter = _parse_frontmatter(lines)
    headings: dict[str, list[int]] = {}
    definitions: dict[str, str] = {}
    duplicate_references: list[int] = []
    html_anchors: list[int] = []
    content_lines: list[tuple[int, str]] = []
    in_fence = False
    fence_marker = ""

    for number, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        heading = _HEADING.match(line)
        if heading:
            headings.setdefault(heading.group(2).strip(), []).append(number)
        if _RAW_HTML_ANCHOR.search(line):
            html_anchors.append(number)
        definition = _REFERENCE_DEFINITION.match(line)
        if definition:
            label = normalize_reference_label(definition.group(1))
            target = definition.group(2) or definition.group(3)
            if label in definitions:
                duplicate_references.append(number)
            else:
                definitions[label] = target
            continue
        content_lines.append((number, line))

    links: list[MarkdownLink] = []
    for number, line in content_lines:
        occupied: list[tuple[int, int]] = []
        for match in _INLINE_LINK.finditer(line):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            links.append(MarkdownLink(target=target, line=number))
            occupied.append(match.span())
        for match in _FULL_REFERENCE.finditer(line):
            label_text = match.group(2) or match.group(1)
            label = normalize_reference_label(label_text)
            links.append(
                MarkdownLink(target=definitions.get(label), line=number, reference_label=label)
            )
            occupied.append(match.span())
        for match in _SHORTCUT_REFERENCE.finditer(line):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            label = normalize_reference_label(match.group(1))
            if label in definitions:
                links.append(
                    MarkdownLink(target=definitions[label], line=number, reference_label=label)
                )

    return ParsedMarkdown(
        frontmatter=frontmatter,
        metadata=_normalized_metadata(lines, frontmatter, headings),
        headings={name: tuple(values) for name, values in headings.items()},
        links=tuple(links),
        duplicate_reference_lines=tuple(duplicate_references),
        raw_html_anchor_lines=tuple(html_anchors),
    )


def normalize_reference_label(value: str) -> str:
    return " ".join(value.split()).casefold()


def heading_anchors(parsed: ParsedMarkdown) -> frozenset[str]:
    ordered = sorted(
        ((line, heading) for heading, lines in parsed.headings.items() for line in lines),
        key=lambda item: item[0],
    )
    counts: dict[str, int] = {}
    anchors: set[str] = set()
    for _, heading in ordered:
        base = _heading_slug(heading)
        count = counts.get(base, 0)
        anchor = base if count == 0 else f"{base}-{count}"
        counts[base] = count + 1
        anchors.add(anchor)
    return frozenset(anchors)


def _heading_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    characters = [
        character for character in normalized if character.isalnum() or character in {" ", "-", "_"}
    ]
    return "-".join("".join(characters).split())


def _overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def _parse_frontmatter(lines: list[str]) -> Frontmatter:
    if not lines or lines[0].strip() != "---":
        return Frontmatter({}, {}, False, False, (), ())
    values: dict[str, str] = {}
    locations: dict[str, int] = {}
    duplicates: list[str] = []
    malformed: list[int] = []
    for index, line in enumerate(lines[1:], 2):
        if line.strip() == "---":
            return Frontmatter(
                values,
                locations,
                True,
                True,
                tuple(sorted(set(duplicates))),
                tuple(malformed),
            )
        if not line.strip():
            continue
        if ":" not in line:
            malformed.append(index)
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            malformed.append(index)
            continue
        if key in values:
            duplicates.append(key)
            continue
        values[key] = value
        locations[key] = index
    return Frontmatter(values, locations, True, False, (), ())


def _normalized_metadata(
    lines: list[str],
    frontmatter: Frontmatter,
    headings: dict[str, list[int]],
) -> Frontmatter:
    base = frontmatter if frontmatter.present else _parse_field_preamble(lines)
    values = dict(base.values)
    locations = dict(base.lines)
    for field in _ADR_IDENTITY_FIELDS - {"Document"}:
        if field in values:
            continue
        heading_lines = headings.get(field)
        if not heading_lines:
            continue
        value = _section_value(lines, heading_lines[0])
        if value is not None:
            values[field] = value
            locations[field] = heading_lines[0]
    return Frontmatter(
        values=values,
        lines=locations,
        present=base.present or bool(values),
        closed=base.closed,
        duplicate_keys=base.duplicate_keys,
        malformed_lines=base.malformed_lines,
    )


def _parse_field_preamble(lines: list[str]) -> Frontmatter:
    values: dict[str, str] = {}
    locations: dict[str, int] = {}
    duplicates: list[str] = []
    malformed: list[int] = []
    observed = False
    for index, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == "---":
            return Frontmatter(
                values,
                locations,
                observed,
                True,
                tuple(sorted(set(duplicates))),
                tuple(malformed),
            )
        if stripped.startswith("#"):
            break
        if not stripped:
            continue
        if ":" not in line:
            if observed:
                malformed.append(index)
            else:
                return Frontmatter({}, {}, False, True, (), ())
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        if key not in _ADR_IDENTITY_FIELDS or not value:
            if observed:
                malformed.append(index)
                continue
            return Frontmatter({}, {}, False, True, (), ())
        observed = True
        if key in values:
            duplicates.append(key)
            continue
        values[key] = value
        locations[key] = index
    return Frontmatter(
        values,
        locations,
        observed,
        True,
        tuple(sorted(set(duplicates))),
        tuple(malformed),
    )


def _section_value(lines: list[str], heading_line: int) -> str | None:
    for line in lines[heading_line:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            return None
        if not stripped:
            continue
        value = stripped.strip("`").strip()
        if value.endswith("."):
            value = value[:-1].rstrip()
        return value or None
    return None
