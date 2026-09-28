"""Load seed_data.py into the database.

    python seed.py           # upsert: add and update, keep everything else
    python seed.py --reset   # drop every table first, then load

Safe to run repeatedly -- categories and items are matched by slug.

The server also seeds an empty database on startup, so this script is for
*re-loading* after you edit seed_data.py, and for --reset.
"""

from __future__ import annotations

import argparse
import sys

from app import seeding
from app.database import Base, SessionLocal, engine


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset", action="store_true", help="drop all tables before seeding"
    )
    args = parser.parse_args()

    if args.reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        counts = seeding.load_seed(db)

    print(
        f"Seeded {counts['categories']} categories, {counts['items']} items, "
        f"{counts['photos']} photos, {counts['aliases']} aliases."
    )

    if counts.get("pruned"):
        print(f"Removed (no longer in seed_data.py): {', '.join(counts['pruned'])}")

    if counts["missing"]:
        print("\nWARNING - items reference images that are not in static/images:")
        for line in counts["missing"]:
            print(f"  {line}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
