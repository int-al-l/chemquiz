"""Russian texts for the cards and decks, keyed by slug.

Hand-edited (never generated): seed.py and the server's first start load it
next to seed_data.py. A card or deck missing here shows its English text.

ITEMS[slug]      = {"name": ..., "description": ..., "aliases": [...]}
CATEGORIES[slug] = {"name": ..., "description": ...}
"""

ITEMS: dict[str, dict] = {}

CATEGORIES: dict[str, dict] = {}
