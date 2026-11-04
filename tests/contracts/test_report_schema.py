from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from wem_validator.engine import validate_target
from wem_validator.schema_resources import load_report_schema, load_report_schema_bytes


def _schema(repository_root: Path) -> dict[str, object]:
    canonical = repository_root / "contracts" / "finding-report" / "0.2.0.schema.json"
    assert load_report_schema_bytes() == canonical.read_bytes()
    return load_report_schema()


def test_report_schema_is_valid_and_accepts_direct_report(repository_root: Path) -> None:
    schema = _schema(repository_root)
    Draft202012Validator.check_schema(schema)
    report = validate_target(
        repository_root / "tests" / "fixtures" / "valid",
        profile_id="wem-1.2.0",
    ).as_json()
    Draft202012Validator(schema).validate(report)


def test_report_schema_accepts_manifest_scope(repository_root: Path) -> None:
    schema = _schema(repository_root)
    report = validate_target(
        repository_root,
        profile_id=None,
        manifest_path=repository_root / "wem-validator.toml",
    ).as_json()
    Draft202012Validator(schema).validate(report)


def test_report_schema_accepts_findings(repository_root: Path) -> None:
    schema = _schema(repository_root)
    report = validate_target(
        repository_root / "tests" / "fixtures" / "invalid",
        profile_id="wem-1.2.0",
    ).as_json()
    assert report["findings"]
    Draft202012Validator(schema).validate(report)
