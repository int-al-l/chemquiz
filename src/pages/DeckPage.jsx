import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import FlipCard from "../components/FlipCard";
import { MasteryBar, Ring } from "../components/ProgressBits";
import SavedError from "../components/SavedError";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchCategory, fetchItems, imageSrc } from "../api/client";
import { useApi } from "../hooks/useApi";
import { useSwipe } from "../hooks/useSwipe";
import { useT } from "../i18n";
import { useProgress } from "../progress/context";
import { deckSummary, dueSlugs, isDue, mastery } from "../progress/engine";
import { useSaved } from "../saved/context";

/**
 * One deck of cards, three ways to go through it:
 *
 *   Browse  swipe left/right (or the arrows) to move between cards, tap to
 *           turn a card over.
 *   Study   the Quizlet-style sort: swipe right "I know it", left "still
 *           learning". Cards still being learnt come back in the next round.
 *           Feeds the spaced-repetition boxes and earns XP.
 *   Grid    every card at once, to find one quickly.
 *
 * The page is exactly one screen tall; nothing scrolls except the grid.
 *
 * Reached as /explore/:slug (a category), /explore/all (every card),
 * /explore/saved (My list) and /review (cards due for review).
 */

const HIDE_KEY = "chemquiz.hideNames";

function readHide() {
  try {
    return window.localStorage.getItem(HIDE_KEY) === "1";
  } catch {
    return false;
  }
}

