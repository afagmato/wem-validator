from __future__ import annotations

import json
from pathlib import Path

import pytest

from wem_validator.cli import main


def test_json_and_text_project_the_same_findings(
    repository_root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = repository_root / "tests" / "fixtures" / "invalid"
    assert main(["validate", str(target), "--format", "json"]) == 1
    json_result = json.loads(capsys.readouterr().out)
    json_ids = {item["ruleId"] for item in json_result["findings"]}

    assert main(["validate", str(target), "--format", "text"]) == 1
    text_result = capsys.readouterr().out
    assert json_ids
    assert all(identifier in text_result for identifier in json_ids)
    assert json_result["profile"] == "wem-1.2.0"
    assert json_result["target"] == "."


def test_valid_target_returns_zero(
    repository_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = repository_root / "tests" / "fixtures" / "valid"
    assert main(["validate", str(target), "--format", "json"]) == 0
    observed = json.loads(capsys.readouterr().out)
    expected = json.loads(
        (repository_root / "tests" / "fixtures" / "expected" / "valid-report.json").read_text(
            encoding="utf-8"
        )
    )
    assert observed == expected


def test_invocation_failure_returns_two_without_absolute_path(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = tmp_path / "private" / "missing"
    assert main(["validate", str(missing), "--format", "json"]) == 2
    captured = capsys.readouterr()
    payload = json.loads(captured.err)
    assert payload["error"]["code"] == "input_unavailable"
    assert str(tmp_path) not in captured.err


def test_unsupported_profile_returns_two(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "input.md").write_text("# Input\n", encoding="utf-8")
    assert main(["validate", str(tmp_path), "--profile", "wem-9.9.9"]) == 2
    assert "unsupported_profile" in capsys.readouterr().err


def test_empty_target_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate", str(tmp_path)]) == 2
    assert "target contains no Markdown files" in capsys.readouterr().err


def test_manifest_profile_conflict_returns_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "input.md").write_text("# Input\n", encoding="utf-8")
    manifest = tmp_path / "wem-validator.toml"
    manifest.write_text(
        'format-version = "0.1.0"\nprofile = "wem-1.2.0"\ninclude = ["**/*.md"]\nexclude = []\n',
        encoding="utf-8",
    )
    assert (
        main(
            [
                "validate",
                str(tmp_path),
                "--config",
                str(manifest),
                "--profile",
                "wem-9.9.9",
                "--format",
                "json",
            ]
        )
        == 2
    )
    payload = json.loads(capsys.readouterr().err)
    assert payload["error"]["code"] == "invalid_manifest"


def test_profile_inventory_is_explicit(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["profile", "inspect", "--profile", "wem-1.2.0", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["profile"] == "wem-1.2.0"
    assert payload["formatVersion"] == "0.2.0"
    assert payload["profileVersion"] == "0.3.0"
    assert {item["ruleId"] for item in payload["rules"]} >= {
        "WEMV120-LINK-002",
        "WEMV120-LINK-003",
        "WEMV120-MANIFEST-001",
        "WEMV120-HISTORY-005",
    }


def test_git_history_mode_validates_the_maintained_repository(
    repository_root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (
        main(
            [
                "validate",
                str(repository_root),
                "--config",
                str(repository_root / "wem-validator.toml"),
                "--history",
                "git",
                "--format",
                "json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["history"]["availability"] == "complete"
    assert payload["history"]["boundary"] == "first-parent"
    assert payload["history"]["commitCount"] >= 1
    assert not {item["ruleId"] for item in payload["findings"]} & {
        "WEMV120-HISTORY-001",
        "WEMV120-HISTORY-002",
        "WEMV120-HISTORY-003",
        "WEMV120-HISTORY-004",
        "WEMV120-HISTORY-005",
    }


def test_requested_git_history_fails_explicitly_for_a_non_repository(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "input.md").write_text("# Input\n", encoding="utf-8")
    assert main(["validate", str(tmp_path), "--history", "git", "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["history"]["availability"] == "unavailable"
    assert {item["ruleId"] for item in payload["findings"]} == {"WEMV120-HISTORY-001"}
