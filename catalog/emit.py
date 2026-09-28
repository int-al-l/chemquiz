"""Turn the curated concepts into backend/seed_data.py and its photographs.

Run from this directory after editing curate.py:

    python emit.py
"""

import json
import pathlib
import re
import shutil

import curate

HERE = pathlib.Path(__file__).parent
APP = HERE.parent / "chemquiz" / "Chemquiz-main" / "backend"
IMAGES = APP / "static" / "images"
# Real-ESRGAN output from photorender.py, not the FSRCNN pass in render.py.
PHOTOS = HERE / "photos_hr"


def literal(value):
    """A Python literal for the generated file (json.dumps writes `null`)."""
    if value is None:
        return "None"
    return json.dumps(value, ensure_ascii=False)


def clean(text):
    """Tidy a piece of prose for the card."""
    if not text:
        return None
    text = re.sub(r"\s+", " ", text).strip()
    # The registered-trademark marks are set as separate runs and come out with
    # a stray space in front.
    text = text.replace(" ®", "®").replace(" ™", "™")
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    # The prose is written in plain ASCII; a card should show a real dash.
    text = text.replace(" -- ", " \u2014 ")
    if text and text[-1] not in ".!?":
        text += "."
    return text[:1].upper() + text[1:] if text else None


def check_accepted_answers(products):
    """Every string the grader accepts must name exactly one concept.

    The grader accepts an item's name, its catalog name and its aliases, all
    normalised. If any of those collided across two concepts, typed mode would
    mark a correct answer wrong for one of them.
    """
    owner, clashes = {}, []
    for concept in curate.CONCEPTS:
        candidates = [concept["name"], products[concept["desc"]]["name"],
                      *concept["aliases"]]
        for text in candidates:
            key = curate.normalise_answer(text)
            if not key:
                continue
            if key in owner and owner[key] != concept["slug"]:
                clashes.append((text, owner[key], concept["slug"]))
            owner[key] = concept["slug"]
    return clashes


def main():
    products = [p for p in json.loads((HERE / "products.json").read_text()) if p.get("photo")]
    curate.all_photo_indices()

    for text, first, second in check_accepted_answers(products):
        raise SystemExit(
            f"'{text}' is accepted for both '{first}' and '{second}' -- typed "
            "mode would mark a correct answer wrong for one of them."
        )

    IMAGES.mkdir(parents=True, exist_ok=True)
    for old in IMAGES.iterdir():
        if old.is_file():
            old.unlink()

    lines = [
        '"""Content for the ChemQuiz database.',
        "",
        "Generated from the Kemtech America 2025 catalog by the scripts in",
        "kem/ -- extract.py pulls product blocks and photographs out of the PDF,",
        "curate.py records which catalog entries are the same piece of glassware,",
        "and emit.py writes this file.",
        "",
        "One entry here is one card in Explore. `photos` holds every picture of",
        "that concept, and a quiz question shows one of them; because the four",
        "options offered are four different concepts, and concepts that cannot be",
        "told apart by eye were merged during curation, a question always has",
        "exactly one right answer.",
        "",
        "Edit by hand if you like -- seed.py upserts by slug, so re-running it",
        "keeps everything else. Re-running emit.py overwrites the file.",
        '"""',
        "",
        'SOURCE = "Kemtech America catalog 2025"',
        "",
        "CATEGORIES = [",
        "    {",
        '        "slug": "labware",',
        '        "name": "Labware",',
        '        "description": "Glassware and equipment found on a synthetic chemistry bench.",',
        '        "sort_order": 10,',
        '        "children": [',
    ]

    for order, (slug, name, description) in enumerate(curate.GROUPS, start=1):
        members = [c for c in curate.CONCEPTS if c["group"] == slug]
        cover = f"{members[0]['slug']}-1.jpg" if members else None
        lines += [
            "            {",
            f'                "slug": "{slug}",',
            f'                "name": "{name}",',
            f'                "description": "{description}",',
            f'                "sort_order": {order * 10},',
            f'                "image": "{cover}",',
            "            },",
        ]

    lines += ["        ],", "    },", "]", "", "", "ITEMS = ["]

    for concept in curate.CONCEPTS:
        primary = products[concept["desc"]]

        # What a card says is written in curate.py, for a reader who has not
        # met the piece before. The catalog's own paragraph is a buyer's
        # description -- wall thickness, joint sizes, part numbers -- and
        # explains nothing about what the thing is for.
        description = clean(curate.DESCRIPTIONS[concept["slug"]])

        # Republish each photograph under the concept's own name, so the folder
        # reads as content rather than as extractor output.
        photos = []
        for number, index in enumerate(concept["photos"], start=1):
            filename = f"{concept['slug']}-{number}.jpg"
            shutil.copy2(PHOTOS / products[index]["photo"], IMAGES / filename)
            photos.append({"file": filename, "page": products[index]["page"]})

        lines += [
            "    {",
            f'        "slug": "{concept["slug"]}",',
            f'        "category": "{concept["group"]}",',
            f'        "name": {literal(concept["name"])},',
            f'        "catalog_name": {literal(primary["name"])},',
            f'        "description": {literal(description)},',
            f'        "source_page": {primary["page"]},',
            f'        "aliases": {json.dumps(concept["aliases"], ensure_ascii=False)},',
            '        "photos": [',
        ]
        for photo in photos:
            lines.append(
                f'            {{"file": "{photo["file"]}", "page": {photo["page"]}}},'
            )
        lines += ["        ],", "    },"]

    lines += [
        "]",
        "",
        "",
        "# Nothing is held back from this catalog: entries whose photograph could",
        "# not be told apart from another concept were merged during curation, and",
        "# a handful whose picture did not match its heading were left out there",
        "# rather than recorded here.",
        "QUARANTINE = []",
        "",
    ]

    (APP / "seed_data.py").write_text("\n".join(lines))

    blank = [c["slug"] for c in curate.CONCEPTS
             if not clean(curate.DESCRIPTIONS.get(c["slug"]))]
    if blank:
        print("WARNING - nothing written for:", ", ".join(blank))

    total = sum(f.stat().st_size for f in IMAGES.iterdir() if f.is_file())
    print(f"wrote seed_data.py: {len(curate.CONCEPTS)} items, "
          f"{sum(len(c['photos']) for c in curate.CONCEPTS)} photos "
          f"({total / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
