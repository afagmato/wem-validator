from wem_validator.parsing import heading_anchors, parse_markdown


def test_parsing_ignores_fenced_links_and_tracks_source_locations() -> None:
    parsed = parse_markdown(
        """---
Document: Example
Status: Draft
---
# Example
[real](target.md)
```text
[ignored](missing.md)
```
"""
    )
    assert parsed.frontmatter.values == {"Document": "Example", "Status": "Draft"}
    assert parsed.frontmatter.lines["Status"] == 3
    assert parsed.headings["Example"] == (5,)
    assert [(item.target, item.line) for item in parsed.links] == [("target.md", 6)]


def test_parsing_reports_duplicate_and_malformed_frontmatter() -> None:
    parsed = parse_markdown("---\nStatus: Draft\nStatus: Released\nmalformed\n---\n")
    assert parsed.frontmatter.duplicate_keys == ("Status",)
    assert parsed.frontmatter.malformed_lines == (4,)


def test_unclosed_frontmatter_is_explicit() -> None:
    parsed = parse_markdown("---\nDocument: Example\n")
    assert parsed.frontmatter.present is True
    assert parsed.frontmatter.closed is False


def test_reference_links_resolve_full_collapsed_and_shortcut_forms() -> None:
    parsed = parse_markdown(
        """[target]: docs/target.md#section
[full text][target]
[target][]
[target]
[missing][unknown]
"""
    )
    assert [(item.target, item.reference_label) for item in parsed.links] == [
        ("docs/target.md#section", "target"),
        ("docs/target.md#section", "target"),
        ("docs/target.md#section", "target"),
        (None, "unknown"),
    ]


def test_heading_anchor_normalization_is_deterministic_for_duplicates() -> None:
    parsed = parse_markdown("# Section Name!\n## Section Name!\n### Àmbit tècnic\n")
    assert heading_anchors(parsed) == frozenset({"section-name", "section-name-1", "àmbit-tècnic"})


def test_duplicate_definitions_and_raw_html_anchors_are_visible() -> None:
    parsed = parse_markdown('[target]: first.md\n[target]: second.md\n<a id="legacy"></a>\n')
    assert parsed.duplicate_reference_lines == (2,)
    assert parsed.raw_html_anchor_lines == (3,)
