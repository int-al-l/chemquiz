"""The built site served by the backend itself, for running on one port."""

from __future__ import annotations

import pytest

from app import config
from test_api import client  # noqa: F401 -- the seeded test app


@pytest.fixture()
def site(tmp_path, monkeypatch):
    build = tmp_path / "dist"
    (build / "assets").mkdir(parents=True)
    (build / "index.html").write_text("<html>the app</html>")
    (build / "assets" / "app.js").write_text("console.log(1)")
    (tmp_path / "secret.txt").write_text("no")
    monkeypatch.setattr(config, "FRONTEND_DIR", build)
    return build


def test_files_are_served(client, site):
    assert client.get("/assets/app.js").text == "console.log(1)"


@pytest.mark.parametrize("path", ["/", "/quiz/setup", "/join/123456", "/live/history"])
def test_every_page_of_the_app_gets_index_html(client, site, path):
    res = client.get(path)
    assert res.status_code == 200 and res.text == "<html>the app</html>"


def test_the_api_is_not_swallowed(client, site):
    assert client.get("/api/health").json()["status"] == "ok"
    res = client.get("/api/nothing-here")
    assert res.status_code == 404 and res.headers["content-type"].startswith("application/json")


def test_nothing_outside_the_build_is_served(client, site):
    assert client.get("/..%2Fsecret.txt").text != "no"
    assert client.get("/assets/..%2F..%2Fsecret.txt").text != "no"


def test_without_a_build_there_is_no_site(client, monkeypatch):
    monkeypatch.setattr(config, "FRONTEND_DIR", None)
    assert client.get("/join/123456").status_code == 404
