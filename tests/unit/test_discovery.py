from __future__ import annotations

from pathlib import Path

import pytest

from wem_validator.discovery import DiscoveryFailure, discover_markdown


def test_discovery_is_sorted_and_skips_git(tmp_path: Path) -> None:
    (tmp_path / "z.md").write_text("# Z\n", encoding="utf-8")
    (tmp_path / "a.md").write_text("# A\n", encoding="utf-8")
    git = tmp_path / ".git"
    git.mkdir()
    (git / "hidden.md").write_text("# Hidden\n", encoding="utf-8")
    assert [item.relative_path for item in discover_markdown(tmp_path)] == ["a.md", "z.md"]


def test_discovery_enforces_file_and_count_bounds(tmp_path: Path) -> None:
    (tmp_path / "large.md").write_text("12345", encoding="utf-8")
    result = discover_markdown(tmp_path, max_file_bytes=4)
    assert result[0].issue == "file exceeds 4 bytes"
    (tmp_path / "second.md").write_text("ok", encoding="utf-8")
    with pytest.raises(DiscoveryFailure, match="exceeds 1 Markdown files"):
        discover_markdown(tmp_path, max_files=1)


def test_discovery_rejects_missing_and_non_markdown_targets(tmp_path: Path) -> None:
    with pytest.raises(DiscoveryFailure, match="does not exist"):
        discover_markdown(tmp_path / "missing")
    text = tmp_path / "input.txt"
    text.write_text("text", encoding="utf-8")
    with pytest.raises(DiscoveryFailure, match="not Markdown"):
        discover_markdown(text)


def test_discovery_rejects_empty_target(tmp_path: Path) -> None:
    with pytest.raises(DiscoveryFailure, match="contains no Markdown files"):
        discover_markdown(tmp_path)


def test_discovery_reports_symbolic_link_without_following_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target"
    target.mkdir()

    class FakeSymbolicLink:
        name = "linked-directory"
        path = str(target / name)

        @staticmethod
        def is_symlink() -> bool:
            return True

    monkeypatch.setattr("wem_validator.discovery.os.scandir", lambda _: [FakeSymbolicLink()])
    result = discover_markdown(target)
    assert len(result) == 1
    assert result[0].text is None
    assert result[0].issue == "symbolic link is not followed"
