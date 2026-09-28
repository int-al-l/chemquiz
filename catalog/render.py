"""Render each product photograph out of the catalog.

The catalog stores its photographs small -- around 166x282 pixels, about 100 dpi
at the size they are printed. Rendering the *page* at high zoom, which this
script used to do, just interpolates that: it produces a large file with no
more detail in it.

So instead the embedded image is taken at its native resolution and enlarged
with FSRCNN, a small super-resolution network. That recovers noticeably cleaner
edges than a plain resize -- glass outlines and joint collars stop ringing --
though nothing can invent detail the file never had. The honest fix is a
print-resolution source PDF.

Pages where the picture is drawn with a clip or a soft mask fall back to
rendering the page region, since the raw XObject there is not what a reader
sees.
"""

import io
import json
import pathlib
import urllib.request

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageChops, ImageFilter

PDF = "/root/.claude/uploads/90b66f5d-8d4e-5a40-8c1a-0e88de52f455/dab90217-KemtechCatalog2025_draft4_compressed_web2.pdf"
HERE = pathlib.Path(__file__).parent
OUT = HERE / "photos"

MODEL = HERE / "FSRCNN_x4.pb"
MODEL_URL = (
    "https://raw.githubusercontent.com/Saafke/FSRCNN_Tensorflow/master/models/FSRCNN_x4.pb"
)
SCALE = 4

# Long edge of the finished file. The quiz shows the photo about 340px tall, so
# 760 still covers a 2x display with room over; past that the folder grows for
# detail nobody sees.
MAX_EDGE = 760

FALLBACK_ZOOM = 6.0     # for photos that have to be rendered from the page
PAD = 2.0


def load_upscaler():
    if not MODEL.exists():
        print("fetching FSRCNN model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(str(MODEL))
    sr.setModel("fsrcnn", SCALE)
    return sr


def trim(image, tolerance=12):
    """Crop the flat border the catalog leaves around each photograph."""
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
    diff = ImageChops.difference(rgb, background).convert("L")
    box = diff.point(lambda v: 255 if v > tolerance else 0).getbbox()
    if not box:
        return image
    x0, y0, x1, y1 = box
    return image.crop(
        (max(0, x0 - 3), max(0, y0 - 3),
         min(image.width, x1 + 3), min(image.height, y1 + 3))
    )


def upscale(image, sr):
    array = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    result = sr.upsample(array)
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


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
    if image.mode in {"P", "1"}:
        return None
    if image.width < 60 or image.height < 60:
        return None
    return image.convert("RGB")


def from_page(doc, product):
    x0, y0, x1, y1 = product["bbox"]
    clip = pymupdf.Rect(x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD)
    matrix = pymupdf.Matrix(FALLBACK_ZOOM, FALLBACK_ZOOM)
    pixmap = doc[product["pdf_index"]].get_pixmap(matrix=matrix, clip=clip)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.jpg"):
        old.unlink()

    products = json.loads((HERE / "products.json").read_text())
    doc = pymupdf.open(PDF)
    sr = load_upscaler()

    written = upscaled = rendered = 0
    for product in products:
        if not product.get("bbox"):
            product["photo"] = None
            continue

        image = native_image(doc, product)
        if image is not None:
            image = upscale(trim(image), sr)
            # FSRCNN leaves edges very slightly soft; a light unsharp mask
            # brings the glass outlines back without haloing.
            image = image.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=3))
            upscaled += 1
        else:
            image = trim(from_page(doc, product))
            rendered += 1

        if max(image.size) > MAX_EDGE:
            image.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)

        name = f"p{product['page']:03d}_{products.index(product):03d}.jpg"
        image.save(OUT / name, "JPEG", quality=87, optimize=True)
        product["photo"] = name
        written += 1

    (HERE / "products.json").write_text(json.dumps(products, indent=1, ensure_ascii=False))

    total = sum(f.stat().st_size for f in OUT.glob("*.jpg"))
    print(f"wrote {written} photos "
          f"({upscaled} upscaled from the embedded image, {rendered} rendered from the page), "
          f"{total / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
