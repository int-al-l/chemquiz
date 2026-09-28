"""content_ru.py has a Russian name and description for every card and deck."""

import re

import content_ru
import seed_data


def all_categories(categories):
    for c in categories:
        yield c
        yield from all_categories(c.get("children", []))


CYRILLIC = re.compile("[а-яё]", re.IGNORECASE)


def test_every_card_is_translated():
    missing = [i["slug"] for i in seed_data.ITEMS if i["slug"] not in content_ru.ITEMS]
    assert missing == []
    for slug, texts in content_ru.ITEMS.items():
        assert CYRILLIC.search(texts["name"]), slug
        assert CYRILLIC.search(texts["description"]), slug
        assert isinstance(texts.get("aliases", []), list), slug


def test_every_deck_is_translated():
    slugs = [c["slug"] for c in all_categories(seed_data.CATEGORIES)]
    assert [s for s in slugs if s not in content_ru.CATEGORIES] == []
    for slug, texts in content_ru.CATEGORIES.items():
        assert CYRILLIC.search(texts["name"]), slug


def test_no_translation_for_a_card_that_does_not_exist():
    known = {i["slug"] for i in seed_data.ITEMS} | {c["slug"] for c in all_categories(seed_data.CATEGORIES)}
    assert [s for s in list(content_ru.ITEMS) + list(content_ru.CATEGORIES) if s not in known] == []


def test_russian_names_tell_cards_apart():
    """A quiz offers four names; two cards with one Russian name would give two right answers."""
    names = [t["name"].casefold() for t in content_ru.ITEMS.values()]
    assert len(names) == len(set(names))
