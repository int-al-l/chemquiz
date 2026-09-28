# Catalog pipeline

Turns the Kemtech America 2025 catalog PDF into the site's content:
`backend/seed_data.py` plus the photographs in `backend/static/images/`.

Run the steps in order from this folder. Only `curate.py` is meant to be edited
by hand — the rest is machinery.

```bash
pip install pymupdf pillow "opencv-contrib-python-headless<5" torch realesrgan basicsr

python extract.py        # product headings, prose and photo positions -> products.json
python render.py         # a fast draft of each photograph -> photos/
python sheets.py         # contact sheets of every photo, for the review below
python curate.py         # check the curation (no output means it is consistent)
python verify_sheets.py  # one sheet per group: each concept as a row of its photos
python photorender.py    # the finished photographs -> photos_hr/
python emit.py           # write backend/seed_data.py and copy the photos across
```

Then, from `../backend/`:

```bash
python seed.py --reset
```

`extract.py` reads the PDF from the path at the top of the file. Point it
somewhere else if you move the catalog.

## What each step is doing

**extract.py** — Each catalog page is one column of products: a photograph
against the outer edge, and beside it a bold uppercase heading, a sentence or
two of prose, and a table of part numbers. Headings are found by font
(`Helvetica-Bold` at 10.1pt, all caps) and paired with photographs by vertical
position.

Three things about the file make that harder than it sounds, and the code
carries the fixes:

- It is laid out as **spreads**, so every page's content stream also references
  the facing page's images at an off-page x offset. Those are discarded by
  intersecting each image against the page rectangle.
- Photographs sit on the **outer** edge, so they are in the left column on odd
  pages and the right column on even ones.
- A page that carries a detail shot alongside the product photographs breaks
  index-based pairing — one extra image shifts everything below it. Pairing is
  therefore a small dynamic program that keeps the vertical order and allows
  surplus images to be skipped.

**render.py** — The catalog stores its photographs at about 166x282 pixels,
roughly 100 dpi at printed size. Rendering the *page* at high zoom, which an
earlier version did, only interpolates that. So the embedded image is taken at
its native resolution and enlarged 4x with FSRCNN, a small super-resolution
network (the model downloads on first run, ~40 KB). It runs in seconds over the
whole catalog, which is what the contact sheets and the curation need, but the
result is soft and rings along every glass outline.

**photorender.py** — the same enlargement done properly, for the pictures the
site actually shows. It goes back to the *embedded* image, so nothing is
enlarged twice, and runs Real-ESRGAN x4plus over it: a far larger network,
about ten seconds a picture on a CPU, and much cleaner edges. The weights
(~64 MB) are not in the repository; the header of the file says where they came
from, and they belong in `models/RealESRGAN_x4plus.pth`.

On the way through, the red maker's mark is painted out — before the upscale,
so the network smooths the repair in rather than sharpening it. The mark is
found by matching the mark itself, `makers-mark.png`, and not by looking for
red: some of these pieces have genuinely red parts, and a colour rule erases
the PTFE handles of a stopcock along with the branding. Nothing else is
touched; the pieces are as photographed, moulded volume stamps and all.

No method invents detail the file never had, and the real fix is still a
print-resolution source PDF.

**curate.py** — the only file with judgement in it. `CONCEPTS` records which
catalog entries are the *same piece of glassware*; each becomes one card in
Explore, and the entries folded into it become that card's photo variants.
`DESCRIPTIONS` holds what each card says, written for a reader who has not met
the piece before: what it is, why it is that shape, and what it is used for.
The catalog's own prose is a buyer's description — wall thickness, joint sizes,
part numbers — and is not used on the cards.

The merge rule is visual: two entries collapse into one concept when a
photograph alone cannot separate them. That is what stops a question having two
right answers — every option offered is a different concept, and concepts that
look alike are not different concepts.

Running it checks two invariants and refuses to continue if either breaks:

- a photograph belongs to exactly one concept;
- no name or alias is accepted for two concepts, which would make typed mode
  mark a correct answer wrong.

**verify_sheets.py** — prints each group as rows of photographs. This is how
the curation was checked and how it should be checked again after editing:
every photo in a row must be the same object, and no two rows may be
confusable. Reviewing these caught a beaker heading paired with a volumetric
flask photograph, a "Hirsch funnel" whose picture is a plain conical funnel,
and two filter funnels indistinguishable from chromatography columns.

## Adding more of the catalog

Everything above already runs over all 144 pages: `products.json` holds 354
product blocks, 346 of them with a photograph. Only 218 photographs across 78
concepts are used, because the rest were either duplicates by eye or hardware
rather than glassware.

To widen the set, open the contact sheets in `sheets/`, pick the entries you
want by their `#number`, add a `dict(...)` to `CONCEPTS` and an entry to
`DESCRIPTIONS`, then re-run `curate.py`, `photorender.py` and `emit.py`. To
change wording or add accepted spellings, edit `name` or `aliases` on the
concept and its text in `DESCRIPTIONS`.
