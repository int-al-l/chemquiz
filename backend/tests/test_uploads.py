"""Pictures for questions: only real images, made small and plain."""

from __future__ import annotations

import io

import pytest
from PIL import Image

from app import config
from app.quizzes import IMAGE_RE
from test_api import auth, client, sign_in  # noqa: F401 -- the seeded test app


@pytest.fixture()
def uploads(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOADS_DIR", tmp_path)
    return tmp_path


def png(size=(10, 10), color=(255, 0, 0, 255), mode="RGBA"):
    out = io.BytesIO()
    Image.new(mode, size, color).save(out, "PNG")
    return out.getvalue()


def send(client, data, headers, name="pic.png"):
    return client.post("/api/uploads", files={"file": (name, data, "image/png")}, headers=headers)


def teacher(client):
    return auth(sign_in(client).json()["token"])


def test_an_upload_becomes_a_jpeg_we_serve(client, uploads):
    res = send(client, png(size=(3000, 1000)), teacher(client))
    assert res.status_code == 201, res.text
    url = res.json()["url"]
    assert IMAGE_RE.match(url) and url.endswith(".jpg")
    with Image.open(uploads / url.rsplit("/", 1)[1]) as img:
        assert img.format == "JPEG" and max(img.size) == 1600


def test_transparent_png_gets_a_white_background(client, uploads):
    url = send(client, png(color=(0, 0, 0, 0)), teacher(client)).json()["url"]
    with Image.open(uploads / url.rsplit("/", 1)[1]) as img:
        assert min(img.convert("L").getdata()) > 240


def test_not_a_picture(client, uploads):
    res = send(client, b"%PDF-1.4 hello", teacher(client), name="x.pdf")
    assert res.status_code == 422 and res.json()["code"] == "upload_bad"


def test_too_big(client, uploads, monkeypatch):
    from app.routers import uploads as route
    monkeypatch.setattr(route, "MAX_BYTES", 100)
    res = send(client, png(size=(200, 200), mode="RGB", color=(1, 2, 3)), teacher(client))
    assert res.status_code == 413 and res.json()["code"] == "upload_too_big"


def test_sign_in_required(client, uploads):
    assert send(client, png(), {}).status_code == 401
