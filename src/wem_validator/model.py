"""Provider-independent validation domain values."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from typing import TypedDict


class Outcome(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    UNSUPPORTED = "unsupported"


class FindingJson(TypedDict):
    ruleId: str
    profile: str
    outcome: str
    path: str
    line: int | None
    explanation: str
    source: str
    limitations: list[str]


@dataclass(frozen=True, slots=True, order=True)
class Finding:
    path: str
    line_sort: int
    rule_id: str
    profile: str
    outcome: Outcome
    line: int | None
    explanation: str
    source: str
    limitations: tuple[str, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        rule_id: str,
        profile: str,
        outcome: Outcome,
        path: str,
        explanation: str,
        source: str,
        line: int | None = None,
        limitations: tuple[str, ...] = (),
    ) -> Finding:
        return cls(
            path=path,
            line_sort=line if line is not None else 0,
            rule_id=rule_id,
            profile=profile,
            outcome=outcome,
            line=line,
            explanation=explanation,
            source=source,
            limitations=limitations,
        )

    def as_json(self) -> FindingJson:
        return {
            "ruleId": self.rule_id,
            "profile": self.profile,
            "outcome": self.outcome.value,
            "path": self.path,
            "line": self.line,
            "explanation": self.explanation,
            "source": self.source,
            "limitations": list(self.limitations),
        }


class SummaryJson(TypedDict):
    total: int
    error: int
    warning: int
    unsupported: int


class ScopeJson(TypedDict):
    mode: str
    manifest: str | None
    includePatterns: list[str]
    excludePatterns: list[str]
    excludedPathCounts: dict[str, int]


class ReportJson(TypedDict):
    formatVersion: str
    profile: str
    wemReference: str
    target: str
    scope: ScopeJson
    findings: list[FindingJson]
    limitations: list[str]
    summary: SummaryJson


@dataclass(frozen=True, slots=True)
class ValidationScope:
    mode: str = "direct"
    manifest: str | None = None
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    excluded_path_counts: tuple[tuple[str, int], ...] = ()

    def as_json(self) -> ScopeJson:
        return {
            "mode": self.mode,
            "manifest": self.manifest,
            "includePatterns": list(self.include_patterns),
            "excludePatterns": list(self.exclude_patterns),
            "excludedPathCounts": dict(self.excluded_path_counts),
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    profile: str
    wem_reference: str
    target: str
    scope: ValidationScope
    findings: tuple[Finding, ...]
    limitations: tuple[str, ...]

    @property
    def failed(self) -> bool:
        return any(item.outcome is Outcome.ERROR for item in self.findings)

    def as_json(self) -> ReportJson:
        counts = Counter(item.outcome.value for item in self.findings)
        return {
            "formatVersion": "0.2.0",
            "profile": self.profile,
            "wemReference": self.wem_reference,
            "target": self.target,
            "scope": self.scope.as_json(),
            "findings": [item.as_json() for item in self.findings],
            "limitations": list(self.limitations),
            "summary": {
                "total": len(self.findings),
                "error": counts[Outcome.ERROR.value],
                "warning": counts[Outcome.WARNING.value],
                "unsupported": counts[Outcome.UNSUPPORTED.value],
            },
        }
