"""Pictures teachers add to their own questions.

Whatever arrives is opened with Pillow and saved again as a plain JPEG under a
random name: anything that is not an image is refused, metadata (a phone's
GPS position) is dropped, and nothing the uploader named reaches the disk.
"""

from __future__ import annotations

import io
import secrets

from fastapi import APIRouter, Depends, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from .. import config, models
from ..i18n import AppError
from .account import current_user

router = APIRouter(prefix="/api/uploads", tags=["quizzes"])

MAX_BYTES = 5 * 1024 * 1024
LONG_SIDE = 1600
WEB_FORMATS = ("JPEG", "PNG", "GIF", "WEBP")
# ponytail: uploads are never cleaned up; sweep files no quiz mentions if disk ever matters.


def _flatten(img: Image.Image) -> Image.Image:
    """RGB on white: JPEG has no transparency, and a transparent PNG turns black."""
    if img.mode in ("RGBA", "LA", "P") or "transparency" in img.info:
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, "white")
        background.paste(img, mask=img.getchannel("A"))
        return background
    return img.convert("RGB")


@router.post("", status_code=201)
def upload(file: UploadFile, user: models.User = Depends(current_user)):
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise AppError("upload_too_big", status=413)
    try:
        # Web picture formats only: Pillow would also hand PostScript to Ghostscript.
        with Image.open(io.BytesIO(data), formats=WEB_FORMATS) as img:
            img = _flatten(ImageOps.exif_transpose(img))  # upright before EXIF is dropped
            img.thumbnail((LONG_SIDE, LONG_SIDE))
            name = f"{secrets.token_urlsafe(12)}.jpg"
            config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            img.save(config.UPLOADS_DIR / name, "JPEG", quality=85)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise AppError("upload_bad", status=422) from exc
    return {"url": f"{config.UPLOADS_URL_PREFIX}/{name}"}
