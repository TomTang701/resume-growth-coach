"""Safely inspect or remove old local resume-analysis data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import SessionLocal, init_db
from app.services.retention import delete_documents_older_than


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--older-than-days", type=int, required=True)
    parser.add_argument("--delete", action="store_true", help="Actually delete matching data; default is dry-run.")
    args = parser.parse_args()
    if args.older_than_days < 1:
        parser.error("--older-than-days must be at least 1")

    init_db()
    with SessionLocal() as db:
        result = delete_documents_older_than(db, args.older_than_days, dry_run=not args.delete)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
