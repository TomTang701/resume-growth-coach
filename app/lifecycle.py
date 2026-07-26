"""Small, dependency-free guards shared by the local server lifecycle scripts."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


COMMAND_MARKER = "uvicorn app.main:app"


def lifecycle_record_is_valid(
    payload: Mapping[str, Any], *, checkout: Path, observed_command: str
) -> bool:
    """Return whether persisted metadata still identifies this checkout's server."""

    try:
        pid = int(payload["pid"])
        recorded_checkout = Path(str(payload["checkout"])).resolve(strict=False)
        expected_checkout = checkout.resolve(strict=False)
        command_marker = str(payload["command_marker"])
    except (KeyError, TypeError, ValueError):
        return False

    return (
        pid > 0
        and recorded_checkout == expected_checkout
        and command_marker == COMMAND_MARKER
        and command_marker in observed_command
    )


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate local server lifecycle metadata.")
    parser.add_argument("--record-path", required=True, type=Path)
    parser.add_argument("--checkout", required=True, type=Path)
    observed_command = parser.add_mutually_exclusive_group(required=True)
    observed_command.add_argument("--observed-command")
    observed_command.add_argument("--observed-command-base64")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        payload = json.loads(args.record_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return 1

    try:
        observed_command = (
            args.observed_command
            if args.observed_command is not None
            else base64.b64decode(args.observed_command_base64, validate=True).decode("utf-8")
        )
    except (ValueError, UnicodeDecodeError):
        return 1

    return int(
        not lifecycle_record_is_valid(
            payload,
            checkout=args.checkout,
            observed_command=observed_command,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
