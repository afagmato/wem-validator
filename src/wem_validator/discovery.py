"""Read-only, bounded Markdown discovery without symbolic-link traversal."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MAX_FILE_BYTES = 1_048_576
DEFAULT_MAX_FILES = 4_096


class DiscoveryFailure(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DiscoveredFile:
    absolute_path: Path
    relative_path: str
    text: str | None
    issue: str | None = None


def discover_markdown(
    target: Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_files: int = DEFAULT_MAX_FILES,
) -> tuple[DiscoveredFile, ...]:
    if max_file_bytes < 1 or max_files < 1:
        raise ValueError("discovery limits must be positive")
    if not target.exists():
        raise DiscoveryFailure("target does not exist")
    if target.is_symlink():
        return (DiscoveredFile(target, target.name, None, "symbolic link target is unsupported"),)

    root = target.resolve() if target.is_dir() else target.resolve().parent
    paths: list[tuple[Path, str, str | None]] = []
    if target.is_file():
        if target.suffix.lower() != ".md":
            raise DiscoveryFailure("target file is not Markdown")
        paths.append((target.resolve(), target.name, None))
    elif target.is_dir():
        _walk(root, root, paths, max_files=max_files)
    else:
        raise DiscoveryFailure("target is neither a regular file nor a directory")
    if not paths:
        raise DiscoveryFailure("target contains no Markdown files")

    discovered: list[DiscoveredFile] = []
    for path, relative, issue in sorted(paths, key=lambda item: item[1]):
        if issue is not None:
            discovered.append(DiscoveredFile(path, relative, None, issue))
            continue
        try:
            size = path.stat().st_size
            if size > max_file_bytes:
                discovered.append(
                    DiscoveredFile(path, relative, None, f"file exceeds {max_file_bytes} bytes")
                )
                continue
            raw = path.read_bytes()
            text = raw.decode("utf-8", errors="strict")
        except (OSError, UnicodeDecodeError) as error:
            discovered.append(
                DiscoveredFile(
                    path,
                    relative,
                    None,
                    f"file cannot be read as UTF-8: {error.__class__.__name__}",
                )
            )
            continue
        discovered.append(DiscoveredFile(path, relative, text))
    return tuple(discovered)


def _walk(
    directory: Path,
    root: Path,
    paths: list[tuple[Path, str, str | None]],
    *,
    max_files: int,
) -> None:
    try:
        entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold())
    except OSError as error:
        raise DiscoveryFailure("target traversal failed") from error
    for entry in entries:
        path = Path(entry.path)
        relative = path.relative_to(root).as_posix()
        if entry.is_symlink():
            paths.append((path, relative, "symbolic link is not followed"))
            if len(paths) > max_files:
                raise DiscoveryFailure(f"target exceeds {max_files} discovered entries")
            continue
        if entry.is_dir(follow_symlinks=False):
            if entry.name == ".git":
                continue
            _walk(path, root, paths, max_files=max_files)
            continue
        if entry.is_file(follow_symlinks=False) and path.suffix.lower() == ".md":
            paths.append((path, relative, None))
            if len(paths) > max_files:
                raise DiscoveryFailure(f"target exceeds {max_files} Markdown files")
