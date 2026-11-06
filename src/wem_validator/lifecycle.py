"""WEM ADR lifecycle evaluation over normalized history observations."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

from wem_validator.history import GitHistoryResult, HistoryArtifact
from wem_validator.model import Finding, Outcome
from wem_validator.parsing import parse_markdown
from wem_validator.profiles import ValidationProfile

_TABLE_SEPARATOR = re.compile(r"^:?-{3,}:?$")
_ALLOWED_TRANSITIONS = {
    "Proposed": frozenset({"Proposed", "Accepted", "Rejected", "Withdrawn"}),
    "Accepted": frozenset({"Accepted", "Superseded", "Retired"}),
    "Rejected": frozenset({"Rejected"}),
    "Withdrawn": frozenset({"Withdrawn"}),
    "Superseded": frozenset({"Superseded"}),
    "Retired": frozenset({"Retired"}),
}


@dataclass(frozen=True, slots=True)
class StatusEntry:
    date: str
    status: str
    authority: str
    reason: str


@dataclass(frozen=True, slots=True)
class AdrLifecycleRecord:
    revision: str
    path: str
    identifier: str
    title: str
    created_date: str
    wem_reference: str
    status: str
    status_history: tuple[StatusEntry, ...]
    history_parseable: bool


def evaluate_lifecycle_history(
    history: GitHistoryResult,
    *,
    profile: ValidationProfile,
) -> tuple[Finding, ...]:
    if history.failure is not None:
        return (
            _finding(
                profile,
                "WEMV120-HISTORY-001",
                ".",
                f"Requested Git history could not be evaluated: {history.failure}.",
                limitations=history.observation.limitations,
            ),
        )

    findings: list[Finding] = []
    previous: dict[str, AdrLifecycleRecord] = {}
    seen: dict[str, AdrLifecycleRecord] = {}
    removal_reported: set[str] = set()

    for snapshot_index, snapshot in enumerate(history.snapshots):
        records = tuple(_record(artifact) for artifact in snapshot.artifacts)
        grouped: dict[str, list[AdrLifecycleRecord]] = defaultdict(list)
        for record in records:
            if not record.identifier:
                findings.append(
                    _finding(
                        profile,
                        "WEMV120-HISTORY-005",
                        record.path,
                        f"ADR identity is unavailable at revision {_revision(record.revision)}.",
                    )
                )
                continue
            grouped[record.identifier].append(record)

        current: dict[str, AdrLifecycleRecord] = {}
        for identifier, matches in sorted(grouped.items()):
            if len(matches) > 1:
                findings.append(
                    _finding(
                        profile,
                        "WEMV120-HISTORY-005",
                        matches[0].path,
                        (
                            f"ADR identifier {identifier} is associated with multiple artifacts at "
                            f"revision {_revision(snapshot.revision)}."
                        ),
                    )
                )
                continue
            current[identifier] = matches[0]

        if snapshot_index == len(history.snapshots) - 1:
            for record in current.values():
                findings.extend(_validate_current_record(record, profile))

        for identifier, record in sorted(current.items()):
            earlier = previous.get(identifier)
            if earlier is not None:
                if not _is_prefix(earlier.status_history, record.status_history):
                    findings.append(
                        _finding(
                            profile,
                            "WEMV120-HISTORY-003",
                            record.path,
                            (
                                f"Status History for {identifier} changed an earlier row "
                                f"between revisions {_revision(earlier.revision)} and "
                                f"{_revision(record.revision)}."
                            ),
                        )
                    )
                if not _transition_allowed(earlier.status, record.status):
                    findings.append(
                        _finding(
                            profile,
                            "WEMV120-HISTORY-004",
                            record.path,
                            (
                                f"Observed lifecycle transition for {identifier} is not allowed: "
                                f"{earlier.status or '<missing>'} to "
                                f"{record.status or '<missing>'}."
                            ),
                        )
                    )
                if earlier.created_date != record.created_date:
                    findings.append(
                        _finding(
                            profile,
                            "WEMV120-HISTORY-005",
                            record.path,
                            f"Permanent identifier {identifier} changed its Created Date.",
                        )
                    )
                if _reference(earlier.wem_reference) != _reference(record.wem_reference):
                    findings.append(
                        _finding(
                            profile,
                            "WEMV120-HISTORY-005",
                            record.path,
                            f"Permanent identifier {identifier} changed its WEM Reference.",
                        )
                    )
            elif identifier in seen:
                first = seen[identifier]
                findings.append(
                    _finding(
                        profile,
                        "WEMV120-HISTORY-005",
                        record.path,
                        (
                            f"Permanent identifier {identifier} reappeared after removal; "
                            f"artifact was observed at revision {_revision(first.revision)}."
                        ),
                    )
                )
            else:
                seen[identifier] = record

        for identifier, record in sorted(previous.items()):
            if identifier not in current and identifier not in removal_reported:
                findings.append(
                    _finding(
                        profile,
                        "WEMV120-HISTORY-003",
                        record.path,
                        (
                            f"Maintained ADR {identifier} disappeared after revision "
                            f"{_revision(record.revision)}."
                        ),
                    )
                )
                removal_reported.add(identifier)
        previous = current

    return tuple(sorted(findings))


def _validate_current_record(
    record: AdrLifecycleRecord,
    profile: ValidationProfile,
) -> list[Finding]:
    findings: list[Finding] = []
    if not record.history_parseable or not record.status_history:
        findings.append(
            _finding(
                profile,
                "WEMV120-HISTORY-002",
                record.path,
                f"Current ADR {record.identifier} has no parseable Status History rows.",
            )
        )
        return findings
    latest = record.status_history[-1].status
    if record.status != latest:
        findings.append(
            _finding(
                profile,
                "WEMV120-HISTORY-002",
                record.path,
                (
                    f"Current Status for {record.identifier} is {record.status or '<missing>'}, "
                    f"but its latest Status History entry is {latest or '<missing>'}."
                ),
            )
        )
    for left, right in zip(record.status_history, record.status_history[1:], strict=False):
        if not _transition_allowed(left.status, right.status):
            findings.append(
                _finding(
                    profile,
                    "WEMV120-HISTORY-004",
                    record.path,
                    (
                        f"Status History for {record.identifier} contains an invalid transition: "
                        f"{left.status or '<missing>'} to {right.status or '<missing>'}."
                    ),
                )
            )
    return findings


def _record(artifact: HistoryArtifact) -> AdrLifecycleRecord:
    parsed = parse_markdown(artifact.text)
    values = parsed.metadata.values
    rows, parseable = _status_history(artifact.text)
    return AdrLifecycleRecord(
        revision=artifact.revision,
        path=artifact.path,
        identifier=values.get("Identifier", ""),
        title=values.get("Title", ""),
        created_date=values.get("Created Date", ""),
        wem_reference=values.get("WEM Reference", ""),
        status=values.get("Status", ""),
        status_history=rows,
        history_parseable=parseable,
    )


def _status_history(text: str) -> tuple[tuple[StatusEntry, ...], bool]:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == "## Status History":
            start = index + 1
            break
    if start is None:
        return (), False

    entries: list[StatusEntry] = []
    parseable = True
    columns: dict[str, int] | None = None
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|"):
            continue
        cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
        if cells and all(_TABLE_SEPARATOR.fullmatch(cell) for cell in cells):
            continue
        if columns is None:
            columns = _status_columns(cells)
            if columns is None:
                parseable = False
            continue
        if len(cells) != len(columns) or not all(cells):
            parseable = False
            continue
        entries.append(
            StatusEntry(
                date=cells[columns["date"]],
                status=cells[columns["status"]],
                authority=cells[columns["authority"]],
                reason=cells[columns["reason"]],
            )
        )
    return tuple(entries), parseable and columns is not None


def _is_prefix(
    earlier: tuple[StatusEntry, ...],
    later: tuple[StatusEntry, ...],
) -> bool:
    return len(later) >= len(earlier) and later[: len(earlier)] == earlier


def _transition_allowed(earlier: str, later: str) -> bool:
    return later in _ALLOWED_TRANSITIONS.get(earlier, frozenset())


def _status_columns(cells: tuple[str, ...]) -> dict[str, int] | None:
    aliases = {
        "date": "date",
        "status": "status",
        "decision authority": "authority",
        "authority": "authority",
        "reason": "reason",
    }
    columns: dict[str, int] = {}
    for index, cell in enumerate(cells):
        semantic = aliases.get(" ".join(cell.casefold().split()))
        if semantic is None or semantic in columns:
            return None
        columns[semantic] = index
    return columns if set(columns) == {"date", "status", "authority", "reason"} else None


def _reference(value: str) -> str:
    return value.removesuffix(".")


def _revision(value: str) -> str:
    return value if value == "WORKTREE" else value[:12]


def _finding(
    profile: ValidationProfile,
    rule_id: str,
    path: str,
    explanation: str,
    *,
    limitations: tuple[str, ...] = (),
) -> Finding:
    definition = next(item for item in profile.rules if item.identifier == rule_id)
    return Finding.create(
        rule_id=rule_id,
        profile=profile.identifier,
        outcome=Outcome.ERROR,
        path=path,
        explanation=explanation,
        source=definition.source,
        limitations=limitations,
    )
