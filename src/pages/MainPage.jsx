import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Thumbnail from "../components/Thumbnail";
import { Icon } from "../components/AppShell";
import { IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { useProgress } from "../progress/context";
import { deckSummary, dueSlugs } from "../progress/engine";
import { titleKey, useT } from "../i18n";
import LanguageSwitch from "../i18n/LanguageSwitch";


/**
 * The home screen, after the OdanQuiz Figma ("Desktop · Главная" and
 * "Mobile · Главная"): progress, what to learn, the class game and the decks.
 * The sidebar and the tab bar around it come from AppShell.
 *
 * Motion is Jackbox-flavoured: the greeting drops in letter by letter, cards
 * pop in one after another with a small overshoot, bars fill, icons wiggle on
 * hover and cards squash when pressed. People who ask their system for reduced
 * motion get none of it.
 */
function MainPage() {
  const t = useT();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { doc, catalog, level, streak, today, goal } = useProgress();
  const [pin, setPin] = useState("");

  const decks = catalog?.decks ?? [];
  const due = dueSlugs(doc, (catalog?.items ?? []).map((i) => i.slug)).length;
  const record = Math.max(streak, bestStreak(doc));
  const levelTitle = t(titleKey(level.title));

  const summaries = decks.map((deck) => ({ deck, s: deckSummary(doc, deck.cards) }));
  const started = (s) => s.learning + s.familiar + s.mastered > 0;
  const current =
    summaries.find(({ s }) => started(s) && s.mastered < s.total) ?? summaries[0] ?? null;

  const firstName = user?.name?.split(" ")[0];
  const greeting = `${t(greetingKey())}${firstName ? `, ${firstName}` : ""}!`;

  // The big blue button on phones: review when something is due, else a quiz.
  const cta = due > 0
    ? { to: "/review", icon: "event_repeat", title: t("common.review"), blurb: t("main.reviewBlurb", { n: due }) }
    : { to: "/quiz/setup", icon: "science", title: t("main.quiz"), blurb: t("main.playBlurb") };

  const learnTiles = [
    { to: "/review", icon: "event_repeat", title: t("common.review"), blurb: due > 0 ? t("main.reviewBlurb", { n: due }) : t("explore.nothingDue"), badge: due || null, primary: due > 0 },
    { to: "/quiz/setup", icon: "science", title: t("main.quiz"), blurb: t("main.playBlurb"), primary: due === 0 },
    { to: "/explore", icon: "style", title: t("main.flashcards"), blurb: t("main.flashcardsBlurb") },
  ];

  const joinWithPin = (event) => {
    event.preventDefault();
    const clean = pin.replace(/\D/g, "");
    navigate(clean ? `/join/${clean}` : "/join");
  };

  let letter = 0; // running index across the greeting, for the letter drop

  return (
    <div className="oq-home">
      {/* ---------- phone header ---------- */}
      <header className="oq-mobile-header">
        <Link to="/" className="oq-logo">OdanQuiz</Link>
        <div className="oq-mobile-header-right">
          <LanguageSwitch />
          <Link to="/profile" className={`oq-pill is-fire ${streak > 0 ? "is-hot" : ""}`}>
            <Icon name="local_fire_department" />
            {t("main.streakShort", { n: streak })}
          </Link>
        </div>
      </header>

      <main className="oq-main">
        <h1 className="oq-greeting" aria-label={`${greeting} ${t("main.subtitle")}`}>
          <span className="oq-greeting-line" aria-hidden="true">
            {greeting.split(" ").map((word, w) => (
              <span className="oq-word" key={w}>
                {[...word].map((ch) => (
                  <span className="oq-letter" key={letter} style={{ "--l": letter++ }}>{ch}</span>
                ))}
              </span>
            ))}
          </span>
          <span className="oq-greeting-sub pop" style={{ "--i": 2 }} aria-hidden="true">
            {t("main.subtitle")}
          </span>
        </h1>

        {/* ---------- progress ---------- */}
        <Link to="/profile" className="oq-card oq-progress pop" style={{ "--i": 3 }} aria-label={t("main.progress")}>
          <div className="oq-level">
            <span className="oq-level-badge">{level.level}</span>
            <div className="oq-level-text">
              <p className="oq-subheader">{t("main.levelLine", { n: level.level, title: levelTitle })}</p>
              <p className="oq-body-2 oq-muted oq-desktop-only">
                {t("main.xpToNext", { into: fmt(level.into), span: fmt(level.span), next: level.level + 1 })}
              </p>
              <Bar value={level.fraction} className="oq-level-bar" />
              <p className="oq-caption oq-muted oq-mobile-only">
                {t("main.xpToNext", { into: fmt(level.into), span: fmt(level.span), next: level.level + 1 })}
              </p>
              <div className="oq-goal-inline oq-mobile-only">
                <Icon name="flag" className="oq-green" />
                <span className="oq-muted">{t("main.goalShort")}</span>
                <Bar value={today / goal} tone="green" thin />
                <strong>{Math.min(today, goal)}/{goal}</strong>
              </div>
            </div>
          </div>

          <span className="oq-divider oq-desktop-only" />

          <div className="oq-stat oq-desktop-only">
            <Icon name="local_fire_department" className={`oq-stat-icon oq-orange ${streak > 0 ? "is-hot" : ""}`} />
            <div>
              <p className="oq-subheader">{t("main.streakDays", { n: streak })}</p>
              <p className="oq-body-2 oq-muted">{t("main.record", { n: record })}</p>
            </div>
          </div>

          <span className="oq-divider oq-desktop-only" />

          <div className="oq-stat oq-desktop-only">
            <Icon name="flag" className="oq-stat-icon oq-green" />
            <div className="oq-goal">
              <p className="oq-subheader">{t("main.goalLine", { done: Math.min(today, goal), goal })}</p>
              <Bar value={today / goal} tone="green" />
            </div>
          </div>
        </Link>

        {/* ---------- phone: one big action, then carry on with a deck ---------- */}
        <Link to={cta.to} className="oq-cta pop oq-mobile-only" style={{ "--i": 4 }}>
          <span className="oq-icon-box is-white"><Icon name={cta.icon} /></span>
          <span className="oq-cta-text">
            <span className="oq-subheader">{cta.title}</span>
            <span className="oq-body-2">{cta.blurb}</span>
          </span>
          <Icon name="chevron_right" className="oq-cta-chevron" />
        </Link>

        {current && (
          <Link to={`/explore/${current.deck.slug}`} className="oq-card oq-continue pop oq-mobile-only" style={{ "--i": 5 }}>
            <Thumbnail imageUrl={current.deck.image_url} className="oq-continue-photo" />
            <span className="oq-continue-text">
              <span className="oq-caption oq-muted">{t("main.continueDeck")}</span>
              <span className="oq-body-1 oq-medium">{current.deck.name}</span>
              <Bar value={current.s.mastered / (current.s.total || 1)} thin />
              <span className="oq-caption oq-muted">{t("main.learned", { n: current.s.mastered, total: current.s.total })}</span>
            </span>
            <span className="oq-play"><Icon name="play_arrow" /></span>
          </Link>
        )}

        <section className="oq-card oq-class-mobile pop oq-mobile-only" style={{ "--i": 6 }}>
          <h2 className="oq-subheader oq-with-icon"><Icon name="groups" className="oq-blue-text" />{t("main.join")}</h2>
          <form className="oq-pin-row" onSubmit={joinWithPin}>
            <div className="oq-input">
              <input
                inputMode="numeric"
                autoComplete="off"
                placeholder={t("main.pinPlaceholder")}
                aria-label={t("main.pinPlaceholder")}
                value={pin}
                onChange={(e) => setPin(e.target.value)}
              />
              <Link to="/join" className="oq-input-icon" aria-label={t("main.joinShort")}>
                <Icon name="qr_code_scanner" />
              </Link>
            </div>
            <button type="submit" className="oq-button is-action">{t("main.pinGo")}</button>
          </form>
          <Link to="/live" className="oq-link">
            <Icon name="cast_for_education" />
            {t("main.hostOnBoard")}
            <Icon name="chevron_right" />
          </Link>
        </section>

        {/* ---------- wide screens: learn + in class ---------- */}
        <div className="oq-row oq-desktop-only">
          <section className="oq-card oq-learn pop" style={{ "--i": 4 }}>
            <h2 className="oq-header">{t("main.learn")}</h2>
            <div className="oq-learn-tiles">
              {learnTiles.map((tile, n) => (
                <Link key={tile.to} to={tile.to} className={`oq-tile ${tile.primary ? "is-primary" : ""} pop`} style={{ "--i": 5 + n }}>
                  <span className={`oq-icon-box ${tile.primary ? "is-blue" : ""}`}><Icon name={tile.icon} /></span>
                  <span className="oq-tile-title">
                    {tile.title}
                    {tile.badge ? <span className="oq-pill is-solid">{tile.badge}</span> : null}
                  </span>
                  <span className="oq-body-2">{tile.blurb}</span>
                </Link>
              ))}
            </div>
          </section>

          <section className="oq-card oq-class pop" style={{ "--i": 5 }}>
            <h2 className="oq-header">{t("main.inClass")}</h2>
            <Link to="/live" className="oq-tile is-row pop" style={{ "--i": 8 }}>
              <span className="oq-icon-box"><Icon name="cast_for_education" /></span>
              <span className="oq-tile-text">
                <span className="oq-tile-title">{t("main.hostShort")}</span>
                <span className="oq-body-2">{t("main.hostBlurb")}</span>
              </span>
            </Link>
            <Link to="/join" className="oq-tile is-row pop" style={{ "--i": 9 }}>
              <span className="oq-icon-box"><Icon name="qr_code_scanner" /></span>
              <span className="oq-tile-text">
                <span className="oq-tile-title">{t("main.joinShort")}</span>
                <span className="oq-body-2">{t("main.joinBlurbLong")}</span>
              </span>
            </Link>
          </section>
        </div>

        {/* ---------- decks ---------- */}
        {decks.length > 0 && (
          <section className="oq-card oq-decks pop" style={{ "--i": 7 }}>
            <div className="oq-decks-head">
              <h2 className="oq-header">{t("common.explore")}</h2>
              <Link to="/explore" className="oq-link">
                {t("main.allDecks")} · {decks.length}
                <Icon name="chevron_right" />
              </Link>
            </div>
            <div className="oq-deck-strip">
              {summaries.map(({ deck, s }, n) => (
                <Link key={deck.slug} to={`/explore/${deck.slug}`} className="oq-deck pop" style={{ "--i": 8 + Math.min(n, 8) }}>
                  <Thumbnail imageUrl={deck.image_url} className="oq-deck-photo" />
                  <span className="oq-deck-name">{deck.name}</span>
                  <span className="oq-caption oq-muted oq-desktop-only">{t("main.learned", { n: s.mastered, total: s.total })}</span>
                  <Bar value={s.mastered / (s.total || 1)} thin />
                </Link>
              ))}
            </div>
          </section>
        )}

        {IS_DEMO && <p className="oq-caption oq-muted oq-demo">{t("main.demoNote")}</p>}
      </main>
    </div>
  );
}

function Bar({ value, tone = "blue", thin = false, className = "" }) {
  const v = Math.max(0, Math.min(1, value || 0));
  return (
    <span className={`oq-bar is-${tone} ${thin ? "is-thin" : ""} ${className}`} aria-hidden="true">
      <span style={{ "--w": `${v * 100}%` }} />
    </span>
  );
}

function greetingKey(hour = new Date().getHours()) {
  if (hour >= 5 && hour < 12) return "main.morning";
  if (hour >= 12 && hour < 18) return "main.afternoon";
  return "main.evening";
}

/** 1240 -> "1 240", the way the design writes numbers. */
function fmt(n) {
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

/** Longest run of consecutive days with any XP, from the progress doc. */
function bestStreak(doc) {
  const days = Object.keys(doc.days ?? {}).filter((k) => doc.days[k] > 0).sort();
  let best = 0;
  let run = 0;
  let prev = null;
  for (const key of days) {
    const time = new Date(`${key}T12:00:00`).getTime();
    run = prev !== null && Math.round((time - prev) / 86400000) === 1 ? run + 1 : 1;
    best = Math.max(best, run);
    prev = time;
  }
  return best;
}

export default MainPage;
