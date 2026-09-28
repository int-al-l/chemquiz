"""Re-render the catalog photographs at a usable size with Real-ESRGAN.

The catalog stores its pictures at about 166x282 pixels. `render.py` enlarged
those with FSRCNN, a small and fast super-resolution network, and the result is
what the cards used to show: bigger, but soft, with ringing along every glass
outline.

This script goes back to the *embedded* image -- not the FSRCNN output, so
nothing is enlarged twice -- and runs Real-ESRGAN x4plus over it, which is a
much larger network and recovers far cleaner edges.

The red maker's mark is painted out before the upscale, so the network smooths
the patch in rather than sharpening a repair. It is found by matching the mark
itself -- `makers-mark.png`, lifted from one flask -- rather than by looking
for red, because some of these pieces have genuinely red parts: the PTFE
handles on a stopcock would be erased along with the branding.

Nothing else is altered. The pieces are exactly as photographed, moulded
volume stamps and all. About ten seconds per picture on this machine.

Run: python photorender.py      -> writes photos_hr/<name>.jpg
"""

import io
import json
import pathlib

import cv2
import numpy as np
import pymupdf
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from PIL import Image, ImageChops
from realesrgan import RealESRGANer

import curate

PDF = ("/root/.claude/uploads/90b66f5d-8d4e-5a40-8c1a-0e88de52f455/"
       "dab90217-KemtechCatalog2025_draft4_compressed_web2.pdf")
HERE = pathlib.Path(__file__).parent
OUT = HERE / "photos_hr"
WEIGHTS = HERE / "models" / "RealESRGAN_x4plus.pth"
MARK = HERE / "makers-mark.png"

MAX_EDGE = 1000        # a card shows ~340px tall; this covers a 2x display
MATCH = 0.60           # how like the mark a patch has to be
FALLBACK_ZOOM = 6.0
PAD = 2.0


def trim(image, tolerance=12):
    """Crop the flat border the catalog leaves around each photograph."""
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
    diff = ImageChops.difference(rgb, background).convert("L")
    box = diff.point(lambda v: 255 if v > tolerance else 0).getbbox()
    if not box:
        return image
    x0, y0, x1, y1 = box
    return image.crop((max(0, x0 - 3), max(0, y0 - 3),
                       min(image.width, x1 + 3), min(image.height, y1 + 3)))


def redness(rgb):
    """How far each pixel leans red, which is what the mark is printed in."""
    red, green, blue = (rgb[:, :, i].astype(np.int16) for i in range(3))
    return np.clip(red - np.maximum(green, blue), 0, 255).astype(np.uint8)


def find_mark(red, template):
    """Where the maker's mark is, or None.

    The mark is printed at whatever size the piece was photographed, so the
    template is tried at a range of scales and the best match kept. A match is
    only believed if the patch is actually red -- correlation alone always
    returns its best guess somewhere.
    """
    best = (0.0, None)
    for scale in (0.5, 0.65, 0.8, 0.9, 1.0, 1.15, 1.3, 1.5):
        patch = cv2.resize(template, None, fx=scale, fy=scale,
                           interpolation=cv2.INTER_AREA)
        if patch.shape[0] >= red.shape[0] or patch.shape[1] >= red.shape[1]:
            continue
        _, score, _, corner = cv2.minMaxLoc(
            cv2.matchTemplate(red, patch, cv2.TM_CCOEFF_NORMED))
        if score > best[0]:
            best = (score, (corner, patch.shape))

    score, found = best
    if score < MATCH or found is None:
        return None
    (x, y), (h, w) = found
    if red[y:y + h, x:x + w].mean() < 20:
        return None
    return x, y, w, h


def strip_mark(rgb, template):
    """Paint out the maker's mark and the size stamp printed under it."""
    red = redness(rgb)
    box = find_mark(red, template)
    if box is None:
        return rgb
    x, y, w, h = box

    mask = np.zeros(red.shape, np.uint8)
    mask[y:y + h, x:x + w] = 255

    # The joint size is printed in the same red directly beneath the mark.
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        (red > 22).astype(np.uint8), 8)
    for index in range(1, count):
        bx, by, bw, bh, area = stats[index]
        below = y + h <= by <= y + h + max(6, h // 2)
        aligned = bx > x - w and bx + bw < x + 2 * w
        if below and aligned and area < w * h:
            mask[labels == index] = 255

    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    return cv2.inpaint(rgb, mask, 8, cv2.INPAINT_TELEA)


def native_image(doc, product):
    """The embedded photograph, or None if it is not usable on its own."""
    xref = product.get("xref")
    if not xref:
        return None
    try:
        info = doc.extract_image(xref)
    except Exception:
        return None
    if not info.get("image"):
        return None
    image = Image.open(io.BytesIO(info["image"]))
    # A paletted or 1-bit image here means the page composites it with
    # something else; rendering the region is safer.
    if image.mode in {"P", "1"} or image.width < 60 or image.height < 60:
        return None
    return image.convert("RGB")


def from_page(doc, product):
    x0, y0, x1, y1 = product["bbox"]
    clip = pymupdf.Rect(x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD)
    pixmap = doc[product["pdf_index"]].get_pixmap(
        matrix=pymupdf.Matrix(FALLBACK_ZOOM, FALLBACK_ZOOM), clip=clip)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def main():
    OUT.mkdir(exist_ok=True)

    products = json.loads((HERE / "products.json").read_text())
    with_photo = [p for p in products if p.get("photo")]
    wanted = {with_photo[i]["photo"] for i in curate.all_photo_indices()}

    doc = pymupdf.open(PDF)
    template = np.array(Image.open(MARK).convert("L"))
    network = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23,
                      num_grow_ch=32, scale=4)
    upscaler = RealESRGANer(scale=4, model_path=str(WEIGHTS), model=network,
                            tile=0, half=False, device=torch.device("cpu"))

    done = 0
    for product in products:
        name = product.get("photo")
        if name not in wanted or (OUT / name).exists():
            continue

        image = native_image(doc, product)
        if image is None:
            # Drawn with a clip or a soft mask: what the raw XObject holds is
            # not what a reader sees, so render the page region instead. That
            # is already large, and needs no upscaling.
            picture = trim(from_page(doc, product))
        else:
            array = strip_mark(np.array(trim(image)), template)
            array, _ = upscaler.enhance(array[:, :, ::-1], outscale=4)
            picture = Image.fromarray(array[:, :, ::-1])

        if max(picture.size) > MAX_EDGE:
            picture.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)

        picture.save(OUT / name, "JPEG", quality=88, optimize=True)
        done += 1
        print(f"{done}/{len(wanted)} {name}", flush=True)

    total = sum(f.stat().st_size for f in OUT.glob("*.jpg"))
    print(f"wrote {len(list(OUT.glob('*.jpg')))} photographs "
          f"({total / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
