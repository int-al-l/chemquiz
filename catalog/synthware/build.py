"""Turn the downloaded Synthware catalogue into the site's content.

    python tools/fetch_synthware.py            # on a machine that can reach the site
    python catalog/synthware/build.py <folder> # <folder> holds products.json and images/

What it does:

1. For every photo chosen in curate.py: crops it to the piece of glassware
   (plus a margin), scales it to at most 900 px, and saves it as
   backend/static/images/<card>-<n>.jpg. Photos no card uses any more are
   deleted from that folder.
2. Rewrites backend/seed_data.py: dropped cards are left out, every card's
   photo list is replaced, new cards are added, and each card records the
   Synthware product(s) its photos came from.

Then, from backend/:  python seed.py   (it also removes the dropped cards
from an existing database).

`--sheets` additionally writes review contact sheets of the chosen photos.

Photos from Wikimedia Commons (stems starting with "wm:", listed in
curate.COMMONS with their credit) are read from <folder>/commons/, named as
curate.commons_filename() says. A photo whose source is not in <folder> but
which an earlier build already made is kept as it is, so new cards can be
added without downloading the whole catalogue again.
"""

from __future__ import annotations

import argparse
import json
import pprint
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BACKEND = ROOT / "backend"
IMAGES = BACKEND / "static" / "images"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BACKEND))

from curate import COMMONS, DROPPED, NEW_CATEGORIES, NEW_OR_CHANGED, PHOTOS, commons_filename  # noqa: E402

MAX_SIDE = 900
MARGIN = 0.06  # of the longer side of the cropped piece


def load(path: Path) -> Image.Image:
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    return im.convert("RGB")


