"""Build contact sheets so every photograph can be checked against its name.

Curation is the one step that cannot be automated: whether two entries are the
same piece of glassware is a judgement about what the picture shows, and the
only way to make it is to look.
"""

import json
import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent
OUT = HERE / "sheets"

COLS = 6
CELL_W, CELL_H = 300, 380
CAPTION_H = 86
PER_SHEET = COLS * 4


def font(size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
    ):
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    products = [p for p in json.loads((HERE / "products.json").read_text()) if p.get("photo")]

    label_font = font(15)
    index_font = font(17)

    for start in range(0, len(products), PER_SHEET):
        chunk = products[start : start + PER_SHEET]
        rows = (len(chunk) + COLS - 1) // COLS
        sheet = Image.new("RGB", (COLS * CELL_W, rows * (CELL_H + CAPTION_H)), "white")
        draw = ImageDraw.Draw(sheet)

        for position, product in enumerate(chunk):
            col, row = position % COLS, position // COLS
            x, y = col * CELL_W, row * (CELL_H + CAPTION_H)

            photo = Image.open(HERE / "photos" / product["photo"]).convert("RGB")
            photo.thumbnail((CELL_W - 24, CELL_H - 24), Image.LANCZOS)
            sheet.paste(photo, (x + (CELL_W - photo.width) // 2, y + 12))

            draw.rectangle([x, y, x + CELL_W - 1, y + CELL_H + CAPTION_H - 1],
                           outline="#cccccc")

            number = start + position
            draw.text((x + 8, y + CELL_H - 4), f"#{number}  p{product['page']}",
                      fill="#b00050", font=index_font)

            wrapped = textwrap.wrap(product["name"], width=36)[:3]
            for line_no, line in enumerate(wrapped):
                draw.text((x + 8, y + CELL_H + 18 + line_no * 18), line,
                          fill="black", font=label_font)

        path = OUT / f"sheet{start // PER_SHEET:02d}.png"
        sheet.save(path)

    print(f"{len(products)} photos across {len(list(OUT.glob('*.png')))} sheets")


if __name__ == "__main__":
    main()
