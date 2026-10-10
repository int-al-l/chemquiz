"""FastAPI application entry point.

Run from the backend/ directory:

    uvicorn app.main:app --reload --port 8000

Interactive API docs are then at http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import crud, migrate, models, schemas, seeding
from .live import purge as purge_live_games
from .config import CORS_ORIGINS, IMAGES_DIR, STATIC_DIR
from .database import Base, SessionLocal, engine, get_db
from .i18n import AppError, request_lang
from .routers import account, content, live, live_history, quiz, quizzes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fine while the schema is still moving. Introduce Alembic before there is
    # data worth keeping through a schema change.
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    added = migrate.add_missing_columns(engine)
    if added:
        print(f"Added database columns: {', '.join(added)}")

    with SessionLocal() as db:
        # create_all() above happily produces an empty database, and an empty
        # database is a site with no content and no error -- every page just
        # says there is nothing here. So fill it on the way up.
        #
        # This only ever fires when there are no items at all, so it cannot
        # overwrite content someone has edited; `python seed.py` is still how
        # you reload after changing seed_data.py.
        if seeding.is_empty(db):
            print("Database is empty -- loading seed_data.py ...")
            try:
                counts = seeding.load_seed(db)
            except Exception as exc:  # noqa: BLE001 - want the reason on stdout
                print(f"  could not seed: {exc}")
                print("  run `python seed.py --reset` from the backend folder.")
            else:
                print(
                    f"  seeded {counts['categories']} categories, "
                    f"{counts['items']} items, {counts['photos']} photos."
                )
                if counts["missing"]:
                    print(
                        f"  WARNING: {len(counts['missing'])} photo file(s) are "
                        "missing from static/images."
                    )

        crud.purge_stale_sessions(db)
        purge_live_games(db)

    yield


app = FastAPI(
    title="ChemQuiz API",
    description="Content and quiz endpoints for the ChemQuiz site.",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppError)
def app_error(request: Request, exc: AppError):
    """Refusals say themselves in the game's language, else the request's."""
    return exc.response(exc.lang or request_lang(request))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(content.router)
app.include_router(quiz.router)
app.include_router(account.router)
app.include_router(live.router)
app.include_router(live_history.router)
app.include_router(quizzes.router)


@app.get("/api/health", response_model=schemas.HealthOut, tags=["meta"])
def health(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "categories": db.execute(select(func.count(models.Category.id))).scalar_one(),
        "items": db.execute(select(func.count(models.Item.id))).scalar_one(),
    }
