"""Merging learning-progress documents.

The browser computes progress (it must work for guests too); the server keeps
one copy per account. Two devices -- or a guest session being adopted on sign
in -- can each hold changes the other has not seen, so documents are merged
rather than overwritten:

  days    XP earned per local date; per date the larger value wins, and total
          XP is the sum over dates, so XP earned on different days on
          different devices adds up.
  cards   per card, the record studied most recently (`last`) wins.
  badges  union, keeping the earliest unlock time.
  goal    the value from the more recently updated document.

The same rules are implemented in src/progress/merge.js.
"""

from __future__ import annotations

from typing import Any

EMPTY: dict[str, Any] = {"v": 1, "days": {}, "cards": {}, "badges": {}, "goal": 50,
                         "stats": {}, "updated": 0}


def _num(value: Any, default: float = 0) -> float:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


def normalise(doc: Any) -> dict:
    if not isinstance(doc, dict):
        doc = {}
    out = {**EMPTY, **{k: v for k, v in doc.items() if k in EMPTY}}
    for key in ("days", "cards", "badges", "stats"):
        if not isinstance(out[key], dict):
            out[key] = {}
    out["days"] = {k: _num(v) for k, v in out["days"].items() if isinstance(k, str)}
    out["cards"] = {k: v for k, v in out["cards"].items() if isinstance(v, dict)}
    out["badges"] = {k: _num(v) for k, v in out["badges"].items()}
    out["stats"] = {k: _num(v) for k, v in out["stats"].items()}
    out["goal"] = _num(out["goal"], 50) or 50
    out["updated"] = _num(out["updated"])
    return out


def merge(a: Any, b: Any) -> dict:
    a, b = normalise(a), normalise(b)
    days = dict(a["days"])
    for k, v in b["days"].items():
        days[k] = max(days.get(k, 0), v)

    cards = dict(a["cards"])
    for slug, card in b["cards"].items():
        mine = cards.get(slug)
        if mine is None or _num(card.get("last")) > _num(mine.get("last")):
            cards[slug] = card

    badges = dict(a["badges"])
    for k, v in b["badges"].items():
        badges[k] = min(badges[k], v) if k in badges else v

    stats = dict(a["stats"])
    for k, v in b["stats"].items():
        stats[k] = max(stats.get(k, 0), v)

    newer = a if a["updated"] >= b["updated"] else b
    return {
        "v": 1,
        "days": days,
        "cards": cards,
        "badges": badges,
        "goal": newer["goal"],
        "stats": stats,
        "updated": max(a["updated"], b["updated"]),
    }
