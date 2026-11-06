from __future__ import annotations

import shutil
from pathlib import Path

from wem_validator.engine import validate_target
from wem_validator.model import Outcome


def test_valid_fixture_has_no_findings(repository_root: Path) -> None:
    report = validate_target(
        repository_root / "tests" / "fixtures" / "valid",
        profile_id="wem-1.2.0",
    )
    assert report.findings == ()
    assert report.failed is False


def test_invalid_fixture_reports_independent_rule_failures(repository_root: Path) -> None:
    report = validate_target(
        repository_root / "tests" / "fixtures" / "invalid",
        profile_id="wem-1.2.0",
    )
    rule_ids = {item.rule_id for item in report.findings}
    assert {
        "WEMV120-FM-003",
        "WEMV120-LINK-001",
        "WEMV120-ADR-001",
        "WEMV120-ADR-002",
        "WEMV120-ADR-003",
    }.issubset(rule_ids)
    assert all(item.outcome is Outcome.ERROR for item in report.findings)
    assert report.failed is True


def test_validation_is_deterministic_and_read_only(tmp_path: Path, repository_root: Path) -> None:
    target = tmp_path / "target"
    shutil.copytree(repository_root / "tests" / "fixtures" / "valid", target)
    before = {
        path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()
    }
    first = validate_target(target, profile_id="wem-1.2.0").as_json()
    second = validate_target(target, profile_id="wem-1.2.0").as_json()
    after = {
        path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()
    }
    assert first == second
    assert after == before


def test_relative_link_cannot_escape_selected_target(tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    target = tmp_path / "target"
    target.mkdir()
    (target / "inside.md").write_text("[escape](../outside.md)\n", encoding="utf-8")
    report = validate_target(target, profile_id="wem-1.2.0")
    assert len(report.findings) == 1
    assert "escapes" in report.findings[0].explanation


def test_reference_style_link_is_explicitly_unsupported(repository_root: Path) -> None:
    report = validate_target(
        repository_root / "tests" / "fixtures" / "unsupported",
        profile_id="wem-1.2.0",
    )
    assert len(report.findings) == 1
    assert report.findings[0].outcome is Outcome.UNSUPPORTED


def test_reference_and_cross_document_anchor_links_are_validated(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text(
        "# Section Name\n## Section Name\n",
        encoding="utf-8",
    )
    (tmp_path / "source.md").write_text(
        "[target]: target.md#section-name-1\n[valid][target]\n",
        encoding="utf-8",
    )
    report = validate_target(tmp_path, profile_id="wem-1.2.0")
    assert report.findings == ()


def test_missing_reference_definition_and_anchor_are_errors(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("# Existing\n", encoding="utf-8")
    (tmp_path / "source.md").write_text(
        "[missing][undefined]\n[anchor](target.md#absent)\n",
        encoding="utf-8",
    )
    report = validate_target(tmp_path, profile_id="wem-1.2.0")
    assert {item.rule_id for item in report.findings} == {
        "WEMV120-LINK-002",
        "WEMV120-LINK-003",
    }


def test_manifest_scope_is_reported_and_read_only(tmp_path: Path) -> None:
    (tmp_path / "kept.md").write_text("# Kept\n", encoding="utf-8")
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "invalid.md").write_text("[missing](none.md)\n", encoding="utf-8")
    manifest = tmp_path / "wem-validator.toml"
    manifest.write_text(
        'format-version = "0.1.0"\n'
        'profile = "wem-1.2.0"\n'
        'include = ["**/*.md"]\n'
        'exclude = ["fixtures/**"]\n',
        encoding="utf-8",
    )
    before = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    report = validate_target(tmp_path, profile_id=None, manifest_path=manifest)
    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert report.findings == ()
    assert report.scope.mode == "manifest"
    assert report.scope.excluded_path_counts == (("fixtures/**", 1),)
    assert before == after


def test_unextractable_adr_identity_is_explicitly_unsupported(tmp_path: Path) -> None:
    decisions = tmp_path / "decisions"
    decisions.mkdir()
    (decisions / "EXAMPLE-ADR-001.md").write_text(
        """# Example

## Identifier

## Title

Example

## Status

Proposed

## Created Date

2026-11-06

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
| 2026-11-06 | Proposed | Project Owner | Evaluation opened. |

## Decision Authority

Project Owner

## WEM Reference

WEM 1.2.0 — Released

## Context

Context.

## Decision

Decision.

## Consequences

Consequences.

## ASI Level

ASI-3

## Related Principles

WEM-P-003.
""",
        encoding="utf-8",
    )
    report = validate_target(tmp_path, profile_id="wem-1.2.0")
    assert {finding.rule_id for finding in report.findings} == {"WEMV120-INPUT-001"}
    assert report.findings[0].outcome is Outcome.UNSUPPORTED
