"""Validate the local database schema and version marker."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import DATABASE_URL, SCHEMA_VERSION, init_db, validate_schema


def main() -> int:
    init_db()
    validate_schema()
    print(f"Database schema is valid: version={SCHEMA_VERSION}, url={DATABASE_URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
