"""API tests.

Each test runs against a throwaway SQLite file seeded with a small fixed
catalog, so nothing here depends on the real content.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import select

from app import crud, models
from app.database import Base, get_db
from app.main import app
from app.text import normalize
from app import mailer


@pytest.fixture()
def client():
    handle, path = tempfile.mkstemp(suffix=".db")
    os.close(handle)

    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSession() as db:
        labware = models.Category(slug="labware", name="Labware", sort_order=1)
        condensers = models.Category(
            slug="condensers", name="Condensers", parent=labware, sort_order=1
        )
        bubblers = models.Category(
            slug="bubblers", name="Bubblers", parent=labware, sort_order=2
        )
        empty = models.Category(slug="amino-acids", name="Amino acids", sort_order=2)
        db.add_all([labware, condensers, bubblers, empty])
        db.flush()

        # Each condenser carries several photographs, the way a real concept
        # does once its catalog variants have been merged into it.
        for index in range(5):
            item = models.Item(
                slug=f"condenser-{index}",
                name=f"Condenser {index}",
                category=condensers,
                image=f"condenser-{index}.jpeg",
            )
            db.add(item)
            db.add(
                models.ItemAlias(
                    item=item, text=f"Cond {index}", normalized=normalize(f"Cond {index}")
                )
            )
            for variant in range(3):
                db.add(
                    models.ItemPhoto(
                        item=item,
                        filename=f"condenser-{index}-{variant}.jpeg",
                        sort_order=variant,
                    )
                )

        for index in range(3):
            db.add(
                models.Item(
                    slug=f"bubbler-{index}",
                    name=f"Bubbler {index}",
                    category=bubblers,
                    image=f"bubbler-{index}.jpeg",
                )
            )

        # A category holding exactly one item, so a quiz over it has a known
        # answer at position 1 without the test needing to peek at the answers.
        solo = models.Category(slug="flasks", name="Flasks", parent=labware, sort_order=3)
        flask = models.Item(
            slug="round-bottom-flask",
            name="Round-bottom flask",
            category=solo,
            image="round-bottom-flask.jpeg",
        )
        db.add_all([solo, flask])
        db.flush()
        for alias in ("RBF", "Round bottomed flask"):
            db.add(models.ItemAlias(item=flask, text=alias, normalized=normalize(alias)))

        db.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        test_client.session_factory = TestingSession
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
    Path(path).unlink(missing_ok=True)


@pytest.fixture()
def db_session(client):
    """A session on the same throwaway database the client is using."""
    session = client.session_factory()
    try:
        yield session
    finally:
        session.close()


# --- content --------------------------------------------------------------


def test_root_categories_only(client):
    slugs = [c["slug"] for c in client.get("/api/categories").json()]
    assert slugs == ["labware", "amino-acids"]


def test_quizzable_count_includes_descendants(client):
    labware = next(c for c in client.get("/api/categories").json() if c["slug"] == "labware")
    # 5 condensers + 3 bubblers + 1 flask, none held directly by labware.
    assert labware["item_count"] == 0
    assert labware["quizzable_count"] == 9


def test_category_detail_has_children_and_parent(client):
    body = client.get("/api/categories/condensers").json()
    assert body["parent"]["slug"] == "labware"
    assert len(body["items"]) == 5
    assert body["items"][0]["image_url"].startswith("/static/images/")


def test_unknown_category_is_404(client):
    assert client.get("/api/categories/nope").status_code == 404


def test_items_filtered_by_category(client):
    assert len(client.get("/api/items?category=bubblers").json()) == 3
    assert len(client.get("/api/items?category=labware").json()) == 9
    assert len(client.get("/api/items?category=labware&include_descendants=false").json()) == 0


# --- quiz: starting -------------------------------------------------------


def start(client, **kwargs):
    payload = {"category_slug": "condensers", "mode": "choice", "question_count": 3}
    payload.update(kwargs)
    return client.post("/api/quiz/start", json=payload)


def test_start_returns_questions_without_answers(client):
    body = start(client).json()
    assert body["question_count"] == 3
    assert len(body["questions"]) == 3
    for question in body["questions"]:
        assert question["image_url"]
        assert len(question["choices"]) == 4
        # These keys and no others: nothing here says which choice is right.
        assert set(question) == {"position", "image_url", "prompt", "choices", "answered"}
        assert question["prompt"] is None


def test_choice_questions_have_no_duplicate_options(client):
    for question in start(client, question_count=5).json()["questions"]:
        names = [c["name"] for c in question["choices"]]
        assert len(names) == len(set(names))


def test_typed_mode_is_gone(client):
    assert start(client, mode="typed").status_code == 422


def test_inverted_mode_sends_a_name_and_four_unnamed_pictures(client):
    body = start(client, mode="inverted", question_count=5).json()
    for question in body["questions"]:
        assert question["prompt"].startswith("Condenser")
        assert question["image_url"] is None
        assert len(question["choices"]) == 4
        for choice in question["choices"]:
            assert choice["image_url"]
            assert choice["name"] is None
        urls = [c["image_url"] for c in question["choices"]]
        assert len(set(urls)) == 4


def test_inverted_answer_is_graded_by_the_picked_picture(client):
    body = start(client, mode="inverted", question_count=1).json()
    question = body["questions"][0]
    token = body["token"]
    result = None
    for choice in question["choices"]:
        # Find the right answer by elimination on a fresh quiz each time is
        # overkill; answer once and check the reveal is consistent.
        result = client.post(
            f"/api/quiz/{token}/answer", json={"position": 1, "choice_id": choice["id"]}
        ).json()
        break
    assert result["correct_item"]["name"] == question["prompt"]
    assert result["correct_choice_id"] == result["correct_item"]["id"]
    assert result["given_choice_id"] == question["choices"][0]["id"]
    assert result["is_correct"] is (result["given_choice_id"] == result["correct_choice_id"])
    # The correct picture is one of the item's own photographs.
    right = next(c for c in question["choices"] if c["id"] == result["correct_choice_id"])
    assert right["image_url"] in result["correct_item"]["photo_urls"]


def test_inverted_quiz_reloads_with_the_same_pictures(client):
    body = start(client, mode="inverted").json()
    again = client.get(f"/api/quiz/{body['token']}").json()
    assert again["questions"] == body["questions"]


def test_items_are_not_repeated_within_a_quiz(client):
    body = start(client, question_count=5).json()
    images = [q["image_url"] for q in body["questions"]]
    assert len(images) == len(set(images))


def test_asking_for_more_questions_than_items_shortens_the_quiz(client):
    body = start(client, question_count=50).json()
    assert body["question_count"] == 5
    assert len(body["questions"]) == 5


def test_start_on_empty_category_is_409(client):
    assert start(client, category_slug="amino-acids").status_code == 409


def test_start_on_unknown_category_is_404(client):
    assert start(client, category_slug="nope").status_code == 404


def test_question_count_is_validated(client):
    assert start(client, question_count=0).status_code == 422
    assert start(client, question_count=9999).status_code == 422


def test_a_custom_question_count_is_accepted(client):
    body = start(client, category_slug="labware", question_count=7).json()
    assert body["question_count"] == 7


def test_reloading_a_quiz_returns_the_same_questions(client):
    body = start(client).json()
    again = client.get(f"/api/quiz/{body['token']}").json()
    assert again["questions"] == body["questions"]


# --- quiz: answering ------------------------------------------------------


def question_choices(client, token, position):
    question = client.get(f"/api/quiz/{token}").json()["questions"][position - 1]
    return question["choices"], question["image_url"]


def test_choice_answer_grades_and_reveals_the_item(client):
    body = start(client).json()
    token = body["token"]
    choices, image_url = question_choices(client, token, 1)

    response = client.post(
        f"/api/quiz/{token}/answer",
        json={"position": 1, "choice_id": choices[0]["id"]},
    )
    assert response.status_code == 200
    result = response.json()

    # The answer is revealed only now. The question showed one of the item's
    # photographs, which need not be the cover shown on its Explore card.
    assert image_url in result["correct_item"]["photo_urls"]
    expected = result["correct_item"]["name"] == choices[0]["name"]
    assert result["correct_item"]["category_slug"] == "condensers"
    assert result["is_correct"] is expected
    assert result["answered_count"] == 1


def test_answering_twice_is_rejected(client):
    body = start(client).json()
    token = body["token"]
    choice = body["questions"][0]["choices"][0]["id"]
    assert client.post(f"/api/quiz/{token}/answer", json={"position": 1, "choice_id": choice}).status_code == 200
    assert client.post(f"/api/quiz/{token}/answer", json={"position": 1, "choice_id": choice}).status_code == 409


def test_choice_id_must_be_one_of_the_options(client):
    body = start(client).json()
    offered = {c["id"] for c in body["questions"][0]["choices"]}
    stranger = next(i for i in range(1, 500) if i not in offered)
    response = client.post(
        f"/api/quiz/{body['token']}/answer",
        json={"position": 1, "choice_id": stranger},
    )
    assert response.status_code == 422


def test_an_answer_requires_a_choice_id(client):
    body = start(client).json()
    response = client.post(
        f"/api/quiz/{body['token']}/answer", json={"position": 1, "text": "Condenser 0"}
    )
    assert response.status_code == 422


def test_answering_a_missing_position_is_404(client):
    body = start(client).json()
    response = client.post(
        f"/api/quiz/{body['token']}/answer", json={"position": 99, "choice_id": 1}
    )
    assert response.status_code == 404


def test_unknown_token_is_404(client):
    assert client.get("/api/quiz/nope").status_code == 404
    assert client.get("/api/quiz/nope/results").status_code == 404


# --- quiz: results --------------------------------------------------------


def test_results_hide_answers_until_each_question_is_answered(client):
    body = start(client, question_count=3).json()
    token = body["token"]

    results = client.get(f"/api/quiz/{token}/results").json()
    # The whole answer key must not be readable from a URL mid-quiz.
    assert all(q["item"] is None for q in results["questions"])
    # The image is fine to send -- the player is already looking at it.
    assert all(q["image_url"] for q in results["questions"])

    first = body["questions"][0]
    client.post(
        f"/api/quiz/{token}/answer",
        json={"position": 1, "choice_id": first["choices"][0]["id"]},
    )

    results = client.get(f"/api/quiz/{token}/results").json()
    assert results["questions"][0]["item"] is not None
    assert all(q["item"] is None for q in results["questions"][1:])


def test_results_track_progress_and_completion(client):
    body = start(client, question_count=3).json()
    token = body["token"]

    results = client.get(f"/api/quiz/{token}/results").json()
    assert results["answered_count"] == 0
    assert results["is_complete"] is False
    assert results["completed_at"] is None

    correct = 0
    for question in body["questions"]:
        answer = client.post(
            f"/api/quiz/{token}/answer",
            json={"position": question["position"], "choice_id": question["choices"][0]["id"]},
        ).json()
        correct += 1 if answer["is_correct"] else 0

    results = client.get(f"/api/quiz/{token}/results").json()
    assert results["answered_count"] == 3
    assert results["is_complete"] is True
    assert results["completed_at"] is not None
    assert results["correct_count"] == correct
    assert all(q["item"]["name"] for q in results["questions"])


def test_abandoning_a_quiz_deletes_it(client):
    token = start(client).json()["token"]
    assert client.delete(f"/api/quiz/{token}").status_code == 204
    assert client.get(f"/api/quiz/{token}").status_code == 404


def test_whole_library_quiz_draws_from_every_category(client):
    body = client.post(
        "/api/quiz/start", json={"mode": "choice", "question_count": 9}
    ).json()
    assert body["question_count"] == 9
    assert body["category_slug"] is None


# --- one right answer per question ----------------------------------------
#
# The catalog describes the same piece of glassware many times over -- a 50 mL
# and a 100 mL conical flask, a condenser with and without removable hose
# connections. Those are merged into one item carrying several photographs, so
# these tests police the property that merge buys: a question's options are
# always four different items, and the item asked about is one of them exactly
# once.


def test_every_option_is_a_distinct_item(client):
    body = start(client, category_slug="condensers", question_count=5).json()
    for question in body["questions"]:
        ids = [c["id"] for c in question["choices"]]
        assert len(ids) == len(set(ids)), "an item was offered twice in one question"
        names = [c["name"] for c in question["choices"]]
        assert len(names) == len(set(names)), "two options carried the same name"


def test_the_answer_appears_exactly_once_among_the_options(client):
    body = start(client, question_count=5).json()
    token = body["token"]

    for question in body["questions"]:
        answer = client.post(
            f"/api/quiz/{token}/answer",
            json={"position": question["position"],
                  "choice_id": question["choices"][0]["id"]},
        ).json()
        correct_name = answer["correct_item"]["name"]
        matches = [c for c in question["choices"] if c["name"] == correct_name]
        assert len(matches) == 1, (
            f"{len(matches)} options named '{correct_name}' -- a player could "
            "pick a right answer and be marked wrong"
        )


def test_a_photo_variant_never_becomes_a_second_correct_option(client, db_session):
    """The failure this guards against is specific.

    If photo variants were separate items, a question showing one 100 mL
    conical flask could offer '50 mL conical flask' as a distractor, and both
    would be right. Variants are photos of one item instead, so the number of
    distinct items in the whole library is the number of distinct answers.
    """
    from app import models

    items = db_session.execute(select(models.Item)).scalars().all()
    names = [i.name for i in items]
    assert len(names) == len(set(names)), "two items share a name"

    # And no item's photographs are shared with another item.
    photos = db_session.execute(select(models.ItemPhoto)).scalars().all()
    files = [p.filename for p in photos]
    assert len(files) == len(set(files)), "a photograph belongs to two items"


def test_questions_can_show_different_photos_of_the_same_item(client, db_session):
    """Variety is the other half of the bargain: many photos, one card."""
    from app import models

    multi = [
        i for i in db_session.execute(select(models.Item)).scalars().all()
        if len(i.photos) > 1
    ]
    assert multi, "no item has more than one photograph"

    item = multi[0]
    seen = set()
    for _ in range(40):
        session = crud.create_quiz_session(
            db_session, mode="choice", question_count=1,
            category=item.category,
        )
        question = next(
            (q for q in session.questions if q.item_id == item.id), None
        )
        if question and question.photo_id:
            seen.add(question.photo_id)
        if len(seen) > 1:
            break

    assert len(seen) > 1, "the same photograph came up every time"


# --- accounts ---------------------------------------------------------------

PASSWORD = "flask-2024"


def last_code(email):
    mail = next(m for m in reversed(mailer.OUTBOX) if m["to"] == email)
    return re.search(r"Your code: (\d{6})", mail["text"]).group(1)


def last_link_token(email):
    mail = next(m for m in reversed(mailer.OUTBOX) if m["to"] == email)
    return re.search(r"token=([\w-]+)", mail["text"]).group(1)


def register(client, name="Anton", email="anton@example.com", password=PASSWORD):
    return client.post(
        "/api/auth/register", json={"name": name, "email": email, "password": password}
    )


def login(client, email="anton@example.com", password=PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def sign_in(client, name="Anton", email="anton@example.com"):
    """Register and verify on first use, log in afterwards."""
    response = login(client, email=email)
    if response.status_code == 200:
        return response
    assert register(client, name=name, email=email).status_code == 202
    return client.post(
        "/api/auth/verify", json={"email": email, "code": last_code(email.strip().lower())}
    )


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_registering_mails_a_code_and_verifying_signs_in(client):
    response = register(client)
    assert response.status_code == 202
    assert response.json() == {"status": "code_sent", "email": "anton@example.com",
                               "purpose": "verify"}

    # Cannot sign in before verifying.
    blocked = login(client)
    assert blocked.status_code == 403

    body = client.post(
        "/api/auth/verify", json={"email": "anton@example.com", "code": last_code("anton@example.com")}
    ).json()
    assert body["email"] == "anton@example.com"
    assert body["name"] == "Anton"
    assert len(body["token"]) > 20
    assert client.get("/api/auth/me", headers=auth(body["token"])).status_code == 200


def test_the_link_in_the_email_verifies_too(client):
    register(client)
    token = last_link_token("anton@example.com")
    body = client.post("/api/auth/verify", json={"token": token}).json()
    assert body["email"] == "anton@example.com"
    # Links are single-use.
    assert client.post("/api/auth/verify", json={"token": token}).status_code == 400


def test_a_wrong_code_is_refused_and_attempts_are_limited(client):
    register(client)
    code = last_code("anton@example.com")
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        r = client.post("/api/auth/verify", json={"email": "anton@example.com", "code": wrong})
        assert r.status_code == 400
    r = client.post("/api/auth/verify", json={"email": "anton@example.com", "code": code})
    assert r.status_code == 429


def test_login_checks_the_password(client):
    sign_in(client)
    assert login(client, password="wrong-pass-1").status_code == 401
    assert login(client, email="nobody@example.com").status_code == 401
    assert login(client).status_code == 200


def test_signing_in_again_returns_the_same_account(client):
    first = sign_in(client).json()
    second = login(client).json()
    assert first["token"] == second["token"]


def test_email_is_matched_case_and_space_insensitively(client):
    first = sign_in(client).json()
    again = login(client, email="  ANTON@Example.com  ").json()
    assert again["token"] == first["token"]


def test_registering_a_verified_email_again_is_refused(client):
    sign_in(client)
    assert register(client).status_code == 409


def test_an_unverified_registration_can_be_redone(client):
    register(client, password="first-pass-1")
    register(client, name="Anton R.", password="second-pass-2")
    code = last_code("anton@example.com")
    body = client.post("/api/auth/verify", json={"email": "anton@example.com", "code": code}).json()
    assert body["name"] == "Anton R."
    assert login(client, password="second-pass-2").status_code == 200


def test_weak_passwords_are_refused(client):
    assert register(client, password="short1").status_code == 422
    assert register(client, password="12345678901").status_code == 422
    assert register(client, password="onlyletters").status_code == 422


def test_a_bad_email_is_refused(client):
    assert register(client, email="not-an-email").status_code == 422
    assert register(client, email="also@bad").status_code == 422


def test_a_blank_name_is_refused(client):
    assert register(client, name="   ").status_code == 422


def test_password_reset_with_code_signs_out_other_devices(client):
    old_token = sign_in(client).json()["token"]
    mailer.OUTBOX.clear()

    assert client.post("/api/auth/forgot", json={"email": "anton@example.com"}).status_code == 202
    code = last_code("anton@example.com")
    body = client.post(
        "/api/auth/reset",
        json={"email": "anton@example.com", "code": code, "password": "new-pass-99"},
    ).json()
    assert body["token"] != old_token
    assert client.get("/api/auth/me", headers=auth(old_token)).status_code == 401
    assert login(client, password="new-pass-99").status_code == 200
    assert login(client).status_code == 401


def test_password_reset_with_link(client):
    sign_in(client)
    client.post("/api/auth/forgot", json={"email": "anton@example.com"})
    token = last_link_token("anton@example.com")
    r = client.post("/api/auth/reset", json={"token": token, "password": "new-pass-99"})
    assert r.status_code == 200


def test_forgot_does_not_reveal_whether_an_account_exists(client):
    r = client.post("/api/auth/forgot", json={"email": "ghost@example.com"})
    assert r.status_code == 202
    assert not any(m["to"] == "ghost@example.com" for m in mailer.OUTBOX)


def test_legacy_passwordless_accounts_set_a_password_by_reset(client, db_session):
    db_session.add(models.User(email="old@example.com", name="Old", token="t" * 43,
                               email_verified=False))
    db_session.commit()
    assert login(client, email="old@example.com").status_code == 409
    # The old token no longer works on its own: the account must verify.
    assert client.get("/api/auth/me", headers=auth("t" * 43)).status_code == 401
    client.post("/api/auth/forgot", json={"email": "old@example.com"})
    r = client.post("/api/auth/reset", json={
        "email": "old@example.com", "code": last_code("old@example.com"), "password": "fresh-pass-1"})
    assert r.status_code == 200
    assert login(client, email="old@example.com", password="fresh-pass-1").status_code == 200


# --- progress -----------------------------------------------------------------


def test_progress_is_stored_and_merged(client):
    token = sign_in(client).json()["token"]
    assert client.get("/api/me/progress", headers=auth(token)).json()["data"]["days"] == {}

    phone = {"days": {"2026-09-27": 40}, "cards": {"condenser-0": {"box": 2, "last": 100}},
             "badges": {"first-quiz": 5}, "updated": 100}
    laptop = {"days": {"2026-09-27": 10, "2026-09-28": 25},
              "cards": {"condenser-0": {"box": 3, "last": 200}, "bubbler-0": {"box": 1, "last": 50}},
              "badges": {"first-quiz": 3}, "goal": 100, "updated": 200}

    client.put("/api/me/progress", json={"data": phone}, headers=auth(token))
    merged = client.put("/api/me/progress", json={"data": laptop}, headers=auth(token)).json()["data"]

    assert merged["days"] == {"2026-09-27": 40, "2026-09-28": 25}
    assert merged["cards"]["condenser-0"]["box"] == 3
    assert "bubbler-0" in merged["cards"]
    assert merged["badges"]["first-quiz"] == 3
    assert merged["goal"] == 100
    assert client.get("/api/me/progress", headers=auth(token)).json()["data"] == merged


def test_progress_needs_a_token(client):
    assert client.get("/api/me/progress").status_code == 401


# --- the saved list -----------------------------------------------------------


def test_the_list_needs_a_token(client):
    assert client.get("/api/me/list").status_code == 401
    assert client.put("/api/me/list/condenser-0").status_code == 401


def test_an_unknown_token_is_refused(client):
    assert client.get("/api/me/list", headers=auth("nonsense")).status_code == 401


def test_saving_and_unsaving(client):
    token = sign_in(client).json()["token"]

    assert client.get("/api/me/list", headers=auth(token)).json() == []

    assert client.put("/api/me/list/condenser-0", headers=auth(token)).status_code == 201
    saved = client.get("/api/me/list", headers=auth(token)).json()
    assert [i["slug"] for i in saved] == ["condenser-0"]

    client.delete("/api/me/list/condenser-0", headers=auth(token))
    assert client.get("/api/me/list", headers=auth(token)).json() == []


def test_saving_twice_is_not_an_error_and_does_not_duplicate(client):
    token = sign_in(client).json()["token"]
    client.put("/api/me/list/condenser-0", headers=auth(token))
    assert client.put("/api/me/list/condenser-0", headers=auth(token)).status_code == 201
    assert len(client.get("/api/me/list", headers=auth(token)).json()) == 1


def test_unsaving_something_never_saved_is_not_an_error(client):
    token = sign_in(client).json()["token"]
    assert client.delete("/api/me/list/condenser-0", headers=auth(token)).status_code == 200


def test_saving_an_unknown_item_is_404(client):
    token = sign_in(client).json()["token"]
    assert client.put("/api/me/list/nope", headers=auth(token)).status_code == 404


def test_one_users_list_is_invisible_to_another(client):
    anton = sign_in(client, "Anton", "anton@example.com").json()["token"]
    maria = sign_in(client, "Maria", "maria@example.com").json()["token"]
    assert anton != maria

    client.put("/api/me/list/condenser-0", headers=auth(anton))
    client.put("/api/me/list/bubbler-1", headers=auth(maria))

    assert [i["slug"] for i in client.get("/api/me/list", headers=auth(anton)).json()] == [
        "condenser-0"
    ]
    assert [i["slug"] for i in client.get("/api/me/list", headers=auth(maria)).json()] == [
        "bubbler-1"
    ]

    # And one cannot delete the other's entry.
    client.delete("/api/me/list/condenser-0", headers=auth(maria))
    assert len(client.get("/api/me/list", headers=auth(anton)).json()) == 1


def test_the_list_follows_the_email_not_the_token(client):
    """The point of accounts: the same details on another device, same list."""
    first = sign_in(client).json()["token"]
    client.put("/api/me/list/condenser-2", headers=auth(first))

    # "Another device" -- sign in again with the same email.
    second = sign_in(client).json()["token"]
    saved = client.get("/api/me/list", headers=auth(second)).json()
    assert [i["slug"] for i in saved] == ["condenser-2"]


def test_importing_a_browser_list_adds_without_replacing(client):
    token = sign_in(client).json()["token"]
    client.put("/api/me/list/condenser-0", headers=auth(token))

    body = client.post(
        "/api/me/list/import",
        json={"slugs": ["condenser-1", "bubbler-0", "does-not-exist"]},
        headers=auth(token),
    )
    assert body.status_code == 200

    slugs = {i["slug"] for i in body.json()}
    # The pre-existing entry survives, the unknown slug is ignored quietly.
    assert slugs == {"condenser-0", "condenser-1", "bubbler-0"}


def test_importing_the_same_slugs_twice_does_not_duplicate(client):
    token = sign_in(client).json()["token"]
    payload = {"slugs": ["condenser-0", "condenser-1"]}
    client.post("/api/me/list/import", json=payload, headers=auth(token))
    body = client.post("/api/me/list/import", json=payload, headers=auth(token))
    assert len(body.json()) == 2


def test_me_reports_the_saved_count(client):
    token = sign_in(client).json()["token"]
    client.put("/api/me/list/condenser-0", headers=auth(token))
    client.put("/api/me/list/condenser-1", headers=auth(token))
    assert client.get("/api/auth/me", headers=auth(token)).json()["saved_count"] == 2


def test_saved_items_carry_their_photos(client):
    token = sign_in(client).json()["token"]
    client.put("/api/me/list/condenser-0", headers=auth(token))
    item = client.get("/api/me/list", headers=auth(token)).json()[0]
    assert item["photo_count"] == 3
    assert item["description"] is None or isinstance(item["description"], str)


# --- seeding ------------------------------------------------------------------


def test_pruning_removes_items_that_left_the_seed_file(client, db_session):
    from app import seeding

    token = sign_in(client).json()["token"]
    client.put("/api/me/list/bubbler-0", headers=auth(token))
    quiz = start(client, category_slug="bubblers", question_count=3).json()

    keep = {s for s in db_session.execute(select(models.Item.slug)).scalars()} - {"bubbler-0"}
    cats = {s for s in db_session.execute(select(models.Category.slug)).scalars()}
    removed = seeding.prune_removed(db_session, item_slugs=keep, category_slugs=cats)
    db_session.commit()

    assert removed == ["bubbler-0"]
    assert client.get("/api/items/bubbler-0").status_code == 404
    assert client.get("/api/me/list", headers=auth(token)).json() == []
    # The quiz that asked about it is gone rather than broken.
    assert client.get(f"/api/quiz/{quiz['token']}").status_code == 404
