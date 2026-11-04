"""Strict explicit repository-validation manifest handling."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Never, cast

from wem_validator.discovery import DEFAULT_MAX_FILE_BYTES, DEFAULT_MAX_FILES, DiscoveredFile

MAX_MANIFEST_BYTES = 65_536
_REQUIRED_MEMBERS = {"format-version", "profile", "include", "exclude"}
_OPTIONAL_MEMBERS = {"limits"}
_LIMIT_MEMBERS = {"max-file-bytes", "max-files"}


class ManifestFailure(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ValidationManifest:
    identity: str
    profile: str
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    max_file_bytes: int
    max_files: int

    def select(
        self, discovered: tuple[DiscoveredFile, ...]
    ) -> tuple[tuple[DiscoveredFile, ...], tuple[tuple[str, int], ...]]:
        matched_includes = {pattern: 0 for pattern in self.include}
        included: list[DiscoveredFile] = []
        for item in discovered:
            path = PurePosixPath(item.relative_path)
            matches = [pattern for pattern in self.include if path.full_match(pattern)]
            for pattern in matches:
                matched_includes[pattern] += 1
            if matches:
                included.append(item)
        unmatched = [pattern for pattern, count in matched_includes.items() if count == 0]
        if unmatched:
            _fail(f"include pattern matched no Markdown input: {unmatched[0]}")

        excluded_counts = {pattern: 0 for pattern in self.exclude}
        selected: list[DiscoveredFile] = []
        for item in included:
            path = PurePosixPath(item.relative_path)
            excluded_by = next(
                (pattern for pattern in self.exclude if path.full_match(pattern)), None
            )
            if excluded_by is None:
                selected.append(item)
            else:
                excluded_counts[excluded_by] += 1
        if not selected:
            _fail("manifest scope contains no Markdown input after exclusions")
        return tuple(selected), tuple(excluded_counts.items())


def load_manifest(path: Path, *, repository: Path) -> ValidationManifest:
    root = repository.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        _fail("manifest path escapes the selected repository")
    if not resolved.is_file() or resolved.is_symlink():
        _fail("manifest is not a regular local file")
    try:
        raw = resolved.read_bytes()
    except OSError as error:
        raise ManifestFailure("manifest could not be read") from error
    if len(raw) > MAX_MANIFEST_BYTES:
        _fail(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    try:
        document = tomllib.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise ManifestFailure("manifest is not valid UTF-8 TOML") from error
    if set(document) - (_REQUIRED_MEMBERS | _OPTIONAL_MEMBERS):
        _fail("manifest contains unknown top-level members")
    if not _REQUIRED_MEMBERS.issubset(document):
        _fail("manifest is missing required members")
    if document["format-version"] != "0.1.0":
        _fail("manifest format version is unsupported")
    profile = _text(document, "profile")
    include = _patterns(document, "include", allow_empty=False)
    exclude = _patterns(document, "exclude", allow_empty=True)
    if len(set(include)) != len(include) or len(set(exclude)) != len(exclude):
        _fail("manifest patterns must be unique within each list")

    max_file_bytes = DEFAULT_MAX_FILE_BYTES
    max_files = DEFAULT_MAX_FILES
    limits = document.get("limits")
    if limits is not None:
        if not isinstance(limits, dict) or set(limits) - _LIMIT_MEMBERS:
            _fail("manifest limits are invalid")
        max_file_bytes = _lower_limit(
            cast(dict[str, object], limits),
            "max-file-bytes",
            DEFAULT_MAX_FILE_BYTES,
        )
        max_files = _lower_limit(cast(dict[str, object], limits), "max-files", DEFAULT_MAX_FILES)
    return ValidationManifest(
        identity=resolved.relative_to(root).as_posix(),
        profile=profile,
        include=include,
        exclude=exclude,
        max_file_bytes=max_file_bytes,
        max_files=max_files,
    )


def _text(document: dict[str, object], member: str) -> str:
    value = document.get(member)
    if not isinstance(value, str) or not value:
        _fail(f"manifest member is not a non-empty string: {member}")
    return value


def _patterns(document: dict[str, object], member: str, *, allow_empty: bool) -> tuple[str, ...]:
    value = document.get(member)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        _fail(f"manifest member is not a string array: {member}")
    patterns = tuple(cast(list[str], value))
    if not allow_empty and not patterns:
        _fail(f"manifest member may not be empty: {member}")
    for pattern in patterns:
        if (
            not pattern
            or "\\" in pattern
            or pattern.startswith("/")
            or ":" in pattern
            or ".." in PurePosixPath(pattern).parts
        ):
            _fail(f"manifest pattern is not repository-relative: {pattern}")
    return patterns


def _lower_limit(document: dict[str, object], member: str, hard_limit: int) -> int:
    value = document.get(member, hard_limit)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > hard_limit:
        _fail(f"manifest limit must be from 1 through {hard_limit}: {member}")
    return value


def _fail(message: str) -> Never:
    raise ManifestFailure(message)