function shuffled(list) {
  const out = [...list];
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/** Due cards first, then new ones, then the rest -- the order a study round takes. */
function studyOrder(items, doc) {
  const now = Date.now();
  const rank = (item) => {
    const card = doc.cards?.[item.slug];
    if (isDue(card, now)) return 0;
    if (!card?.seen) return 1;
    return 2;
  };
  return shuffled(items).sort((a, b) => rank(a) - rank(b)).map((i) => i.slug);
}

function DeckPage({ review = false }) {
  const t = useT();
  const { slug: routeSlug } = useParams();
  const slug = review ? "review" : routeSlug;
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const progress = useProgress();
  const { doc, catalog } = progress;
  const { has, toggle, slugs: savedSlugs } = useSaved();

  const special = slug === "all" || slug === "saved" || slug === "review";

  const loader = useCallback(() => {
    if (special) return fetchItems().then((items) => ({ category: null, items }));
    return Promise.all([fetchCategory(slug), fetchItems(slug)]).then(([category, items]) => ({
      category,
      items,
    }));
  }, [slug, special]);
  const { data, error, loading, reload } = useApi(loader, [slug]);

  // The review deck is fixed when the page opens, so answering a card does not
  // make it vanish from under the finger.
  const [reviewSlugs] = useState(() =>
    review ? dueSlugs(doc, Object.keys(doc.cards ?? {})) : null,
  );

  const items = useMemo(() => {
    const all = data?.items ?? [];
    if (slug === "saved") return all.filter((i) => savedSlugs.includes(i.slug));
    if (slug === "review") {
      const set = new Set(reviewSlugs);
      return all.filter((i) => set.has(i.slug));
    }
    return all;
  }, [data, slug, savedSlugs, reviewSlugs]);

  const bySlug = useMemo(() => Object.fromEntries(items.map((i) => [i.slug, i])), [items]);

  const title =
    slug === "all"
      ? t("common.allCards")
      : slug === "saved"
        ? t("common.myList")
        : slug === "review"
          ? t("common.review")
          : (data?.category?.name ??
            catalog?.decks.find((d) => d.slug === slug)?.name ??
            t("deck.fallbackTitle"));

  const mode = review ? "study" : (params.get("mode") ?? "browse");
  const setMode = (m) => setParams(m === "browse" ? {} : { mode: m }, { replace: true });

  const [hideNames, setHideNames] = useState(readHide);
  useEffect(() => {
    try {
      window.localStorage.setItem(HIDE_KEY, hideNames ? "1" : "0");
    } catch {
      // ignore
    }
  }, [hideNames]);

  const summary = deckSummary(doc, items.map((i) => i.slug));

  const backTo = review ? "/" : "/explore";

  let body;
  if (loading) body = <Loading />;
  else if (error) body = <ErrorMessage error={error} onRetry={reload} />;
  else if (!items.length)
    body = (
      <div className="deck-empty">
        <span className="material-symbols-outlined" aria-hidden="true">
          {review ? "task_alt" : "inbox"}
        </span>
        <p>
          {review
            ? t("deck.nothingDue")
            : slug === "saved"
              ? t("deck.listEmpty")
              : t("deck.noCards")}
        </p>
        <Link className="primary-button" to="/explore">
          {t("deck.exploreDecks")}
        </Link>
      </div>
    );
  else if (mode === "grid")
    body = (
      <GridView
        items={items}
        doc={doc}
        onOpen={(index) => setParams({ card: String(index) }, { replace: true })}
      />
    );
  else if (mode === "study")
    body = (
      <StudyView
        key={slug}
        items={items}
        bySlug={bySlug}
        doc={doc}
        progress={progress}
        hideNames={hideNames}
        has={has}
        toggle={toggle}
        quizTo={special ? "/quiz/setup" : `/quiz/setup/${slug}`}
        onExit={() => (review ? navigate("/") : setMode("browse"))}
      />
    );
  else
    body = (
      <BrowseView
        key={slug}
        items={items}
        doc={doc}
        progress={progress}
        hideNames={hideNames}
        has={has}
        toggle={toggle}
        startAt={Number(params.get("card") ?? 0)}
      />
    );

  return (
    <main className="deck-page">
      <header className="deck-header">
        <button className="icon-button" onClick={() => navigate(backTo)} aria-label={t("deck.back")} type="button">
          <span className="material-symbols-outlined">arrow_back</span>
        </button>
        <h1 className="deck-title">{title}</h1>
        <button
          className={`icon-button ${hideNames ? "is-on" : ""}`}
          onClick={() => setHideNames((v) => !v)}
          aria-pressed={hideNames}
          title={t(hideNames ? "deck.showNames" : "deck.hideNames")}
          aria-label={t("deck.hideNamesLabel")}
          type="button"
        >
          <span className="material-symbols-outlined">{hideNames ? "visibility_off" : "visibility"}</span>
        </button>
      </header>

      {!review && items.length > 0 && (
        <nav className="mode-switch" aria-label={t("deck.modes")}>
          {[
            ["browse", "style", t("deck.browse")],
            ["study", "school", t("deck.study")],
            ["grid", "grid_view", t("deck.grid")],
          ].map(([id, icon, label]) => (
            <button
              key={id}
              className={mode === id ? "is-selected" : ""}
              aria-pressed={mode === id}
              onClick={() => setMode(id)}
              type="button"
            >
              <span className="material-symbols-outlined" aria-hidden="true">{icon}</span>
              {label}
            </button>
          ))}
        </nav>
      )}

      {items.length > 0 && <MasteryBar summary={summary} className="deck-mastery" />}

      <SavedError />
      {body}
    </main>
  );
}

// --- browse ------------------------------------------------------------------

function BrowseView({ items, doc, progress, hideNames, has, toggle, startAt }) {
  const t = useT();
  const [order, setOrder] = useState(() => items.map((i) => i.slug));
  const [index, setIndex] = useState(() => Math.min(Math.max(0, startAt || 0), items.length - 1));
  const [flipped, setFlipped] = useState(false);
  const bySlug = useMemo(() => Object.fromEntries(items.map((i) => [i.slug, i])), [items]);
  const item = bySlug[order[index]] ?? items[0];

  const flip = useCallback(() => {
    if (!flipped) progress.lookAt(item.slug);
    setFlipped(!flipped);
  }, [item, progress, flipped]);

  const swipe = useSwipe({
    onTap: flip,
    onSwipe: (dir) => go(dir === "left" ? 1 : -1),
  });


  function go(step) {
    if (swipe.leaving) return false;
    const next = index + step;
    if (next < 0 || next >= order.length) return false;
    swipe.flyOut(step > 0 ? "left" : "right", () => {
      setIndex(next);
      setFlipped(false);
    });
    return true;
  }

  useKeys({
    ArrowRight: () => go(1),
    ArrowLeft: () => go(-1),
    " ": flip,
    Enter: flip,
  });

  return (
    <>
      <CardStage swipe={swipe} cardKey={item.slug} scrollable={flipped}>
        <FlipCard
          key={item.slug}
          item={item}
          flipped={flipped}
          onFlip={flip}
          hideName={hideNames}
          masteryKey={mastery(doc.cards?.[item.slug])}
          saved={has(item.slug)}
          onToggleSave={() => toggle(item.slug)}
        />
      </CardStage>

      <footer className="deck-controls">
        <button
          className="round-button"
          onClick={() => {
            setOrder((o) => shuffled(o));
            setIndex(0);
            setFlipped(false);
          }}
          aria-label={t("deck.shuffle")}
          title={t("deck.shuffle")}
          type="button"
        >
          <span className="material-symbols-outlined">shuffle</span>
        </button>
        <button className="round-button is-big" onClick={() => go(-1)} disabled={index === 0} aria-label={t("deck.prev")} type="button">
          <span className="material-symbols-outlined">chevron_left</span>
        </button>
        <span className="deck-counter" aria-live="polite">
          {index + 1} / {order.length}
        </span>
        <button
          className="round-button is-big"
          onClick={() => go(1)}
          disabled={index === order.length - 1}
          aria-label={t("deck.next")}
          type="button"
        >
          <span className="material-symbols-outlined">chevron_right</span>
        </button>
        <button className="round-button" onClick={flip} aria-label={t("deck.turnOver")} title={t("deck.turnOverShort")} type="button">
          <span className="material-symbols-outlined">flip</span>
        </button>
      </footer>
      <p className="deck-hint">{t("deck.browseHint")}</p>
    </>
  );
}

// --- study -------------------------------------------------------------------

function StudyView({ items, bySlug, doc, progress, hideNames, has, toggle, quizTo, onExit }) {
  const t = useT();
  const [queue, setQueue] = useState(() => studyOrder(items, doc));
  const [pos, setPos] = useState(0);
  const [known, setKnown] = useState([]);
  const [learning, setLearning] = useState([]);
  const [flipped, setFlipped] = useState(false);
  const [round, setRound] = useState(1);
  const [roundXp, setRoundXp] = useState(0);
  const [done, setDone] = useState(false);

  const slug = queue[pos];
  const item = bySlug[slug];

  const flip = useCallback(() => {
    if (!item) return;
    if (!flipped) progress.lookAt(item.slug);
    setFlipped(!flipped);
  }, [item, progress, flipped]);

  function answer(knowIt) {
    if (!item || done || swipe.leaving) return false;
    swipe.flyOut(knowIt ? "right" : "left", () => {
      let gained = progress.studyAnswer(item.slug, knowIt);
      if (knowIt) setKnown((k) => [...k, item.slug]);
      else setLearning((l) => [...l, item.slug]);
      setFlipped(false);
      if (pos + 1 >= queue.length) {
        gained += progress.roundFinished();
        setDone(true);
      } else {
        setPos(pos + 1);
      }
      setRoundXp((x) => x + gained);
    });
    return true;
  }

  const swipe = useSwipe({
    onTap: flip,
    onSwipe: (dir) => answer(dir === "right"),
  });

  useKeys({
    ArrowRight: () => answer(true),
    ArrowLeft: () => answer(false),
    " ": flip,
    Enter: flip,
  });

  function startRound(slugs) {
    setQueue(slugs);
    setPos(0);
    setKnown([]);
    setLearning([]);
    setFlipped(false);
    setRoundXp(0);
    setDone(false);
    setRound((r) => r + 1);
  }

  if (done) {
    const total = known.length + learning.length;
    return (
      <section className="round-summary">
        <Ring value={total ? known.length / total : 0} size={140} stroke={12} className="summary-ring" label={t("deck.knownRound")}>
          <span className="summary-ring-value">
            {known.length}/{total}
          </span>
          <span className="summary-ring-label">{t("deck.known")}</span>
        </Ring>
        <h2>{learning.length ? t("deck.roundDone", { n: round }) : t("deck.allKnown")}</h2>
        <p className="summary-xp">{t("deck.roundXp", { n: roundXp })}</p>

        <div className="summary-actions">
          {learning.length > 0 && (
            <button className="primary-button" onClick={() => startRound(shuffled(learning))} type="button">
              {t("deck.keepGoing")}
              <span className="button-note">{t("deck.stillLearningCount", { n: learning.length })}</span>
            </button>
          )}
          <button
            className={learning.length ? "secondary-button" : "primary-button"}
            onClick={() => startRound(studyOrder(items, doc))}
            type="button"
          >
            {t("deck.studyAgain")}
          </button>
          <Link className="secondary-button" to={quizTo}>
            {t("deck.quiz")}
          </Link>
          <button className="text-button" onClick={onExit} type="button">
            {t("deck.done")}
          </button>
        </div>
      </section>
    );
  }

  if (!item) return null;

  const dx = swipe.dx;
  const lean = Math.min(1, Math.abs(dx) / 100);

  return (
    <>
      <div className="study-counts" aria-live="polite">
        <span className="count-learning">
          <span className="material-symbols-outlined" aria-hidden="true">replay</span>
          {learning.length}
        </span>
        <span className="study-position">
          {pos + 1} / {queue.length}
          {round > 1 ? t("deck.round", { n: round }) : ""}
        </span>
        <span className="count-known">
          {known.length}
          <span className="material-symbols-outlined" aria-hidden="true">check</span>
        </span>
      </div>

      <CardStage swipe={swipe} cardKey={`${round}-${slug}`} scrollable={flipped}>
        <FlipCard
          key={`${round}-${slug}`}
          item={item}
          flipped={flipped}
          onFlip={flip}
          hideName={hideNames}
          masteryKey={mastery(doc.cards?.[item.slug])}
          saved={has(item.slug)}
          onToggleSave={() => toggle(item.slug)}
        />
        <span className="swipe-stamp is-know" style={{ opacity: dx > 0 ? lean : 0 }}>
          {t("deck.knowIt")}
        </span>
        <span className="swipe-stamp is-learning" style={{ opacity: dx < 0 ? lean : 0 }}>
          {t("deck.stillLearning")}
        </span>
      </CardStage>

      <footer className="deck-controls study-controls">
        <button className="study-button is-learning" onClick={() => answer(false)} type="button">
          <span className="material-symbols-outlined" aria-hidden="true">close</span>
          {t("deck.stillLearning")}
        </button>
        <button className="round-button" onClick={flip} aria-label={t("deck.turnOver")} title={t("deck.turnOverShort")} type="button">
          <span className="material-symbols-outlined">flip</span>
        </button>
        <button className="study-button is-know" onClick={() => answer(true)} type="button">
          <span className="material-symbols-outlined" aria-hidden="true">check</span>
          {t("deck.knowIt")}
        </button>
      </footer>
      <p className="deck-hint">{t("deck.studyHint")}</p>
    </>
  );
}

// --- grid --------------------------------------------------------------------

function GridView({ items, doc, onOpen }) {
  const t = useT();
  return (
    <section className="card-grid">
      {items.map((item, index) => {
        const m = mastery(doc.cards?.[item.slug]);
        return (
          <button
            key={item.slug}
            className="grid-card"
            onClick={() => onOpen(index)}
            type="button"
          >
            <span className="grid-photo">
              {item.image_url && <img src={imageSrc(item.image_url)} alt="" loading="lazy" />}
            </span>
            <span className="grid-name">{item.name}</span>
            <span className={`grid-dot is-${m}`} title={t(`deck.status.${m}`)} />
          </button>
        );
      })}
    </section>
  );
}

// --- shared --------------------------------------------------------------------

/** The area the card lives in: follows the finger, flies off, springs in. */
function CardStage({ swipe, cardKey, scrollable = false, children }) {
  const { dx, dragging, leaving, handlers } = swipe;
  let transform = `translateX(${dx}px) rotate(${dx * 0.04}deg)`;
  if (leaving === "left") transform = "translateX(-130%) rotate(-8deg)";
  if (leaving === "right") transform = "translateX(130%) rotate(8deg)";

  return (
    <div className="card-stage">
      <div
        key={cardKey}
        className={`card-mover ${scrollable ? "can-scroll" : ""} ${dragging ? "is-dragging" : ""} ${leaving ? "is-leaving" : "is-entering"}`}
        style={{ transform }}
        {...handlers}
      >
        {children}
      </div>
    </div>
  );
}

/** Keyboard shortcuts for the deck, ignored while typing in a field. */
function useKeys(map) {
  useEffect(() => {
    function onKey(event) {
      if (event.target.closest?.("input, textarea, select")) return;
      if (event.target.closest?.("button") && (event.key === " " || event.key === "Enter")) return;
      const fn = map[event.key];
      if (fn) {
        event.preventDefault();
        fn();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });
}

export default DeckPage;
