"""One sheet per group: every concept as a row of its own photographs.

Two things have to be true for the quiz to be fair, and both are visual:
  * every photograph in a row shows the same piece of glassware, and
  * no two rows could be confused for each other.
This is the only way to check either.
"""

import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

import curate

HERE = pathlib.Path(__file__).parent
OUT = HERE / "concepts"

THUMB = 190
LABEL_W = 300
ROW_H = THUMB + 22


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = pathlib.Path("/usr/share/fonts/truetype/dejavu") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    products = [p for p in json.loads((HERE / "products.json").read_text()) if p.get("photo")]
    name_font, title_font = font(15, True), font(21, True)

    for slug, group_name, _ in curate.GROUPS:
        members = [c for c in curate.CONCEPTS if c["group"] == slug]
        widest = max(len(c["photos"]) for c in members)

        width = LABEL_W + widest * THUMB
        height = 46 + len(members) * ROW_H
        sheet = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((14, 12), f"{group_name}  --  {len(members)} concepts",
                  fill="black", font=title_font)

        for row, concept in enumerate(members):
            y = 46 + row * ROW_H
            draw.line([(0, y), (width, y)], fill="#dddddd")
            draw.text((10, y + 10), concept["name"], fill="#111111", font=name_font)
            draw.text((10, y + 32), f"{len(concept['photos'])} photos",
                      fill="#b00050", font=font(13))

            for column, index in enumerate(concept["photos"]):
                photo = Image.open(HERE / "photos" / products[index]["photo"]).convert("RGB")
                photo.thumbnail((THUMB - 12, THUMB - 12), Image.LANCZOS)
                x = LABEL_W + column * THUMB
                sheet.paste(photo, (x + (THUMB - photo.width) // 2, y + 8))
                draw.text((x + 4, y + THUMB + 2), f"#{index}", fill="#888888", font=font(12))

        sheet.save(OUT / f"{slug}.png")

    print("wrote", len(list(OUT.glob("*.png"))), "concept sheets")


if __name__ == "__main__":
    main()
