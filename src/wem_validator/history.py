"""Bounded read-only observation of local Git history."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType

from wem_validator.model import HistoryObservation, ValidationScope

DEFAULT_MAX_HISTORY_COMMITS = 1_024
DEFAULT_MAX_HISTORY_ARTIFACTS = 4_096
DEFAULT_MAX_HISTORY_BLOB_BYTES = 1_048_576


@dataclass(frozen=True, slots=True)
class HistoryArtifact:
    revision: str
    path: str
    text: str


@dataclass(frozen=True, slots=True)
class HistorySnapshot:
    revision: str
    artifacts: tuple[HistoryArtifact, ...]


@dataclass(frozen=True, slots=True)
class GitHistoryResult:
    observation: HistoryObservation
    snapshots: tuple[HistorySnapshot, ...]
    failure: str | None = None


class _GitFailure(RuntimeError):
    pass


def observe_git_history(
    root: Path,
    *,
    current_artifacts: Mapping[str, str],
    scope: ValidationScope,
    max_commits: int = DEFAULT_MAX_HISTORY_COMMITS,
    max_artifacts: int = DEFAULT_MAX_HISTORY_ARTIFACTS,
    max_blob_bytes: int = DEFAULT_MAX_HISTORY_BLOB_BYTES,
) -> GitHistoryResult:
    """Observe the current HEAD first-parent chain without modifying Git state."""

    if min(max_commits, max_artifacts, max_blob_bytes) < 1:
        raise ValueError("history limits must be positive")
    selected_root = root.resolve()
    try:
        top_level_raw = _run_git(selected_root, "rev-parse", "--show-toplevel")
        top_level = Path(_decode(top_level_raw, "repository root").strip()).resolve()
        if os.path.normcase(str(top_level)) != os.path.normcase(str(selected_root)):
            return _unavailable("the selected target is not the Git repository root")

        shallow = _decode(
            _run_git(selected_root, "rev-parse", "--is-shallow-repository"),
            "shallow-repository state",
        ).strip()
        if shallow == "true":
            return _insufficient("the selected repository has shallow or incomplete history")
        if shallow != "false":
            return _unavailable("Git did not report a supported repository-history state")

        current_revision = _decode(
            _run_git(selected_root, "rev-parse", "HEAD"), "current revision"
        ).strip()
        revisions = tuple(
            item
            for item in _decode(
                _run_git(selected_root, "rev-list", "--first-parent", "--reverse", "HEAD"),
                "revision list",
            ).splitlines()
            if item
        )
    except _GitFailure as error:
        return _unavailable(str(error))

    if len(revisions) > max_commits:
        return _insufficient(
            f"first-parent history exceeds the {max_commits} commit observation limit",
            current_revision=current_revision,
            commit_count=len(revisions),
        )

    snapshots: list[HistorySnapshot] = []
    artifact_count = 0
    try:
        for revision in revisions:
            tree_paths = _tree_paths(selected_root, revision)
            artifacts: list[HistoryArtifact] = []
            for path in tree_paths:
                if not _path_in_scope(path, scope):
                    continue
                artifact_count += 1
                if artifact_count > max_artifacts:
                    return _insufficient(
                        f"history exceeds the {max_artifacts} artifact observation limit",
                        current_revision=current_revision,
                        commit_count=len(revisions),
                        artifact_count=artifact_count,
                    )
                object_name = f"{revision}:{path}"
                size_text = _decode(
                    _run_git(selected_root, "cat-file", "-s", object_name),
                    "historical blob size",
                ).strip()
                try:
                    size = int(size_text)
                except ValueError as error:
                    raise _GitFailure("Git returned an invalid historical blob size") from error
                if size > max_blob_bytes:
                    return _insufficient(
                        f"historical artifact exceeds the {max_blob_bytes} byte observation limit",
                        current_revision=current_revision,
                        commit_count=len(revisions),
                        artifact_count=artifact_count,
                    )
                text = _decode(
                    _run_git(selected_root, "cat-file", "blob", object_name),
                    "historical Markdown artifact",
                )
                artifacts.append(HistoryArtifact(revision, path, text))
            snapshots.append(HistorySnapshot(revision, tuple(artifacts)))
    except _GitFailure as error:
        return _unavailable(
            str(error),
            current_revision=current_revision,
            commit_count=len(revisions),
            artifact_count=artifact_count,
        )

    current = tuple(
        HistoryArtifact("WORKTREE", path, text)
        for path, text in sorted(current_artifacts.items())
        if _path_in_scope(path, scope)
    )
    artifact_count += len(current)
    if artifact_count > max_artifacts:
        return _insufficient(
            f"history exceeds the {max_artifacts} artifact observation limit",
            current_revision=current_revision,
            commit_count=len(revisions),
            artifact_count=artifact_count,
        )
    snapshots.append(HistorySnapshot("WORKTREE", current))
    observation = HistoryObservation(
        mode="git",
        availability="complete",
        complete=True,
        current_revision=current_revision,
        boundary="first-parent",
        commit_count=len(revisions),
        artifact_count=artifact_count,
        limitations=(
            "Git lifecycle evaluation is bounded to the current HEAD first-parent history.",
            "Git authorship and commit metadata do not prove human approval.",
        ),
    )
    return GitHistoryResult(observation, tuple(snapshots))


def frozen_artifacts(values: Mapping[str, str]) -> Mapping[str, str]:
    """Return an immutable copy suitable for an observation request."""

    return MappingProxyType(dict(values))


def _tree_paths(root: Path, revision: str) -> tuple[str, ...]:
    raw = _run_git(root, "ls-tree", "-r", "-z", "--name-only", revision, "--", "decisions")
    paths: list[str] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        try:
            path = item.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise _GitFailure("a historical path is not valid UTF-8") from error
        if "\\" in path or path.startswith("/") or ".." in PurePosixPath(path).parts:
            raise _GitFailure("Git returned a path outside the supported repository-relative form")
        paths.append(path)
    return tuple(sorted(paths))


def _path_in_scope(path: str, scope: ValidationScope) -> bool:
    if not path.startswith("decisions/") or not path.casefold().endswith(".md"):
        return False
    if scope.mode != "manifest":
        return True
    candidate = PurePosixPath(path)
    if not any(candidate.full_match(pattern) for pattern in scope.include_patterns):
        return False
    return not any(candidate.full_match(pattern) for pattern in scope.exclude_patterns)


def _run_git(root: Path, *arguments: str) -> bytes:
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_PAGER": "cat",
            "LC_ALL": "C",
        }
    )
    try:
        completed = subprocess.run(
            ("git", "-C", str(root), *arguments),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            timeout=30,
            env=environment,
        )
    except FileNotFoundError as error:
        raise _GitFailure("the Git executable is unavailable") from error
    except subprocess.TimeoutExpired as error:
        raise _GitFailure("a bounded Git observation timed out") from error
    if completed.returncode != 0:
        raise _GitFailure("the selected target is not an observable local Git repository")
    return completed.stdout


def _decode(value: bytes, subject: str) -> str:
    try:
        return value.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise _GitFailure(f"{subject} is not valid UTF-8") from error


def _unavailable(
    reason: str,
    *,
    current_revision: str | None = None,
    commit_count: int = 0,
    artifact_count: int = 0,
) -> GitHistoryResult:
    observation = HistoryObservation(
        mode="git",
        availability="unavailable",
        complete=False,
        current_revision=current_revision,
        boundary="first-parent",
        commit_count=commit_count,
        artifact_count=artifact_count,
        limitations=(reason,),
    )
    return GitHistoryResult(observation, (), reason)


def _insufficient(
    reason: str,
    *,
    current_revision: str | None = None,
    commit_count: int = 0,
    artifact_count: int = 0,
) -> GitHistoryResult:
    observation = HistoryObservation(
        mode="git",
        availability="insufficient",
        complete=False,
        current_revision=current_revision,
        boundary="first-parent",
        commit_count=commit_count,
        artifact_count=artifact_count,
        limitations=(reason,),
    )
    return GitHistoryResult(observation, (), reason)