def crop_to_piece(im: Image.Image) -> Image.Image:
    """Crop away the empty background around the glassware.

    The background colour is taken from the image border; anything clearly
    different from it is the piece (or the surface it stands on, which is
    kept). Glass is faint, so the threshold is low and specks are ignored by
    requiring a few pixels per row and column.
    """
    a = np.asarray(im, dtype=np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3),
                             a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    diff = np.abs(a - bg).max(axis=2) > 28
    rows = np.where(diff.sum(axis=1) > max(2, w // 300))[0]
    cols = np.where(diff.sum(axis=0) > max(2, h // 300))[0]
    if len(rows) == 0 or len(cols) == 0:
        return im
    top, bottom, left, right = rows[0], rows[-1], cols[0], cols[-1]
    pad = int(MARGIN * max(bottom - top, right - left))
    box = (max(0, left - pad), max(0, top - pad), min(w, right + pad + 1), min(h, bottom + pad + 1))
    # Nothing to gain from trimming a sliver; keep the original framing then.
    if (box[2] - box[0]) * (box[3] - box[1]) > 0.92 * w * h:
        return im
    return im.crop(box)


def process(src: Path, dest: Path) -> None:
    im = crop_to_piece(load(src))
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    im.save(dest, "JPEG", quality=88, optimize=True, progressive=True)


def find(folder: Path, stem: str) -> Path | None:
    if stem.startswith("wm:"):
        p = folder / "commons" / commons_filename(stem[3:])
        return p if p.exists() else None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = folder / "images" / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def product_id(stem: str) -> int | None:
    return None if stem.startswith("wm:") else int(stem.split("_")[0])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path, help="folder with products.json and images/")
    ap.add_argument("--sheets", type=Path, help="also write review contact sheets here")
    args = ap.parse_args()

    products_file = args.folder / "products.json"
    products = {p["id"]: p for p in json.loads(products_file.read_text("utf-8"))} if products_file.exists() else {}

    import seed_data  # noqa: PLC0415

    old_items = {i["slug"]: i for i in seed_data.ITEMS}
    IMAGES.mkdir(parents=True, exist_ok=True)

    # What each existing image file was made from, so it can be kept when its
    # source is not in the download folder this time.
    made_from = {p["file"]: p.get("source") for i in seed_data.ITEMS for p in i["photos"]}
    old_urls = {sp["id"]: sp["url"] for i in seed_data.ITEMS for sp in i.get("source_products", []) if "id" in sp}

    written: set[str] = set()
    items = []
    order = [s for s in old_items if s not in DROPPED] + [s for s in PHOTOS if s not in old_items]
    for slug in order:
        stems = PHOTOS.get(slug)
        if not stems:
            print(f"  no photos chosen for {slug}; leaving it out")
            continue
        base = dict(old_items.get(slug, {}))
        change = NEW_OR_CHANGED.get(slug, {})
        if not base and not change:
            raise SystemExit(f"{slug} is new but has no entry in NEW_OR_CHANGED")
        ids = list(dict.fromkeys(i for i in map(product_id, stems) if i is not None))
        first = products.get(ids[0], {}).get("name") if ids else None
        sources = [{"id": i, "url": products[i]["permalink"] if i in products else old_urls[i]} for i in ids]
        sources += [{"url": COMMONS[s[3:]]["url"]} for s in stems if s.startswith("wm:")]
        item = {
            "slug": slug,
            "category": change.get("category", base.get("category")),
            "name": change.get("name", base.get("name")),
            "catalog_name": change.get("catalog_name", base.get("catalog_name") or first),
            "description": change.get("description", base.get("description")),
            "aliases": change.get("aliases", base.get("aliases", [])),
            "source_products": sources,
            "photos": [],
        }
        for n, stem in enumerate(stems, start=1):
            name = f"{slug}-{n}.jpg"
            src = find(args.folder, stem)
            if src is not None:
                process(src, IMAGES / name)
            elif not ((IMAGES / name).exists() and made_from.get(name) == stem):
                raise SystemExit(f"{slug}: photo {stem} is not in {args.folder} and was not built before")
            written.add(name)
            photo = {"file": name, "source": stem}
            if stem.startswith("wm:"):
                photo["credit"] = COMMONS[stem[3:]]["credit"]
            item["photos"].append(photo)
        items.append(item)
        print(f"  {slug}: {len(stems)} photo(s)")

    categories = [dict(c) for c in seed_data.CATEGORIES]
    covers = {i["category"]: i["photos"][0]["file"] for i in items}
    for root in categories:
        root["children"] = [dict(c) for c in root.get("children", [])]
    have = {c["slug"] for root in categories for c in root["children"]}
    categories[0]["children"] += [dict(c) for c in NEW_CATEGORIES if c["slug"] not in have]
    new_covers = {c["slug"]: c["image"] for c in NEW_CATEGORIES if c.get("image")}
    for child in categories[0]["children"]:
        if child["slug"] in new_covers:
            child["image"] = new_covers[child["slug"]]
    for root in categories:
        for child in root["children"]:
            if child.get("image") not in written:
                child["image"] = covers.get(child["slug"])
            if child["slug"] == "flasks":
                child["name"] = "Flasks & vessels"
                child["description"] = "Flasks, beakers, bottles and cylinders: the vessels things happen in."

    # A deck with no cards left is not worth a tile.
    used = {i["category"] for i in items}
    for root in categories:
        root["children"] = [c for c in root["children"] if c["slug"] in used]
        for child in root["children"]:
            if child["slug"] == "funnels":
                child["name"] = "Funnels & filtration"
                child["description"] = "Pour, filter, separate and add liquids."

    removed = 0
    for f in IMAGES.iterdir():
        if f.is_file() and f.name not in written:
            f.unlink()
            removed += 1

    header = '''"""Content for the ChemQuiz database.

Generated by catalog/synthware/build.py from the SYNTHWARE catalogue at
chengduglassware.com (downloaded with tools/fetch_synthware.py), plus openly
licensed photographs from Wikimedia Commons for equipment Synthware does not
photograph cleanly; each of those carries its `credit`. The choice of
photographs is in catalog/synthware/curate.py; names and descriptions are
written for the site, for someone meeting the glassware for the first time.

One entry here is one card in Explore. `photos` holds every picture of that
piece, and a quiz question shows one of them; the options offered are
different pieces that cannot be confused with one another, so a question
always has exactly one right answer.

Edit by hand if you like -- seed.py upserts by slug and removes cards that
are no longer listed. Re-running build.py overwrites this file.
"""

'''
    body = (
        f"SOURCE = {'SYNTHWARE catalogue, chengduglassware.com; Wikimedia Commons'!r}\n\n"
        f"CATEGORIES = {pprint.pformat(categories, width=100, sort_dicts=False)}\n\n"
        f"ITEMS = {pprint.pformat(items, width=100, sort_dicts=False)}\n\n"
        f"# Cards taken out because the catalogue has no clean photograph of them.\n"
        f"DROPPED = {pprint.pformat(DROPPED, width=100, sort_dicts=False)}\n"
    )
    (BACKEND / "seed_data.py").write_text(header + body, "utf-8")

    print(f"{len(items)} cards, {len(written)} photos written, {removed} old files removed.")
    if DROPPED:
        print("Dropped:", ", ".join(DROPPED))

    if args.sheets:
        from PIL import ImageDraw  # noqa: PLC0415
        args.sheets.mkdir(parents=True, exist_ok=True)
        T, cols = 170, 8
        per_page = 6
        for page in range(0, len(items), per_page):
            chunk = items[page:page + per_page]
            rows = sum((len(i["photos"]) + cols - 1) // cols for i in chunk)
            sheet = Image.new("RGB", (cols * (T + 6), rows * (T + 6) + 22 * len(chunk)), "#eee")
            draw = ImageDraw.Draw(sheet)
            y = 0
            for i in chunk:
                draw.text((4, y + 4), f"{i['name']}  ({i['category']})", fill="black")
                y += 22
                for k, p in enumerate(i["photos"]):
                    im = Image.open(IMAGES / p["file"]).convert("RGB")
                    im.thumbnail((T, T))
                    x = (k % cols) * (T + 6)
                    if k and k % cols == 0:
                        y += T + 6
                    sheet.paste(im, (x + (T - im.width) // 2, y + (T - im.height) // 2))
                y += T + 6
            sheet.save(args.sheets / f"final-{page // per_page:02d}.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
