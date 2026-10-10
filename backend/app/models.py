"""Database models.

Content lives in three tables -- Category (a tree), Item (a piece of glassware)
and ItemAlias (accepted spellings for typed answers). Play lives in two more --
QuizSession and QuizQuestion -- which hold the correct answers server-side so a
quiz in progress cannot be read out of the network tab.

Accounts live in User (email + password, verified by a code sent by email),
EmailCode (the one-time codes and links) and UserProgress (the learning
progress document: XP, per-card mastery, streak days, badges).

A teacher's own quizzes are CustomQuiz rows (app/quizzes.py).

Live classroom games live in LiveGame, LivePlayer and LiveAnswer (the rules
are in app/live.py). A game hosted while signed in stays after it ends, as the
host's history.
"""

from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Category(Base):
    """A node in the content tree.

    Depth is not fixed: 'Labware' is a root, 'Condensers' is its child, and a
    child of 'Condensers' would work the same way. A category holds items,
    child categories, or both.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    # Russian texts from content_ru.py; None means "show the English one".
    name_ru: Mapped[Optional[str]] = mapped_column(String(160), default=None)
    description_ru: Mapped[Optional[str]] = mapped_column(Text, default=None)

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), default=None, index=True
    )
    # Filename inside static/images, or None to fall back to a placeholder.
    image: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    parent: Mapped[Optional["Category"]] = relationship(
        back_populates="children", remote_side=[id]
    )
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="Category.sort_order, Category.name",
    )
    items: Mapped[list["Item"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="Item.sort_order, Item.name",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Category {self.slug}>"


class ItemPhoto(Base):
    """One photograph of an item.

    An item is a *concept* -- "Erlenmeyer flask" -- and the catalog shows that
    concept several times over: different sizes, a plain neck and a ground
    joint, with and without a cap. Those all hang here, so a quiz can ask about
    the same concept more than once without repeating a picture, while Explore
    still shows a single card.
    """

    __tablename__ = "item_photos"
    __table_args__ = (
        UniqueConstraint("item_id", "filename", name="uq_photo_per_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    # Where in the source catalog this particular picture came from.
    source_page: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    # Attribution for photographs under an open licence (Wikimedia Commons),
    # e.g. "Jane Doe, CC BY-SA 4.0, via Wikimedia Commons". Empty for the
    # catalogue's own product shots.
    credit: Mapped[Optional[str]] = mapped_column(String(300), default=None)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    item: Mapped["Item"] = relationship(back_populates="photos")


class Item(Base):
    """One piece of glassware -- the thing a quiz question is about.

    An item is a concept rather than a catalog line: every catalog entry that
    a photograph cannot distinguish from this one is folded in here, and its
    picture becomes another row in `photos`. That is what guarantees a
    multiple-choice question has exactly one right answer -- the four options
    are four items, and no two items look alike.
    """

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    # What the player sees and types: written for humans.
    name: Mapped[str] = mapped_column(String(200))
    # Exactly as it appears in the source catalog, kept for traceability.
    catalog_name: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    name_ru: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    description_ru: Mapped[Optional[str]] = mapped_column(Text, default=None)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    image: Mapped[Optional[str]] = mapped_column(String(255), default=None)

    # Where this came from, so a bad extraction can be traced back.
    source: Mapped[Optional[str]] = mapped_column(String(120), default=None)
    source_page: Mapped[Optional[int]] = mapped_column(Integer, default=None)

    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    category: Mapped["Category"] = relationship(back_populates="items")
    aliases: Mapped[list["ItemAlias"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
    photos: Mapped[list["ItemPhoto"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="ItemPhoto.sort_order, ItemPhoto.id",
    )

    @property
    def cover(self) -> Optional[str]:
        """The picture Explore shows on this item's card."""
        if self.image:
            return self.image
        return self.photos[0].filename if self.photos else None

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Item {self.slug}>"


