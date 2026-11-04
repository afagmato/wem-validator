"""Equivalent deterministic text and JSON projections."""

from __future__ import annotations

import json

from wem_validator.model import ValidationReport


def render_json(report: ValidationReport) -> str:
    return json.dumps(report.as_json(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_text(report: ValidationReport) -> str:
    lines = [
        f"Profile: {report.profile}",
        f"WEM Reference: {report.wem_reference}",
        f"Target: {report.target}",
        "",
    ]
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
