"""Download the SYNTHWARE catalogue from chengduglassware.com.

Run on your own computer (Python 3.8+, no extra packages needed):

    python fetch_synthware.py

It creates a folder `synthware/` containing
    products.json          every product: name, link, description, image list
    images/<id>_<n>.jpg    up to MAX_IMAGES full-size photos per product
and then packs that folder into synthware_part1.zip, synthware_part2.zip, ...
(each under ~95 MB so they can be attached to a chat). Attach all the parts.

Re-running is safe: images already downloaded are skipped.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile

BASE = "https://chengduglassware.com/wp-json/wc/store/v1/products"
CATEGORY_ID = 32          # "SYNTHWARE"
PER_PAGE = 100
MAX_IMAGES = 4            # photos kept per product (the first ones are the best)
OUT = "synthware"
PART_LIMIT = 95 * 1024 * 1024
HEADERS = {"User-Agent": "Mozilla/5.0 (ChemQuiz image fetch)"}


def get(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read(), resp.headers
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == tries - 1:
                raise
            print(f"   retry ({exc}) ...")
            time.sleep(2 + attempt * 3)


def fetch_products():
    products, page = [], 1
    while True:
        url = f"{BASE}?category={CATEGORY_ID}&per_page={PER_PAGE}&page={page}"
        body, headers = get(url)
        batch = json.loads(body)
        if not batch:
            break
        products.extend(batch)
        total_pages = int(headers.get("X-WP-TotalPages", page))
        print(f"page {page}/{total_pages}: {len(batch)} products")
        if page >= total_pages:
            break
        page += 1
    return products


def main():
    os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
    products = fetch_products()
    print(f"{len(products)} products")

    slim = []
    for i, p in enumerate(products, 1):
        imgs = []
        for n, im in enumerate(p.get("images", [])[:MAX_IMAGES]):
            src = im.get("src")
            if not src:
                continue
            ext = os.path.splitext(src.split("?")[0])[1].lower() or ".jpg"
            name = f"{p['id']}_{n}{ext}"
            path = os.path.join(OUT, "images", name)
            if not os.path.exists(path):
                try:
                    data, _ = get(src)
                    with open(path, "wb") as f:
                        f.write(data)
                except Exception as exc:  # noqa: BLE001
                    print(f"   could not get {src}: {exc}")
                    continue
            imgs.append({"file": name, "src": src})
        slim.append({
            "id": p["id"],
            "name": p.get("name"),
            "permalink": p.get("permalink"),
            "sku": p.get("sku"),
            "description": p.get("description"),
            "short_description": p.get("short_description"),
            "images_total": len(p.get("images", [])),
            "images": imgs,
        })
        if i % 25 == 0:
            print(f"images: {i}/{len(products)} products done")

    with open(os.path.join(OUT, "products.json"), "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, indent=1)

    # Pack into parts small enough to attach.
    files = [os.path.join(OUT, "products.json")] + sorted(
        os.path.join(OUT, "images", n) for n in os.listdir(os.path.join(OUT, "images"))
    )
    part, size, zf = 0, 0, None
    for path in files:
        fsize = os.path.getsize(path)
        if zf is None or size + fsize > PART_LIMIT:
            if zf:
                zf.close()
            part += 1
            size = 0
            zf = zipfile.ZipFile(f"synthware_part{part}.zip", "w", zipfile.ZIP_STORED)
            print(f"writing synthware_part{part}.zip")
        zf.write(path)
        size += fsize
    if zf:
        zf.close()
    print(f"Done. Attach synthware_part1.zip ... synthware_part{part}.zip to the chat.")


if __name__ == "__main__":
    sys.exit(main())
