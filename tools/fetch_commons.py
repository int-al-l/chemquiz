"""Download the Wikimedia Commons photos that curate.py uses.

Run on your own computer (Python 3.9+, nothing to install):

    python tools/fetch_commons.py <folder>

Every file named in catalog/synthware/curate.COMMONS that is not yet in
<folder>/commons/ is downloaded there, under the name build.py looks for
(curate.commons_filename). Photos wider than 2000 px are fetched as a
2000 px rendition, which is still twice what the site shows. Re-running is
safe: files already there are skipped.

Then build as usual:

    python catalog/synthware/build.py <folder>
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "catalog" / "synthware"))

from curate import COMMONS, commons_filename  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
WIDTH = 2000
HEADERS = {"User-Agent": "ChemQuiz photo fetch (https://github.com/int-al-l/chemquiz)"}


def get(url: str) -> bytes:
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=90) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001
            if attempt == 3:
                raise
            print(f"    retry ({exc})")
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def image_urls(titles: list[str]) -> dict[str, str]:
    """File title -> URL of the original, or of a WIDTH px rendition if larger."""
    out = {}
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "prop": "imageinfo",
            "iiprop": "url|size", "iiurlwidth": WIDTH,
            "titles": "|".join("File:" + t for t in chunk),
        })
        data = json.loads(get(f"{API}?{query}"))
        normalized = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
        for page in data["query"]["pages"].values():
            if "imageinfo" not in page:
                print(f"  ! not on Commons: {page['title']}")
                continue
            info = page["imageinfo"][0]
            title = normalized.get(page["title"], page["title"])[5:]
            big = info.get("width", 0) > WIDTH and info.get("thumburl")
            out[title] = info["thumburl"] if big else info["url"]
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    dest = Path(sys.argv[1]) / "commons"
    dest.mkdir(parents=True, exist_ok=True)
    wanted = [t for t in COMMONS if not (dest / commons_filename(t)).exists()]
    print(f"{len(COMMONS)} Commons photos in curate.py, {len(wanted)} to download into {dest}")
    urls = image_urls(wanted)
    failed = [t for t in wanted if t not in urls]
    for n, title in enumerate(wanted, start=1):
        if title not in urls:
            continue
        print(f"  [{n}/{len(wanted)}] {title}")
        try:
            (dest / commons_filename(title)).write_bytes(get(urls[title]))
        except Exception as exc:  # noqa: BLE001
            print(f"    ! failed: {exc}")
            failed.append(title)
        time.sleep(0.5)
    if failed:
        print("\nNot downloaded:\n  " + "\n  ".join(failed))
        return 1
    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