class ItemAlias(Base):
    """An accepted spelling for typed mode.

    `normalized` is what grading actually compares against; `text` is kept so a
    human editing the content sees what they wrote.
    """

    __tablename__ = "item_aliases"
    __table_args__ = (
        UniqueConstraint("item_id", "normalized", name="uq_alias_per_item"),
        Index("ix_alias_normalized", "normalized"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(String(200))
    normalized: Mapped[str] = mapped_column(String(200))
    # "en" or "ru": which language this spelling belongs to.
    lang: Mapped[str] = mapped_column(String(2), default="en")

    item: Mapped["Item"] = relationship(back_populates="aliases")


class User(Base):
    """Someone using the site, identified by their email address.

    Signing in takes the email and a password. An account is usable only once
    its email is verified -- a six-digit code (or the link beside it) is mailed
    on registration, see `EmailCode`.

    Accounts created before passwords existed have `password_hash` = None;
    they set one through the password-reset flow, which also proves they own
    the address.

    `token` is what the browser keeps as its session. It is rotated whenever
    the password changes, which signs every other device out.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stored lowercased and stripped; that normalised form is the identity.
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))

    password_hash: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    token: Mapped[str] = mapped_column(String(43), unique=True, index=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    saved: Mapped[list["SavedItem"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="SavedItem.created_at.desc()",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<User {self.email}>"


class EmailCode(Base):
    """A one-time code mailed to a user, for verifying an address or resetting
    a password.

    The same email carries a six-digit code (to type on a phone) and a link (to
    click on a computer); either one redeems the row. Only hashes are stored.
    """

    __tablename__ = "email_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # "verify" or "reset"
    purpose: Mapped[str] = mapped_column(String(16))
    code_hash: Mapped[str] = mapped_column(String(64))
    link_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[Optional[dt.datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    user: Mapped["User"] = relationship()


class UserProgress(Base):
    """The learning-progress document for one user, stored as JSON.

    The browser owns the rules (XP, Leitner boxes, streaks) so that guests get
    the same experience without an account; the server stores the document and
    merges concurrent copies (see `progress.merge`).
    """

    __tablename__ = "user_progress"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    data: Mapped[str] = mapped_column(Text, default="{}")
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CustomQuiz(Base):
    """A teacher's own quiz (the rules are in `app/quizzes.py`).

    The questions are one JSON document, saved whole by the editor. Only the
    author sees the quiz. Games played from it keep their own frozen copy, so
    editing or deleting the quiz leaves past games as they were.
    """

    __tablename__ = "custom_quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    lang: Mapped[str] = mapped_column(String(2), default="en")
    questions: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SavedItem(Base):
    """One entry in a user's list."""

    __tablename__ = "saved_items"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_saved_once"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="saved")
    item: Mapped["Item"] = relationship()


class QuizSession(Base):
    """One run of a quiz, addressed by an unguessable token."""

    __tablename__ = "quiz_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(43), unique=True, index=True)

    # Null means the quiz drew from the whole library.
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), default=None
    )
    category_slug: Mapped[Optional[str]] = mapped_column(String(80), default=None)
    category_name: Mapped[Optional[str]] = mapped_column(String(160), default=None)

    # "choice" (photo -> pick the name) or "inverted" (name -> pick the photo).
    mode: Mapped[str] = mapped_column(String(16))
    question_count: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[Optional[dt.datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="QuizQuestion.position",
    )

    @property
    def correct_count(self) -> int:
        return sum(1 for q in self.questions if q.is_correct)

    @property
    def answered_count(self) -> int:
        return sum(1 for q in self.questions if q.answered_at is not None)

    @property
    def is_complete(self) -> bool:
        return self.answered_count >= self.question_count


class QuizQuestion(Base):
    """A single question inside a session.

    The answer never leaves the server until the question has been answered.
    `choice_item_ids` fixes the options at start time so a reload shows the
    same four options in the same order; in inverted mode `choice_photo_ids`
    fixes which photograph stands for each option.
    """

    __tablename__ = "quiz_questions"
    __table_args__ = (
        UniqueConstraint("session_id", "position", name="uq_question_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))

    # Which of the item's photographs this question shows. Fixed when the quiz
    # is built, so a reload shows the same picture rather than quietly swapping
    # to another variant of the same piece of glassware.
    photo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("item_photos.id", ondelete="SET NULL"), default=None
    )

    # Comma-separated item ids.
    choice_item_ids: Mapped[str] = mapped_column(String(200), default="")
    # Inverted mode only: comma-separated photo ids, parallel to the above.
    choice_photo_ids: Mapped[str] = mapped_column(String(200), default="")

    given_answer: Mapped[Optional[str]] = mapped_column(String(300), default=None)
    given_choice_id: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    answered_at: Mapped[Optional[dt.datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    session: Mapped["QuizSession"] = relationship(back_populates="questions")
    item: Mapped["Item"] = relationship()
    photo: Mapped[Optional["ItemPhoto"]] = relationship()

    @property
    def choice_ids(self) -> list[int]:
        if not self.choice_item_ids:
            return []
        return [int(part) for part in self.choice_item_ids.split(",") if part]

    @property
    def choice_photo_list(self) -> list[Optional[int]]:
        if not self.choice_photo_ids:
            return []
        return [int(p) if p else None for p in self.choice_photo_ids.split(",")]


class LiveGame(Base):
    """A live classroom game (the rules are in `app/live.py`).

    `pin` is how the class finds the game while it runs. It is cleared when the
    game is archived, so the six digits can go to a new game; the partial
    unique index keeps PINs unique among games that still have one, even when
    two backend processes create games at the same moment.

    `questions` is frozen when the game is created -- what the board shows, the
    options, which one is right, and the card revealed afterwards -- so a game
    in someone's history reads the same after the content changes.

    Times are epoch seconds, the clock `live._now()` reads.
    """

    __tablename__ = "live_games"
    __table_args__ = (
        Index(
            "uq_live_games_pin",
            "pin",
            unique=True,
            sqlite_where=text("pin IS NOT NULL"),
            postgresql_where=text("pin IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pin: Mapped[Optional[str]] = mapped_column(String(6), default=None)
    host_token: Mapped[str] = mapped_column(String(43), unique=True)
    # Null when the host was not signed in; such games are never kept.
    host_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), default=None, index=True
    )

    # "choice" or "inverted", as in QuizSession.
    mode: Mapped[str] = mapped_column(String(16))
    # "en" or "ru", chosen by the teacher; the questions are frozen in it.
    lang: Mapped[str] = mapped_column(String(2), default="en")
    time_limit: Mapped[int] = mapped_column(Integer)
    question_count: Mapped[int] = mapped_column(Integer)
    # A null slug means the game drew from the whole library.
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), default=None
    )
    category_slug: Mapped[Optional[str]] = mapped_column(String(80), default=None)
    category_name: Mapped[Optional[str]] = mapped_column(String(160), default=None)
    questions: Mapped[list] = mapped_column(JSON)

    phase: Mapped[str] = mapped_column(String(16), default="lobby")
    position: Mapped[int] = mapped_column(Integer, default=0)
    starts_at: Mapped[Optional[float]] = mapped_column(Float, default=None)
    deadline: Mapped[Optional[float]] = mapped_column(Float, default=None)
    closed_at: Mapped[Optional[float]] = mapped_column(Float, default=None)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[float] = mapped_column(Float)
    touched_at: Mapped[float] = mapped_column(Float)
    started_at: Mapped[Optional[float]] = mapped_column(Float, default=None)
    finished_at: Mapped[Optional[float]] = mapped_column(Float, default=None)


class LivePlayer(Base):
    """A phone in a live game, known by a nickname and a secret token."""

    __tablename__ = "live_players"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("live_games.id", ondelete="CASCADE"), index=True
    )
    token: Mapped[str] = mapped_column(String(43), unique=True)
    name: Mapped[str] = mapped_column(String(40))
    joined_at: Mapped[float] = mapped_column(Float)
    last_seen: Mapped[float] = mapped_column(Float)
    score: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    # Removed by the host: kept, but left out of everything anyone is shown.
    removed: Mapped[bool] = mapped_column(Boolean, default=False)


class LiveAnswer(Base):
    """One player's answer to one question.

    The unique constraint has the last word on "you have already answered":
    whichever backend process a second tap reaches, the database refuses it.
    """

    __tablename__ = "live_answers"
    __table_args__ = (
        UniqueConstraint("player_id", "position", name="uq_live_answer_once"),
        Index("ix_live_answers_game_position", "game_id", "position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("live_games.id", ondelete="CASCADE"))
    player_id: Mapped[int] = mapped_column(ForeignKey("live_players.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    choice_id: Mapped[int] = mapped_column(Integer)
    elapsed: Mapped[float] = mapped_column(Float)
    correct: Mapped[bool] = mapped_column(Boolean)
    points: Mapped[int] = mapped_column(Integer)
