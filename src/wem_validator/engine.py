"""Deterministic validation orchestration without target mutation."""

from __future__ import annotations

from pathlib import Path

from wem_validator.configuration import ManifestFailure, ValidationManifest, load_manifest
from wem_validator.discovery import DEFAULT_MAX_FILE_BYTES, DEFAULT_MAX_FILES, discover_markdown
from wem_validator.history import GitHistoryResult, frozen_artifacts, observe_git_history
from wem_validator.lifecycle import evaluate_lifecycle_history
from wem_validator.model import Finding, HistoryObservation, ValidationReport, ValidationScope
from wem_validator.parsing import parse_markdown
from wem_validator.profiles import resolve_profile
from wem_validator.rules import evaluate_document


def validate_target(
    target: Path,
    *,
    profile_id: str | None,
    manifest_path: Path | None = None,
    history_mode: str = "none",
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_files: int = DEFAULT_MAX_FILES,
) -> ValidationReport:
    if history_mode not in {"none", "git"}:
        raise ValueError(f"unsupported history mode: {history_mode}")
    selected = target.resolve()
    manifest: ValidationManifest | None = None
    if manifest_path is not None:
        if not selected.is_dir():
            raise ManifestFailure("manifest validation requires a repository directory target")
        manifest = load_manifest(manifest_path, repository=selected)
        if profile_id is not None and profile_id != manifest.profile:
            raise ManifestFailure("command profile conflicts with manifest profile")
        profile_id = manifest.profile
        max_file_bytes = manifest.max_file_bytes
        max_files = manifest.max_files
    profile = resolve_profile(profile_id or "wem-1.2.0")
    root = selected if selected.is_dir() else selected.parent
    discovered = discover_markdown(
        target,
        max_file_bytes=max_file_bytes,
        max_files=max_files,
    )
    documents = {
        item.absolute_path.resolve(): parse_markdown(item.text)
        for item in discovered
        if item.text is not None
    }
    if manifest is None:
        evaluated = discovered
        scope = ValidationScope()
    else:
        evaluated, excluded_counts = manifest.select(discovered)
        scope = ValidationScope(
            mode="manifest",
            manifest=manifest.identity,
            include_patterns=manifest.include,
            exclude_patterns=manifest.exclude,
            excluded_path_counts=excluded_counts,
        )
    findings: list[Finding] = []
    for item in evaluated:
        parsed = documents.get(item.absolute_path.resolve())
        findings.extend(
            evaluate_document(
                item,
                parsed,
                root=root,
                profile=profile,
                documents=documents,
            )
        )
    history = HistoryObservation()
    if history_mode == "git":
        if not selected.is_dir():
            reason = "Git history requires a repository directory target"
            history_result = GitHistoryResult(
                observation=HistoryObservation(
                    mode="git",
                    availability="unavailable",
                    complete=False,
                    boundary="first-parent",
                    limitations=(reason,),
                ),
                snapshots=(),
                failure=reason,
            )
        else:
            current_artifacts = frozen_artifacts(
                {item.relative_path: item.text for item in evaluated if item.text is not None}
            )
            history_result = observe_git_history(
                selected,
                current_artifacts=current_artifacts,
                scope=scope,
            )
        history = history_result.observation
        findings.extend(evaluate_lifecycle_history(history_result, profile=profile))
    return ValidationReport(
        profile=profile.identifier,
        profile_version=profile.version,
        wem_reference=profile.wem_reference,
        target=".",
        scope=scope,
        history=history,
        findings=tuple(sorted(findings)),
        limitations=profile.limitations + history.limitations,
    )
