import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { createLiveGame, imageSrc, IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { rich, useLang, useT } from "../i18n";
import { useProgress } from "../progress/context";
import { DemoNotice } from "./components";
import { saveHostToken } from "./game";

const LENGTHS = [5, 10, 15, 20];
const TIMES = [10, 20, 30, 60];

/**
 * The teacher sets up a class game: which deck, which way round, how many
 * questions and how long each one runs. Creating it opens the board with the
 * PIN for the class to join.
 */
function LiveSetupPage() {
  const navigate = useNavigate();
  const { catalog } = useProgress();
  const { user } = useAuth();
  const t = useT();
  const { lang: userLang } = useLang();

  const [deck, setDeck] = useState(null); // null = every deck
  const [mode, setMode] = useState("choice");
  const [count, setCount] = useState(10);
  const [timeLimit, setTimeLimit] = useState(20);
  const [gameLang, setGameLang] = useState(userLang);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  const decks = catalog?.decks ?? [];
  const available = deck
    ? (decks.find((d) => d.slug === deck)?.cards.length ?? 0)
    : (catalog?.items.length ?? 0);
  const length = Math.min(count, available || count);

  async function create() {
    setCreating(true);
    setError(null);
    try {
      const game = await createLiveGame({
        categorySlug: deck,
        mode,
        questionCount: length,
        timeLimit,
        lang: gameLang,
      });
      saveHostToken(game.pin, game.host_token);
      navigate(`/live/host/${game.pin}`, { replace: true });
    } catch (err) {
      setError(err);
      setCreating(false);
    }
  }

  return (
    <main className="setup-page">
      <div className="page-layout setup">
        <PageHeader title={t("live.setup.title")} backTo="/" />

        <section className="setup-content">
          {IS_DEMO ? (
            <DemoNotice />
          ) : (
            <>
              <p className="setup-lead live-setup-lead">
                {t("live.setup.lead")}
              </p>
              <p className="section-note">
                {user ? (
                  <Link to="/live/history">{t("live.setup.pastGames")}</Link>
                ) : (
                  rich(t("live.setup.signIn"), { signIn: <Link to="/sign-in">{t("common.signInLink")}</Link> })
                )}
              </p>

              {!catalog && <Loading />}
              {catalog?.failed && <ErrorMessage error={{ message: t("explore.loadFailed") }} />}

              {catalog && !catalog.failed && (
                <>
                  <fieldset className="option-group">
                    <legend className="option-legend">{t("live.setup.deck")}</legend>
                    <div className="live-deck-grid">
                      <button
                        type="button"
                        className={`live-deck ${deck === null ? "is-selected" : ""}`}
                        aria-pressed={deck === null}
                        onClick={() => setDeck(null)}
                      >
                        <span className="live-deck-icon material-symbols-outlined" aria-hidden="true">
                          apps
                        </span>
                        <span className="live-deck-name">{t("history.everything")}</span>
                        <span className="option-note">{catalog.items.length}</span>
                      </button>
                      {decks.map((d) => (
                        <button
                          key={d.slug}
                          type="button"
                          className={`live-deck ${deck === d.slug ? "is-selected" : ""}`}
                          aria-pressed={deck === d.slug}
                          onClick={() => setDeck(d.slug)}
                        >
                          {d.image_url ? (
                            <img className="live-deck-thumb" src={imageSrc(d.image_url)} alt="" loading="lazy" />
                          ) : (
                            <span className="live-deck-icon material-symbols-outlined" aria-hidden="true">
                              science
                            </span>
                          )}
                          <span className="live-deck-name">{d.name}</span>
                          <span className="option-note">{d.cards.length}</span>
                        </button>
                      ))}
                    </div>
                  </fieldset>

                  <fieldset className="option-group">
                    <legend className="option-legend">{t("setup.answerBy")}</legend>
                    <div className="option-row">
                      {[
                        ["choice", "image_search", t("mode.choice"), t("live.setup.choiceNote")],
                        ["inverted", "grid_view", t("mode.inverted"), t("live.setup.invertedNote")],
                      ].map(([id, icon, title, note]) => (
                        <button
                          key={id}
                          type="button"
                          className={`option-button ${mode === id ? "is-selected" : ""}`}
                          aria-pressed={mode === id}
                          onClick={() => setMode(id)}
                        >
                          <span className="option-icon material-symbols-outlined" aria-hidden="true">
                            {icon}
                          </span>
                          {title}
                          <span className="option-note">{note}</span>
                        </button>
                      ))}
                    </div>
                  </fieldset>

                  <fieldset className="option-group">
                    <legend className="option-legend">{t("setup.questions")}</legend>
                    <div className="option-row option-row-tight">
                      {LENGTHS.filter((n) => n < available).map((n) => (
                        <button
                          key={n}
                          type="button"
                          className={`option-button option-button-small ${length === n ? "is-selected" : ""}`}
                          aria-pressed={length === n}
                          onClick={() => setCount(n)}
                        >
                          {n}
                        </button>
                      ))}
                      <button
                        type="button"
                        className={`option-button option-button-small ${length === available ? "is-selected" : ""}`}
                        aria-pressed={length === available}
                        onClick={() => setCount(available)}
                      >
                        {t("setup.all")}
                        <span className="option-note">{available}</span>
                      </button>
                    </div>
                  </fieldset>

                  <fieldset className="option-group">
                    <legend className="option-legend">{t("live.setup.time")}</legend>
                    <div className="option-row option-row-tight">
                      {TIMES.map((sec) => (
                        <button
                          key={sec}
                          type="button"
                          className={`option-button option-button-small ${timeLimit === sec ? "is-selected" : ""}`}
                          aria-pressed={timeLimit === sec}
                          onClick={() => setTimeLimit(sec)}
                        >
                          {t("live.setup.seconds", { n: sec })}
                        </button>
                      ))}
                    </div>
                  </fieldset>

                  <fieldset className="option-group">
                    <legend className="option-legend">{t("live.setup.lang")}</legend>
                    <div className="option-row option-row-tight">
                      {["en", "ru"].map((code) => (
                        <button
                          key={code}
                          type="button"
                          className={`option-button option-button-small ${gameLang === code ? "is-selected" : ""}`}
                          aria-pressed={gameLang === code}
                          onClick={() => setGameLang(code)}
                        >
                          {t(`live.setup.lang.${code}`)}
                        </button>
                      ))}
                    </div>
                  </fieldset>

                  {error && <ErrorMessage error={error} />}

                  <button className="primary-button" onClick={create} disabled={creating || !available} type="button">
                    {creating ? t("live.opening") : t("live.setup.open")}
                    {!creating && (
                      <span className="primary-button-note">
                        {t("live.setup.note", { n: length, s: timeLimit })}
                      </span>
                    )}
                  </button>
                </>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  );
}

export default LiveSetupPage;
