"""Equivalent deterministic text and JSON projections."""

from __future__ import annotations

import json

from wem_validator.model import ValidationReport


def render_json(report: ValidationReport) -> str:
    return json.dumps(report.as_json(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_text(report: ValidationReport) -> str:
    lines = [
        f"Profile: {report.profile}",
        f"Profile version: {report.profile_version}",
        f"WEM Reference: {report.wem_reference}",
        f"Target: {report.target}",
        f"History: {report.history.mode} ({report.history.availability})",
        "",
    ]
    if report.history.current_revision is not None:
        lines.insert(5, f"Current revision: {report.history.current_revision}")
        lines.insert(6, f"History boundary: {report.history.boundary}")
        lines.insert(
            7,
            (
                f"History observations: {report.history.commit_count} commit(s), "
                f"{report.history.artifact_count} artifact(s)"
            ),
        )
    if report.findings:
        for finding in report.findings:
            location = finding.path
            if finding.line is not None:
                location = f"{location}:{finding.line}"
            lines.append(
                f"{finding.outcome.value.upper()} {finding.rule_id} {location} — "
                f"{finding.explanation} [{finding.source}]"
            )
            for limitation in finding.limitations:
                lines.append(f"  Limitation: {limitation}")
    else:
        lines.append("No findings.")
    lines.extend(("", "Profile limitations:"))
    lines.extend(f"- {item}" for item in report.limitations)
    payload = report.as_json()["summary"]
    lines.extend(
        (
            "",
            (
                f"Summary: {payload['total']} finding(s); {payload['error']} error, "
                f"{payload['warning']} warning, {payload['unsupported']} unsupported."
            ),
        )
    )
    return "\n".join(lines) + "\n"
