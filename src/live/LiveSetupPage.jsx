import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { createLiveGame, imageSrc, IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
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

  const [deck, setDeck] = useState(null); // null = every deck
  const [mode, setMode] = useState("choice");
  const [count, setCount] = useState(10);
  const [timeLimit, setTimeLimit] = useState(20);
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
        <PageHeader title="Class game" backTo="/" />

        <section className="setup-content">
          {IS_DEMO ? (
            <DemoNotice />
          ) : (
            <>
              <p className="setup-lead live-setup-lead">
                Put this screen on the board. Students join from their phones with a PIN and answer
                against the clock.
              </p>
              <p className="section-note">
                {user ? (
                  <Link to="/live/history">Past games</Link>
                ) : (
                  <>
                    <Link to="/sign-in">Sign in</Link> to keep the results of your games.
                  </>
                )}
              </p>

              {!catalog && <Loading />}
              {catalog?.failed && <ErrorMessage error={{ message: "Could not load the decks." }} />}

              {catalog && !catalog.failed && (
                <>
                  <fieldset className="option-group">
                    <legend className="option-legend">Deck</legend>
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
                        <span className="live-deck-name">Everything</span>
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
                    <legend className="option-legend">Answer by</legend>
                    <div className="option-row">
                      {[
                        ["choice", "image_search", "Name it", "Photo on the board, pick the name"],
                        ["inverted", "grid_view", "Find it", "Name on the board, pick the photo"],
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
                    <legend className="option-legend">Questions</legend>
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
                        All
                        <span className="option-note">{available}</span>
                      </button>
                    </div>
                  </fieldset>

                  <fieldset className="option-group">
                    <legend className="option-legend">Time per question</legend>
                    <div className="option-row option-row-tight">
                      {TIMES.map((t) => (
                        <button
                          key={t}
                          type="button"
                          className={`option-button option-button-small ${timeLimit === t ? "is-selected" : ""}`}
                          aria-pressed={timeLimit === t}
                          onClick={() => setTimeLimit(t)}
                        >
                          {t}s
                        </button>
                      ))}
                    </div>
                  </fieldset>

                  {error && <ErrorMessage error={error} />}

                  <button className="primary-button" onClick={create} disabled={creating || !available} type="button">
                    {creating ? "Opening the room..." : "Open the room"}
                    {!creating && (
                      <span className="primary-button-note">
                        {length} question{length === 1 ? "" : "s"}, {timeLimit} seconds each
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
