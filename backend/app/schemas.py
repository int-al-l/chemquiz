"""Pydantic models for the public API.

The split that matters here is between the content schemas (which may show
names freely) and the quiz schemas (which must not). `QuizQuestionOut` has no
field that reveals the answer of an unanswered question -- in choice mode it
carries an image and four shuffled names, in inverted mode a name and four
shuffled images (without their names).
"""

from __future__ import annotations

import datetime as dt
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuizMode(str, Enum):
    CHOICE = "choice"      # photo shown, pick the name
    INVERTED = "inverted"  # name shown, pick the photo


# --- content --------------------------------------------------------------


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    catalog_name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    # Every photograph of this concept; the quiz shows one at a time.
    photo_urls: list[str] = Field(default_factory=list)
    photo_count: int = 0
    # Parallel to photo_urls; None where the photo needs no attribution.
    photo_credits: list[Optional[str]] = Field(default_factory=list)
    category_slug: Optional[str] = None


class CategoryOut(BaseModel):
    """A category without its contents -- used in lists."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    child_count: int = 0
    item_count: int = 0
    # Items reachable from here including every descendant: what a quiz can draw on.
    quizzable_count: int = 0


class CategoryDetailOut(CategoryOut):
    """A category with everything needed to render its page."""

    parent: Optional[CategoryOut] = None
    children: list[CategoryOut] = Field(default_factory=list)
    items: list[ItemOut] = Field(default_factory=list)


# --- quiz -----------------------------------------------------------------


class QuizStartIn(BaseModel):
    category_slug: Optional[str] = Field(
        default=None,
        description="Draw questions from this category and its descendants. "
        "Omit to draw from the whole library.",
    )
    mode: QuizMode = QuizMode.CHOICE
    question_count: int = Field(default=10, ge=1, le=500)


class QuizChoiceOut(BaseModel):
    """One selectable answer. `id` is opaque to the player.

    Choice mode fills `name`; inverted mode fills `image_url` only -- sending
    the name with the picture would give the answer away.
    """

    id: int
    name: Optional[str] = None
    image_url: Optional[str] = None


class QuizQuestionOut(BaseModel):
    position: int
    # Choice mode: the photograph to name.
    image_url: Optional[str] = None
    # Inverted mode: the name whose photograph must be found.
    prompt: Optional[str] = None
    choices: list[QuizChoiceOut] = Field(default_factory=list)
    answered: bool = False


class QuizSessionOut(BaseModel):
    token: str
    mode: QuizMode
    question_count: int
    category_slug: Optional[str] = None
    category_name: Optional[str] = None
    answered_count: int = 0
    correct_count: int = 0
    is_complete: bool = False
    questions: list[QuizQuestionOut] = Field(default_factory=list)


class QuizAnswerIn(BaseModel):
    position: int = Field(ge=1)
    choice_id: int


class QuizAnswerOut(BaseModel):
    position: int
    is_correct: bool
    # Revealed only now that the question has been answered.
    correct_item: ItemOut
    # The option id that was right (equal to correct_item.id) and the one picked.
    correct_choice_id: int
    given_choice_id: Optional[int] = None
    given_answer: Optional[str] = None
    answered_count: int
    correct_count: int
    is_complete: bool


class QuizResultQuestionOut(BaseModel):
    position: int
    # Null until the question has been answered -- see crud.results_payload.
    item: Optional[ItemOut] = None
    image_url: Optional[str] = None
    given_answer: Optional[str] = None
    is_correct: bool
    answered: bool


class QuizResultsOut(BaseModel):
    token: str
    mode: QuizMode
    category_slug: Optional[str] = None
    category_name: Optional[str] = None
    question_count: int
    answered_count: int
    correct_count: int
    is_complete: bool
    created_at: dt.datetime
    completed_at: Optional[dt.datetime] = None
    questions: list[QuizResultQuestionOut] = Field(default_factory=list)


# --- account --------------------------------------------------------------


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=200)


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=200)


class EmailIn(BaseModel):
    email: str = Field(min_length=3, max_length=320)


class VerifyIn(BaseModel):
    """Redeem a verification email: the typed code with the email, or the
    token from the link on its own."""

    email: Optional[str] = None
    code: Optional[str] = None
    token: Optional[str] = None


class ResetIn(VerifyIn):
    password: str = Field(min_length=1, max_length=200)


class PendingOut(BaseModel):
    """An email was (or would have been) sent; the next step is a code."""

    status: Literal["code_sent"] = "code_sent"
    email: str
    purpose: Literal["verify", "reset"]


class SignedInUser(BaseModel):
    """What the browser keeps after signing in. `token` is the session."""

    token: str
    email: str
    name: str
    saved_count: int = 0


class SavedOut(BaseModel):
    slug: str
    saved: bool


class ImportListIn(BaseModel):
    slugs: list[str] = Field(default_factory=list, max_length=500)


class ProgressIn(BaseModel):
    data: dict


class ProgressOut(BaseModel):
    data: dict


# --- misc -----------------------------------------------------------------


class HealthOut(BaseModel):
    status: Literal["ok"] = "ok"
    categories: int
    items: int
