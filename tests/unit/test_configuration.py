from __future__ import annotations

from pathlib import Path

import pytest

from wem_validator.configuration import ManifestFailure, load_manifest
from wem_validator.discovery import discover_markdown


def _manifest(path: Path, content: str) -> Path:
    manifest = path / "wem-validator.toml"
    manifest.write_text(content, encoding="utf-8")
    return manifest


def test_manifest_selects_and_counts_explicit_exclusions(tmp_path: Path) -> None:
    (tmp_path / "kept.md").write_text("# Kept\n", encoding="utf-8")
    excluded = tmp_path / "fixtures"
    excluded.mkdir()
    (excluded / "invalid.md").write_text("# Invalid\n", encoding="utf-8")
    manifest = load_manifest(
        _manifest(
            tmp_path,
            'format-version = "0.1.0"\n'
            'profile = "wem-1.2.0"\n'
            'include = ["**/*.md"]\n'
            'exclude = ["fixtures/**"]\n',
        ),
        repository=tmp_path,
    )
    selected, counts = manifest.select(discover_markdown(tmp_path))
    assert [item.relative_path for item in selected] == ["kept.md"]
    assert counts == (("fixtures/**", 1),)


@pytest.mark.parametrize(
    "pattern",
    ["/absolute/*.md", "../escape.md", "folder\\file.md", "C:/*.md"],
)
def test_manifest_rejects_unsafe_patterns(tmp_path: Path, pattern: str) -> None:
    with pytest.raises(ManifestFailure, match="not repository-relative"):
        load_manifest(
            _manifest(
                tmp_path,
                'format-version = "0.1.0"\n'
                'profile = "wem-1.2.0"\n'
                f'include = ["{pattern.replace(chr(92), chr(92) * 2)}"]\n'
                "exclude = []\n",
            ),
            repository=tmp_path,
        )


def test_manifest_cannot_raise_hard_limits(tmp_path: Path) -> None:
    with pytest.raises(ManifestFailure, match="max-files"):
        load_manifest(
            _manifest(
                tmp_path,
                'format-version = "0.1.0"\n'
                'profile = "wem-1.2.0"\n'
                'include = ["**/*.md"]\n'
                "exclude = []\n"
                "[limits]\n"
                "max-files = 4097\n",
            ),
            repository=tmp_path,
        )


def test_manifest_rejects_unmatched_include(tmp_path: Path) -> None:
    (tmp_path / "present.md").write_text("# Present\n", encoding="utf-8")
    manifest = load_manifest(
        _manifest(
            tmp_path,
            'format-version = "0.1.0"\n'
            'profile = "wem-1.2.0"\n'
            'include = ["missing/**/*.md"]\n'
            "exclude = []\n",
        ),
        repository=tmp_path,
    )
    with pytest.raises(ManifestFailure, match="matched no Markdown input"):
        manifest.select(discover_markdown(tmp_path))


def test_manifest_path_must_remain_inside_repository(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    outside = _manifest(
        tmp_path,
        'format-version = "0.1.0"\nprofile = "wem-1.2.0"\ninclude = ["**/*.md"]\nexclude = []\n',
    )
    with pytest.raises(ManifestFailure, match="escapes"):
        load_manifest(outside, repository=repository)
