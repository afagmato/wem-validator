from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from wem_validator.history import observe_git_history
from wem_validator.lifecycle import evaluate_lifecycle_history
from wem_validator.model import ValidationScope
from wem_validator.profiles import resolve_profile


def _git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repository), *arguments),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def _repository(path: Path) -> Path:
    path.mkdir()
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.name", "WEM Validator Test")
    _git(path, "config", "user.email", "wem-validator@example.invalid")
    return path


def _commit(repository: Path, message: str) -> None:
    _git(repository, "add", "--all")
    _git(repository, "commit", "-m", message)


def _write_adr(
    repository: Path,
    *,
    identifier: str = "TEST-ADR-001",
    status: str,
    rows: tuple[tuple[str, str, str, str], ...],
    created_date: str = "2026-11-04",
) -> Path:
    decisions = repository / "decisions"
    decisions.mkdir(exist_ok=True)
    path = decisions / f"{identifier}.md"
    table = "\n".join(f"| {' | '.join(row)} |" for row in rows)
    path.write_text(
        f"""---
Document: Architecture Decision Record
Identifier: {identifier}
Title: Test lifecycle observation
Status: {status}
Created Date: {created_date}
ASI Level: 3
Decision Authority: Test Owner
WEM Reference: WEM 1.2.0 — Released
---

# {identifier} — Test lifecycle observation

## Status History

| Date | Status | Decision Authority | Reason |
| --- | --- | --- | --- |
{table}

## Context

Test context.
""",
        encoding="utf-8",
    )
    return path


def _current_artifacts(repository: Path) -> dict[str, str]:
    decisions = repository / "decisions"
    if not decisions.exists():
        return {}
    return {
        path.relative_to(repository).as_posix(): path.read_text(encoding="utf-8")
        for path in decisions.glob("*.md")
    }


def _observe(repository: Path, **limits: int):  # type: ignore[no-untyped-def]
    return observe_git_history(
        repository,
        current_artifacts=_current_artifacts(repository),
        scope=ValidationScope(),
        **limits,
    )


def test_git_observation_is_complete_deterministic_and_read_only(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repository")
    proposed = ("2026-11-04", "Proposed", "Test Owner", "Evaluation opened.")
    accepted = ("2026-11-04", "Accepted", "Test Owner", "Decision approved.")
    _write_adr(repository, status="Proposed", rows=(proposed,))
    _commit(repository, "propose decision")
    _write_adr(repository, status="Accepted", rows=(proposed, accepted))
    _commit(repository, "accept decision")

    status_before = _git(repository, "status", "--porcelain=v1")
    refs_before = _git(repository, "show-ref")
    first = _observe(repository)
    second = _observe(repository)

    assert first == second
    assert first.observation.availability == "complete"
    assert first.observation.complete is True
    assert first.observation.commit_count == 2
    assert first.observation.artifact_count == 3
    assert evaluate_lifecycle_history(first, profile=resolve_profile("wem-1.2.0")) == ()
    assert _git(repository, "status", "--porcelain=v1") == status_before
    assert _git(repository, "show-ref") == refs_before


def test_lifecycle_rules_detect_rewrite_invalid_transition_removal_and_reuse(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path / "repository")
    proposed = ("2026-11-04", "Proposed", "Test Owner", "Evaluation opened.")
    accepted = ("2026-11-04", "Accepted", "Test Owner", "Decision approved.")
    _write_adr(repository, status="Proposed", rows=(proposed,))
    _commit(repository, "propose")
    _write_adr(repository, status="Accepted", rows=(proposed, accepted))
    _commit(repository, "accept")

    rewritten = ("2026-11-04", "Proposed", "Test Owner", "Rewritten history.")
    invalid = ("2026-11-04", "Proposed", "Test Owner", "Invalid reversal.")
    _write_adr(repository, status="Proposed", rows=(rewritten, accepted, invalid))
    _commit(repository, "rewrite and reverse")
    (repository / "decisions" / "TEST-ADR-001.md").unlink()
    _commit(repository, "remove decision")
    _write_adr(
        repository,
        status="Proposed",
        rows=(proposed,),
        created_date="2026-11-05",
    )
    _commit(repository, "reuse identifier")

    findings = evaluate_lifecycle_history(
        _observe(repository), profile=resolve_profile("wem-1.2.0")
    )
    identifiers = {finding.rule_id for finding in findings}
    assert {
        "WEMV120-HISTORY-003",
        "WEMV120-HISTORY-004",
        "WEMV120-HISTORY-005",
    }.issubset(identifiers)


def test_current_status_must_match_latest_history_row(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repository")
    proposed = ("2026-11-04", "Proposed", "Test Owner", "Evaluation opened.")
    _write_adr(repository, status="Proposed", rows=(proposed,))
    _commit(repository, "propose")
    _write_adr(repository, status="Accepted", rows=(proposed,))

    findings = evaluate_lifecycle_history(
        _observe(repository), profile=resolve_profile("wem-1.2.0")
    )
    assert {finding.rule_id for finding in findings} == {"WEMV120-HISTORY-002"}


def test_requested_history_reports_unavailable_and_bounded_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    non_repository = tmp_path / "not-a-repository"
    non_repository.mkdir()
    unavailable = _observe(non_repository)
    assert unavailable.observation.availability == "unavailable"

    repository = _repository(tmp_path / "repository")
    proposed = ("2026-11-04", "Proposed", "Test Owner", "Evaluation opened.")
    _write_adr(repository, status="Proposed", rows=(proposed,))
    _commit(repository, "first")
    (repository / "marker.md").write_text("# Second commit\n", encoding="utf-8")
    _commit(repository, "second")

    assert _observe(repository, max_commits=1).observation.availability == "insufficient"
    assert _observe(repository, max_artifacts=1).observation.availability == "insufficient"
    assert _observe(repository, max_blob_bytes=1).observation.availability == "insufficient"

    subdirectory = repository / "decisions"
    assert _observe(subdirectory).observation.availability == "unavailable"

    def missing_git(*args: object, **kwargs: object) -> None:
        raise FileNotFoundError

    monkeypatch.setattr("wem_validator.history.subprocess.run", missing_git)
    missing = _observe(repository)
    assert missing.observation.availability == "unavailable"
    assert "executable" in (missing.failure or "")


def test_shallow_history_is_explicitly_insufficient(tmp_path: Path) -> None:
    source = _repository(tmp_path / "source")
    proposed = ("2026-11-04", "Proposed", "Test Owner", "Evaluation opened.")
    _write_adr(source, status="Proposed", rows=(proposed,))
    _commit(source, "first")
    (source / "marker.md").write_text("# Second commit\n", encoding="utf-8")
    _commit(source, "second")

    shallow = tmp_path / "shallow"
    subprocess.run(
        ("git", "clone", "--depth", "1", "--no-local", source.as_uri(), str(shallow)),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    result = _observe(shallow)
    assert result.observation.availability == "insufficient"
    assert "shallow" in (result.failure or "")
