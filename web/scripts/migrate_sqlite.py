#!/usr/bin/env python3
"""Copy the legacy SQLite database into the Next.js workspace and enforce constraints."""

from __future__ import annotations

import argparse
import sqlite3
import shutil
from pathlib import Path


def deduplicate_events(connection: sqlite3.Connection) -> int:
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM events
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM events
            GROUP BY title, location, datetime, channel, status
        )
        """
    )
    deleted = cursor.rowcount
    connection.commit()
    return deleted


def ensure_indexes(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS events_unique_constraint
        ON events(title, location, datetime, channel, status)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS events_datetime_idx
        ON events(datetime)
        """
    )
    connection.commit()


def normalize_text_fields(connection: sqlite3.Connection) -> None:
    """Replace non-breaking spaces with regular spaces in text fields."""
    cursor = connection.cursor()
    nbsp = "\xa0"
    columns = ("title", "location", "channel", "status")
    for column in columns:
        cursor.execute(
            f"UPDATE events SET {column} = REPLACE({column}, ?, ' ') WHERE instr({column}, ?) > 0",
            (nbsp, nbsp),
        )
    connection.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy backend/data.db into the web workspace (dev.db) and add indexes.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("../backend/data.db"),
        help="Path to the existing SQLite database.",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path("dev.db"),
        help="Destination path for the copied database.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the destination database if it already exists.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.source.exists():
        raise SystemExit(f"Source database not found: {args.source}")

    if args.destination.exists() and not args.force:
        raise SystemExit(
            f"Destination {args.destination} already exists. "
            "Use --force to overwrite or remove it first."
        )

    args.destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.source, args.destination)

    with sqlite3.connect(args.destination) as connection:
        deleted = deduplicate_events(connection)
        normalize_text_fields(connection)
        ensure_indexes(connection)

    print(f"Copied database to {args.destination}.")
    if deleted:
        print(f"Removed {deleted} duplicate rows before creating unique index.")
    else:
        print("No duplicate rows found.")


if __name__ == "__main__":
    main()
