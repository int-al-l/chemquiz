"""Read-only content endpoints: the category tree and the items in it."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..i18n import AppError, request_lang

router = APIRouter(prefix="/api", tags=["content"])


@router.get("/categories", response_model=list[schemas.CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    parent: str | None = Query(
        default=None,
        description="Slug of a parent category. Omit for top-level categories.",
    ),
):
    if parent is None:
        categories = crud.list_root_categories(db)
    else:
        parent_category = crud.get_category_by_slug(db, parent)
        if parent_category is None:
            raise AppError("no_category", status=404, slug=parent)
        categories = parent_category.children

    return [crud.category_payload(db, c) for c in categories]


@router.get("/categories/{slug}", response_model=schemas.CategoryDetailOut)
def get_category(slug: str, db: Session = Depends(get_db)):
    category = crud.get_category_by_slug(db, slug)
    if category is None:
        raise AppError("no_category", status=404, slug=slug)

    payload = crud.category_payload(db, category)
    payload["parent"] = (
        crud.category_payload(db, category.parent) if category.parent else None
    )
    payload["children"] = [crud.category_payload(db, c) for c in category.children]
    payload["items"] = [crud.item_payload(i) for i in category.items]
    return payload


@router.get("/items", response_model=list[schemas.ItemOut])
def list_items(
    db: Session = Depends(get_db),
    category: str | None = Query(default=None, description="Category slug to filter by."),
    include_descendants: bool = Query(
        default=True, description="Include items in child categories."
    ),
):
    category_id = None
    if category is not None:
        found = crud.get_category_by_slug(db, category)
        if found is None:
            raise AppError("no_category", status=404, slug=category)
        category_id = found.id

    items = crud.list_items(db, category_id, include_descendants=include_descendants)
    return [crud.item_payload(i) for i in items]


@router.get("/items/{slug}", response_model=schemas.ItemOut)
def get_item(slug: str, db: Session = Depends(get_db)):
    from sqlalchemy import select

    from .. import models

    item = db.execute(
        select(models.Item).where(models.Item.slug == slug)
    ).scalar_one_or_none()
    if item is None:
        raise AppError("no_item", status=404, slug=slug)
    return crud.item_payload(item)
