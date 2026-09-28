"""Write src/demo/data.json from backend/seed_data.py, for the demo build.

    python tools/make_demo_data.py && npm run build:demo
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
import seed_data  # noqa: E402


def img(name):
    return f"static/images/{name}" if name else None


categories, parents = [], {}
for i, root in enumerate(seed_data.CATEGORIES):
    categories.append({"slug": root["slug"], "name": root["name"], "description": root.get("description"),
                       "image": img(root.get("image")), "parent": None, "order": root.get("sort_order", i)})
    for j, child in enumerate(root.get("children", [])):
        categories.append({"slug": child["slug"], "name": child["name"], "description": child.get("description"),
                           "image": img(child.get("image")), "parent": root["slug"], "order": child.get("sort_order", j)})

items = []
for n, it in enumerate(seed_data.ITEMS, start=1):
    items.append({
        "id": n, "slug": it["slug"], "name": it["name"], "catalog_name": it.get("catalog_name"),
        "description": it.get("description"), "category": it["category"],
        "photos": [img(p["file"]) for p in it["photos"]],
    })

out = ROOT / "src" / "demo" / "data.json"
out.write_text(json.dumps({"categories": categories, "items": items}, ensure_ascii=False), "utf-8")
print(f"{len(categories)} categories, {len(items)} items -> {out}")
