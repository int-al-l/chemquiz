"""Loading seed_data.py into the database.

Lives here rather than in seed.py so the server can use it too: an empty
database is a broken site, and starting the server used to create one silently.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models
from .config import IMAGES_DIR
from .text import normalize

# seed_data.py sits beside the app package, at the backend root.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def load_seed_module():
    import seed_data  # noqa: PLC0415 - deliberately late, after sys.path is set

    return seed_data


def upsert_category(db: Session, data: dict, parent=None) -> models.Category:
    category = db.execute(
        select(models.Category).where(models.Category.slug == data["slug"])
    ).scalar_one_or_none()

    if category is None:
        category = models.Category(slug=data["slug"])
        db.add(category)

    category.name = data["name"]
    category.description = data.get("description")
    category.image = data.get("image")
    category.sort_order = data.get("sort_order", 0)
    category.parent = parent
    db.flush()

    for child in data.get("children", []):
        upsert_category(db, child, parent=category)

    return category


def upsert_item(db: Session, data: dict, categories_by_slug: dict, source: str):
    category = categories_by_slug.get(data["category"])
    if category is None:
        raise ValueError(
            f"Item '{data['slug']}' names category '{data['category']}', "
            "which is not in CATEGORIES."
        )

    item = db.execute(
        select(models.Item).where(models.Item.slug == data["slug"])
    ).scalar_one_or_none()

    if item is None:
        item = models.Item(slug=data["slug"])
        db.add(item)

    photos = data.get("photos", [])

    item.name = data["name"]
    item.catalog_name = data.get("catalog_name")
    item.description = data.get("description")
    # The card image: an explicit one, else the first photograph.
    item.image = data.get("image") or (photos[0]["file"] if photos else None)
    item.source = source
    item.source_page = data.get("source_page")
    item.sort_order = data.get("sort_order", 0)
    item.category = category
    db.flush()

    # Photos and aliases are rewritten wholesale: the seed file is the source
    # of truth for both.
    item.photos.clear()
    item.aliases.clear()
    db.flush()

    for order, photo in enumerate(photos, start=1):
        db.add(
            models.ItemPhoto(
                item=item,
                filename=photo["file"],
                source_page=photo.get("page"),
                credit=photo.get("credit"),
                sort_order=order,
            )
        )

    seen: set[str] = set()
    for text in data.get("aliases", []):
        key = normalize(text)
        if not key or key in seen:
            continue
        seen.add(key)
        db.add(models.ItemAlias(item=item, text=text, normalized=key))

    db.flush()
    return item


def load_seed(db: Session) -> dict:
    """Upsert every category and item from seed_data.py.

    Returns counts plus any photo files the data references but that are not in
    static/images.
    """
    seed_data = load_seed_module()

    for data in seed_data.CATEGORIES:
        upsert_category(db, data)

    categories_by_slug = {
        category.slug: category
        for category in db.execute(select(models.Category)).scalars()
    }

    missing: list[str] = []
    for data in seed_data.ITEMS:
        item = upsert_item(db, data, categories_by_slug, seed_data.SOURCE)
        for photo in item.photos:
            if not (IMAGES_DIR / photo.filename).exists():
                missing.append(f"{item.slug} -> {photo.filename}")

    # After the upsert, so a category whose cards all moved elsewhere is empty
    # by now and goes too.
    db.expire_all()
    pruned = prune_removed(
        db,
        item_slugs={d["slug"] for d in seed_data.ITEMS},
        category_slugs=_all_category_slugs(seed_data.CATEGORIES),
    )

    db.commit()

    count = lambda model: db.execute(select(func.count(model.id))).scalar_one()  # noqa: E731
    return {
        "categories": count(models.Category),
        "items": count(models.Item),
        "photos": count(models.ItemPhoto),
        "aliases": count(models.ItemAlias),
        "missing": missing,
        "pruned": pruned,
    }


def _all_category_slugs(categories: list[dict]) -> set[str]:
    out: set[str] = set()
    for c in categories:
        out.add(c["slug"])
        out |= _all_category_slugs(c.get("children", []))
    return out


def prune_removed(db: Session, *, item_slugs: set[str], category_slugs: set[str]) -> list[str]:
    """Delete items and categories that are no longer in seed_data.py.

    seed_data.py is the source of truth for content, so a card taken out of it
    must leave the site. Rows that point at a removed item -- saved-list
    entries and quiz sessions that asked about it -- go with it; SQLite does
    not enforce the foreign keys that would otherwise cascade.
    """
    gone = db.execute(
        select(models.Item).where(models.Item.slug.notin_(item_slugs))
    ).scalars().all()
    removed = [item.slug for item in gone]
    if gone:
        ids = [item.id for item in gone]
        db.execute(models.SavedItem.__table__.delete().where(models.SavedItem.item_id.in_(ids)))
        session_ids = db.execute(
            select(models.QuizQuestion.session_id).where(models.QuizQuestion.item_id.in_(ids))
        ).scalars().all()
        for session in db.execute(
            select(models.QuizSession).where(models.QuizSession.id.in_(set(session_ids)))
        ).scalars():
            db.delete(session)
        for item in gone:
            db.delete(item)
        db.flush()

    for category in db.execute(
        select(models.Category).where(models.Category.slug.notin_(category_slugs))
    ).scalars().all():
        if not category.items and not category.children:
            removed.append(f"category:{category.slug}")
            db.delete(category)
    db.flush()
    return removed


def is_empty(db: Session) -> bool:
    return db.execute(select(func.count(models.Item.id))).scalar_one() == 0
