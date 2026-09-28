"""Download the Synthware products from labware-shop.com (a Wix store).

Run on your own computer (Python 3.9+):

    pip install playwright
    python -m playwright install chromium
    python fetch_labware_shop.py

The shop builds its product lists with JavaScript, so the list pages are read
with a hidden Chromium browser; the product pages and photos are then fetched
directly. Takes roughly 15-40 minutes.

It creates labware/ with
    products.json            name, link, SKU, brand, description, image list
    images/<slug>_<n>.jpg    up to MAX_IMAGES photos per product, 1200 px
and packs it into labware_part1.zip, labware_part2.zip, ... (under ~95 MB
each). Attach all the parts to the chat.

Re-running is safe: anything already downloaded is skipped.
"""

import concurrent.futures as cf
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile

SHOP = "https://www.labware-shop.com"
LIST_URL = SHOP + "/shop?Brands=Synthware&page={page}"
MAX_PAGES = 80
MAX_IMAGES = 4
IMAGE_SIZE = 1200
OUT = "labware"
PART_LIMIT = 95 * 1024 * 1024
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ChemQuiz image fetch"}

MEDIA_RE = re.compile(r"(?:static\.wixstatic\.com/media/)?([0-9a-f]{6}_[0-9a-f]{32}~mv2\.(?:jpe?g|png|webp))", re.I)


def get(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == tries - 1:
                raise
            time.sleep(2 + attempt * 3)
            print(f"   retry {url} ({exc})")


# --- 1. the list of Synthware products (needs a real browser) ---------------------------

def list_products():
    from playwright.sync_api import sync_playwright

    found = {}  # slug -> name
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        empty_in_a_row = 0
        for n in range(1, MAX_PAGES + 1):
            page.goto(LIST_URL.format(page=n), wait_until="domcontentloaded", timeout=90000)
            try:
                page.wait_for_selector('a[href*="/product-page/"]', timeout=30000)
            except Exception:
                pass
            # Scroll so the whole grid renders.
            for _ in range(8):
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(400)
            links = page.eval_on_selector_all(
                'a[href*="/product-page/"]',
                "els => els.map(e => [e.href, (e.innerText || e.getAttribute('aria-label') || '').trim()])",
            )
            new = 0
            for href, text in links:
                slug = href.split("/product-page/")[1].split("?")[0].split("#")[0]
                if slug and slug not in found:
                    found[slug] = text.split("\n")[0]
                    new += 1
            print(f"list page {n}: {len(links)} links, {new} new, {len(found)} total")
            empty_in_a_row = empty_in_a_row + 1 if new == 0 else 0
            if empty_in_a_row >= 2:
                break
        browser.close()
    return found


# --- 2. each product page -----------------------------------------------------------------

def meta(page_html, prop):
    m = re.search(r'<meta[^>]+(?:property|name)="%s"[^>]+content="([^"]*)"' % re.escape(prop), page_html)
    return html.unescape(m.group(1)) if m else None


def read_product(slug):
    url = f"{SHOP}/product-page/{slug}"
    raw = get(url).decode("utf-8", "replace")
    media = []
    for m in MEDIA_RE.finditer(raw):
        if m.group(1) not in media:
            media.append(m.group(1))
    sku = re.search(r'"sku"\s*:\s*"([^"]+)"', raw)
    brand = re.search(r'"brand"\s*:\s*(?:\{[^}]*"name"\s*:\s*)?"([^"]+)"', raw)
    return {
        "slug": slug,
        "url": url,
        "name": meta(raw, "og:title"),
        "description": meta(raw, "og:description"),
        "sku": sku.group(1) if sku else None,
        "brand": brand.group(1) if brand else ("Synthware" if "Synthware" in raw else None),
        "media": media,
    }


def download(product):
    files = []
    for n, media_id in enumerate(product["media"][:MAX_IMAGES]):
        name = f"{product['slug'][:80]}_{n}.jpg"
        path = os.path.join(OUT, "images", name)
        if not os.path.exists(path):
            src = f"https://static.wixstatic.com/media/{media_id}/v1/fit/w_{IMAGE_SIZE},h_{IMAGE_SIZE},q_90/file.jpg"
            try:
                data = get(src)
            except Exception as exc:  # noqa: BLE001
                print(f"   could not get {src}: {exc}")
                continue
            with open(path, "wb") as f:
                f.write(data)
        files.append({"file": name, "media": media_id})
    return files


def main():
    os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
    list_path = os.path.join(OUT, "list.json")
    if os.path.exists(list_path):
        found = json.load(open(list_path, encoding="utf-8"))
        print(f"{len(found)} products from the saved list")
    else:
        found = list_products()
        json.dump(found, open(list_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not found:
        print("No products found -- the shop layout may have changed. Send me the output above.")
        return 1

    products = []
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(read_product, slug): slug for slug in found}
        for i, fut in enumerate(cf.as_completed(futures), 1):
            try:
                products.append(fut.result())
            except Exception as exc:  # noqa: BLE001
                print(f"   could not read {futures[fut]}: {exc}")
            if i % 50 == 0:
                print(f"product pages: {i}/{len(found)}")

    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        for product, files in zip(products, pool.map(download, products)):
            product["images"] = files
    print(f"photos: {sum(len(p['images']) for p in products)}")

    with open(os.path.join(OUT, "products.json"), "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=1)

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
            zf = zipfile.ZipFile(f"labware_part{part}.zip", "w", zipfile.ZIP_STORED)
            print(f"writing labware_part{part}.zip")
        zf.write(path)
        size += fsize
    if zf:
        zf.close()
    print(f"Done: {len(products)} products. Attach labware_part1.zip ... labware_part{part}.zip to the chat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
