"""Pull product blocks out of the Kemtech 2025 catalog.

Each catalog page is a single column of products: a photograph on the left, and
to its right a bold uppercase heading, a short description, and a table of part
numbers. Headings and photographs therefore pair up by vertical position.

The file is laid out as spreads, so every page's content stream also references
the neighbouring page's images at an off-page x offset; those are discarded by
intersecting each image against the page rectangle.
"""

import json
import pathlib
import re
import sys

import pymupdf

PDF = "/root/.claude/uploads/90b66f5d-8d4e-5a40-8c1a-0e88de52f455/dab90217-KemtechCatalog2025_draft4_compressed_web2.pdf"
FIRST_PAGE = 9          # 0-based index of catalog page 1
PAGE_OFFSET = 8         # pdf index - PAGE_OFFSET == printed page number

HEADING_FONT = "Helvetica-Bold"
HEADING_SIZE = 10.1
BODY_FONTS = {"Helvetica", "ArialMT", "Helvetica-Bold"}

NOT_A_PRODUCT = {
    "KEMTECH", "SYNTHWARE GLASS", "KEMX", "SYNTHWARE",
    "ITEM #", "ACCESSORY:", "ACCESSORIES:", "NOTE:",
}

# Where a product's prose stops and its parts table begins.
#
# Matching on opening words alone is too blunt: real sentences start "Top joint
# is a 24/40 outer..." and "O.D. of disc is 24mm.", and an earlier version of
# this threw both away. A column label is instead recognised by being *short*
# and unpunctuated, which a sentence is not.
TABLE_START = re.compile(r"^(item\s*#|accessor(y|ies)|part\s*number|caps?$)", re.I)
ITEM_CODE = re.compile(r"^[A-Z]{1,3}\d{3,}")
COLUMN_LABEL = re.compile(
    r"^(joint|size|cap|o\.?d\.?|i\.?d\.?|bore|length|height|volume|capacity|"
    r"top|bottom|replacement|part|description|thread|stopcock|diameter|width|"
    r"porosity|number|approx|item|glass|flask|column|tube|plug|model|qty)\b",
    re.I,
)


def starts_the_table(text):
    if TABLE_START.match(text) or ITEM_CODE.match(text):
        return True
    if re.match(r"^[\d(]", text):
        return True
    # A column heading is a label, not a sentence: short, and no full stop.
    return bool(COLUMN_LABEL.match(text)) and len(text) <= 26 and not text.endswith(".")


def heading_spans(blocks):
    out = []
    for block in blocks:
        for line in block.get("lines", []):
            for span in line["spans"]:
                text = " ".join(span["text"].split())
                if not text or len(text) < 4:
                    continue
                if span["font"] != HEADING_FONT:
                    continue
                if round(span["size"], 1) != HEADING_SIZE:
                    continue
                if text.upper() != text or not re.search(r"[A-Z]", text):
                    continue
                if text in NOT_A_PRODUCT:
                    continue
                out.append({"text": text, "y": span["bbox"][1], "x": span["bbox"][0]})
    out.sort(key=lambda s: s["y"])

    # A heading can wrap: either onto the same visual line as two spans, or onto
    # the next line, in which case the first part ends mid-phrase. Join both
    # cases rather than inventing a product called "REMOVABLE HOSE CONNECTIONS".
    merged = []
    for span in out:
        if merged:
            gap = span["y"] - merged[-1]["y"]
            same_line = abs(gap) < 3
            continuation = 3 <= gap < 16 and merged[-1]["text"].rstrip().endswith(",")
            if same_line or continuation:
                merged[-1]["text"] = merged[-1]["text"].rstrip() + " " + span["text"]
                continue
        merged.append(dict(span))

    return [s for s in merged if is_product_name(s["text"])]


# Table headers are set in the same bold face as product names. These are the
# ones that slip through: units, column labels and bare material names.
JUNK_HEADING = re.compile(
    r"^(\(?(ml|mm|cm|l|g|in|oz)\)?|[ioIO]\.?[dD]\.?|ptfe|teflon|nylon|viton|"
    r"glass|size|type|joint|bore|volume|capacity|length|height|width|"
    r"porosity|thread|item\s*#?|part\s*#?|code|model|qty|price|"
    r"top|bottom|left|right|inner|outer|male|female|"
    r"accessor(y|ies):?|replacement|note:?|new!?|page\s*\d+)$",
    re.I,
)


def is_product_name(text):
    stripped = text.strip().strip(":")
    if len(stripped) < 6:
        return False
    if JUNK_HEADING.match(stripped):
        return False
    # A real product name carries letters, not just a measurement.
    letters = sum(1 for c in stripped if c.isalpha())
    if letters < 5:
        return False
    # Fragments left over from a wrapped table header.
    if stripped.count("(") != stripped.count(")"):
        return False
    return True


