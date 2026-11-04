"""Deterministic validation orchestration without target mutation."""

from __future__ import annotations

from pathlib import Path

from wem_validator.configuration import ManifestFailure, ValidationManifest, load_manifest
from wem_validator.discovery import DEFAULT_MAX_FILE_BYTES, DEFAULT_MAX_FILES, discover_markdown
from wem_validator.model import Finding, ValidationReport, ValidationScope
from wem_validator.parsing import parse_markdown
from wem_validator.profiles import resolve_profile
from wem_validator.rules import evaluate_document


def validate_target(
    target: Path,
    *,
    profile_id: str | None,
    manifest_path: Path | None = None,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_files: int = DEFAULT_MAX_FILES,
) -> ValidationReport:
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
    return ValidationReport(
        profile=profile.identifier,
        wem_reference=profile.wem_reference,
        target=".",
        scope=scope,
        findings=tuple(sorted(findings)),
        limitations=profile.limitations,
    )
