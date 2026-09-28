"""Text normalisation used for grading typed answers.

Grading has to be forgiving about the things that carry no meaning -- case,
accents, punctuation, doubled spaces, joint sizes written as 24/40 or 24-40 --
while staying strict about the actual words. Everything an answer is compared
against (aliases, the display name) goes through the same function, so the
comparison is symmetric.
"""

import re
import unicodedata

# Words that add nothing to an answer's identity. "A Friedrichs condenser"
# and "Friedrichs condenser" are the same answer.
_STOPWORDS = {"a", "an", "the", "with", "and"}

_PUNCT_RE = re.compile(r"[^\w\s/]", flags=re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalize(value: str) -> str:
    """Reduce a name or a typed answer to a comparable key.

    >>> normalize("Condenser, Friedrichs, with 24/40 joint")
    'condenser friedrichs 24 40 joint'
    """
    if not value:
        return ""

    # Strip accents: "Büchner" -> "Buchner", so both spellings match.
    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    text = text.lower()

    # Joint sizes: 24/40, 24-40 and "24 40" should all collapse to the same
    # thing, so turn the separators into spaces before dropping punctuation.
    text = re.sub(r"(\d)\s*[/\-]\s*(\d)", r"\1 \2", text)

    text = _PUNCT_RE.sub(" ", text)
    text = text.replace("/", " ")
    text = _WS_RE.sub(" ", text).strip()

    tokens = [t for t in text.split(" ") if t and t not in _STOPWORDS]
    return " ".join(tokens)


def titleize(catalog_name: str) -> str:
    """Turn a SHOUTED catalog heading into a readable display name.

    'CONDENSER, FRIEDRICHS, WITH 24/40 JOINT' -> 'Condenser, Friedrichs, with 24/40 joint'

    This is a starting point for content entry, not a substitute for it -- the
    seed data carries hand-written display names where the catalog wording is
    not how a chemist would say it.
    """
    lowered = catalog_name.strip().lower()
    if not lowered:
        return ""

    words = []
    for index, word in enumerate(lowered.split(" ")):
        if index > 0 and word.strip(",") in _STOPWORDS:
            words.append(word)
        else:
            words.append(word[:1].upper() + word[1:])

    result = " ".join(words)
    # Keep joint sizes and other numbers untouched, restore the leading capital.
    return result[:1].upper() + result[1:]