def product_images(page):
    rect = page.rect
    out = []
    for info in page.get_image_info(xrefs=True):
        x0, y0, x1, y1 = info["bbox"]
        w, h = x1 - x0, y1 - y0

        # Off-page (the neighbouring spread), decorative banners, and the
        # full-bleed background all fail one of these.
        if x1 <= rect.x0 or x0 >= rect.x1:
            continue
        if w < 45 or h < 45:
            continue
        if w > rect.width * 0.6 or h > rect.height * 0.6:
            continue
        # The catalog is a mirrored spread: photographs sit against the outer
        # edge, so they are in the left column on odd pages and the right
        # column on even ones. Either is fine -- what disqualifies an image is
        # sitting in the middle, where the text and tables live.
        centre = (x0 + x1) / 2
        if 0.3 * rect.width < centre < 0.68 * rect.width:
            continue
        if y0 < 60:                     # page header strip
            continue
        out.append({"xref": info["xref"], "bbox": [x0, y0, x1, y1], "y": y0})

    out.sort(key=lambda i: i["y"])

    # The same picture can be painted twice; keep one per position.
    deduped = []
    for image in out:
        if deduped and abs(image["y"] - deduped[-1]["y"]) < 8:
            continue
        deduped.append(image)
    return deduped


def pair_by_position(headings, images):
    """Match headings to photographs down the page.

    Pairing by index breaks on the pages that carry a detail shot or a diagram
    alongside the product photographs -- one extra image shifts every pairing
    below it. Both lists are in vertical order, so the correct assignment is the
    order-preserving one that puts each heading nearest its photograph; that is
    a short dynamic program, and it lets surplus images be skipped.
    """
    n, m = len(headings), len(images)
    if not n or not m:
        return [None] * n

    INF = float("inf")
    # cost[i][j] = best total distance pairing headings[i:] with images[j:]
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    choice = [[None] * (m + 1) for _ in range(n + 1)]
    for j in range(m + 1):
        cost[n][j] = 0.0

    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            # Use images[j] for headings[i].
            take = abs(headings[i]["y"] - images[j]["y"]) + cost[i + 1][j + 1]
            # Skip images[j] and try the next one.
            skip = cost[i][j + 1] + 40.0     # a skipped image is not free
            if take <= skip:
                cost[i][j], choice[i][j] = take, "take"
            else:
                cost[i][j], choice[i][j] = skip, "skip"

    out = [None] * n
    i = j = 0
    while i < n and j < m:
        if choice[i][j] == "take":
            out[i] = images[j]
            i += 1
            j += 1
        else:
            j += 1
    return out


def description_for(blocks, heading, next_heading_y):
    """The prose between a heading and the start of its parts table."""
    lines = []
    for block in blocks:
        for line in block.get("lines", []):
            y = line["bbox"][1]
            if y <= heading["y"] + 2:
                continue
            if next_heading_y is not None and y >= next_heading_y - 2:
                continue
            text = " ".join(
                " ".join(s["text"].split()) for s in line["spans"]
            ).strip()
            if not text:
                continue
            lines.append((y, line["bbox"][0], text))

    lines.sort()

    heading_words = heading["text"].upper()

    prose = []
    for _, _, text in lines:
        if text.upper() == text and len(text) > 6 and re.search(r"[A-Z]{4}", text):
            # A heading that wrapped onto a second line is part of *this*
            # product, not the start of the next one -- stepping over it is what
            # lets the prose underneath be found.
            if text.upper() in heading_words:
                continue
            break                      # ran into the next heading
        if starts_the_table(text):
            break                      # ran into the table
        prose.append(text)

    joined = " ".join(prose).strip()
    joined = re.sub(r"\s+", " ", joined)
    return joined


def main():
    doc = pymupdf.open(PDF)
    products = []
    mismatches = []

    for index in range(FIRST_PAGE, doc.page_count):
        page = doc[index]
        printed = index - PAGE_OFFSET

        blocks = page.get_text("dict")["blocks"]
        headings = heading_spans(blocks)
        images = product_images(page)
        if not headings:
            continue

        if len(headings) != len(images):
            mismatches.append(
                {"page": printed, "headings": len(headings), "images": len(images),
                 "names": [h["text"] for h in headings]}
            )

        pairing = pair_by_position(headings, images)

        for position, heading in enumerate(headings):
            nxt = headings[position + 1]["y"] if position + 1 < len(headings) else None
            image = pairing[position]
            description = description_for(blocks, heading, nxt)
            products.append(
                {
                    "page": printed,
                    "pdf_index": index,
                    "name": heading["text"],
                    "description": description,
                    "xref": image["xref"] if image else None,
                    "bbox": image["bbox"] if image else None,
                }
            )

    out = pathlib.Path(__file__).parent / "products.json"
    out.write_text(json.dumps(products, indent=1, ensure_ascii=False))

    with_image = sum(1 for p in products if p["xref"])
    with_desc = sum(1 for p in products if len(p["description"]) > 15)

    print(f"products      : {len(products)}")
    print(f"  with photo  : {with_image}")
    print(f"  with prose  : {with_desc}")
    print(f"pages where heading count != image count: {len(mismatches)}")
    for m in mismatches[:15]:
        print(f"  p{m['page']:>3}  {m['headings']} headings / {m['images']} images  {m['names'][:2]}")
    if len(mismatches) > 15:
        print(f"  ... and {len(mismatches) - 15} more")


if __name__ == "__main__":
    sys.exit(main())
