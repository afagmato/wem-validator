"""Load the canonical Draft report Schema from source or an installed wheel."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

_REPORT_SCHEMA = "contracts/finding-report/0.3.0.schema.json"


def load_report_schema_bytes() -> bytes:
    packaged = files("wem_validator").joinpath(_REPORT_SCHEMA)
    try:
        return packaged.read_bytes()
    except FileNotFoundError:
        return (Path(__file__).resolve().parents[2] / _REPORT_SCHEMA).read_bytes()


def load_report_schema() -> dict[str, object]:
    value = json.loads(load_report_schema_bytes())
    if not isinstance(value, dict):
        raise ValueError("the canonical report Schema is not a JSON object")
    return value
