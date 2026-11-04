"""Command-line adapter for local read-only validation."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from wem_validator.configuration import ManifestFailure
from wem_validator.discovery import DiscoveryFailure
from wem_validator.engine import validate_target
from wem_validator.profiles import profile_inventory
from wem_validator.rendering import render_json, render_text


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wem-validate")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate one local target read-only")
    validate.add_argument("target", type=Path)
    validate.add_argument("--profile")
    validate.add_argument("--config", type=Path)
    validate.add_argument("--format", choices=("text", "json"), default="text")
    profile = commands.add_parser("profile")
    profile_commands = profile.add_subparsers(dest="profile_command", required=True)
    inspect = profile_commands.add_parser("inspect")
    inspect.add_argument("--profile", default="wem-1.2.0")
    inspect.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _emit_failure(code: str, message: str, *, output_format: str) -> None:
    if output_format == "json":
        payload = {
            "formatVersion": "0.2.0",
            "status": "error",
            "error": {"code": code, "message": message},
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=sys.stderr)
    else:
        print(f"ERROR {code} — {message}", file=sys.stderr)


def _configure_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="strict")


def main(argv: Sequence[str] | None = None) -> int:
    _configure_utf8_streams()
    args = _parser().parse_args(argv)
    if args.command == "profile" and args.profile_command == "inspect":
        try:
            inventory = profile_inventory(args.profile)
        except ValueError as error:
            _emit_failure("unsupported_profile", str(error), output_format=args.format)
            return 2
        if args.format == "json":
            print(json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(f"Profile: {inventory['profile']}")
            print(f"WEM Reference: {inventory['wemReference']}")
            print("Rules:")
            rules = inventory["rules"]
            if not isinstance(rules, list):
                raise RuntimeError("profile inventory rules are invalid")
            for rule in rules:
                if not isinstance(rule, dict):
                    raise RuntimeError("profile inventory rule is invalid")
                print(f"- {rule['ruleId']} — {rule['description']} [{rule['source']}]")
            print("Limitations:")
            limitations = inventory["limitations"]
            if not isinstance(limitations, list):
                raise RuntimeError("profile inventory limitations are invalid")
            for limitation in limitations:
                print(f"- {limitation}")
        return 0
    if args.command != "validate":
        _emit_failure("unsupported_command", "The command is not supported.", output_format="text")
        return 2
    try:
        report = validate_target(
            args.target,
            profile_id=args.profile,
            manifest_path=args.config,
        )
    except ManifestFailure as error:
        _emit_failure("invalid_manifest", str(error), output_format=args.format)
        return 2
    except ValueError as error:
        _emit_failure("unsupported_profile", str(error), output_format=args.format)
        return 2
    except DiscoveryFailure as error:
        _emit_failure("input_unavailable", str(error), output_format=args.format)
        return 2
    except OSError:
        _emit_failure(
            "evaluation_failed",
            "The local target could not be evaluated.",
            output_format=args.format,
        )
        return 2
    output = render_json(report) if args.format == "json" else render_text(report)
    sys.stdout.write(output)
    return 1 if report.failed else 0
