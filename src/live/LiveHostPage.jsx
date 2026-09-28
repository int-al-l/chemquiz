import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ErrorMessage } from "../components/StatusMessage";
import {
  fetchLiveHost,
  imageSrc,
  IS_DEMO,
  liveClose,
  liveFinish,
  liveLock,
  liveNetwork,
  liveNext,
  liveRemovePlayer,
} from "../api/client";
import { Countdown, DemoNotice, QrCode, Shape } from "./components";
import { hostToken, OPTION_STYLES, questionClock, saveHostToken, useLivePoll, useServerNow } from "./game";

const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]", "::1"]);

/**
 * The address phones should open. A board opened as http://localhost would
 * hand out an address that only works on the board itself, so in that case
 * ask the server for this machine's address on the local network.
 */
function useJoinBase() {
  const { protocol, hostname, port } = window.location;
  const local = LOCAL_HOSTS.has(hostname);
  const [lanHost, setLanHost] = useState(null);

  useEffect(() => {
    if (!local) return;
    liveNetwork()
      .then(({ addresses }) => setLanHost(addresses[0] ?? null))
      .catch(() => {});
  }, [local]);

  const host = local ? lanHost : hostname;
  if (!host) return { base: null, local };
  return { base: `${protocol}//${host}${port ? `:${port}` : ""}`, local };
}

/**
 * The board at the front of the class. It shows the PIN while people join,
 * then each question, the answers as they come in, the right answer, and the
 * standings. The teacher drives it with one Next button (or Space / Enter).
 */
function LiveHostPage() {
  const { pin } = useParams();
  const navigate = useNavigate();
  const token = hostToken(pin);

  const { state, error, apply, offset } = useLivePoll(
    () => fetchLiveHost(pin, token),
    800,
    Boolean(token) && !IS_DEMO,
  );
  const running = state?.phase === "question";
  const now = useServerNow(offset, running);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState(null);

  async function act(fn) {
    if (busy) return;
    setBusy(true);
    setActionError(null);
    try {
      apply(await fn());
    } catch (err) {
      setActionError(err);
    } finally {
      setBusy(false);
    }
  }

  const next = () => act(() => liveNext(pin, token));

  async function close() {
    try {
      await liveClose(pin, token);
    } catch {
      /* already gone */
    }
    saveHostToken(pin, null);
    navigate("/live", { replace: true });
  }

  useEffect(() => {
    function onKey(event) {
      if (event.target.closest?.("input, textarea")) return;
      if (event.key === " " || event.key === "Enter" || event.key === "ArrowRight") {
        if (!state || state.phase === "finished") return;
        if (state.phase === "lobby" && state.players.length === 0) return;
        event.preventDefault();
        next();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (IS_DEMO) {
    return (
      <main className="live-board">
        <DemoNotice />
      </main>
    );
  }

  if (!token || (error && [403, 404].includes(error.status))) {
    return (
      <main className="live-board live-board-center">
        <div className="live-message">
          <h1>This game is not open on this screen</h1>
          <p>
            {token
              ? "It has ended, or the server was restarted."
              : "Only the device that opened a game can run its board."}
          </p>
          <Link className="primary-button live-inline-button" to="/live">
            Start a new game
          </Link>
        </div>
      </main>
    );
  }

  if (!state) {
    return (
      <main className="live-board live-board-center">
        {error ? <ErrorMessage error={error} /> : <p className="status-message">Opening the room...</p>}
      </main>
    );
  }

  return (
    <main className={`live-board phase-${state.phase}`}>
      {error && <div className="live-offline">Reconnecting to the server...</div>}

      {state.phase === "lobby" && (
        <Lobby
          state={state}
          busy={busy}
          onStart={next}
          onLock={() => act(() => liveLock(pin, token, !state.locked))}
          onRemove={(id) => act(() => liveRemovePlayer(pin, token, id))}
          onClose={close}
        />
      )}

      {(state.phase === "question" || state.phase === "reveal") && (
        <QuestionBoard state={state} now={now} busy={busy} onNext={next} />
      )}

      {state.phase === "scoreboard" && <Scoreboard state={state} busy={busy} onNext={next} />}

      {state.phase === "finished" && <Podium state={state} onNew={close} />}

      {actionError && (
        <div className="live-toast" role="alert">
          {actionError.message}
        </div>
      )}

      {state.phase !== "lobby" && state.phase !== "finished" && (
        <button
          className="live-end-button"
          type="button"
          onClick={() => {
            if (window.confirm("End the game now and show the final results?")) {
              act(() => liveFinish(pin, token));
            }
          }}
        >
          End game
        </button>
      )}
    </main>
  );
}

// --- lobby -------------------------------------------------------------------------

function Lobby({ state, busy, onStart, onLock, onRemove, onClose }) {
  const { base, local } = useJoinBase();
  const joinUrl = base ? `${base}/join/${state.pin}` : null;
  const shortUrl = base ? `${base.replace(/^https?:\/\//, "")}/join` : null;
  const count = state.players.length;

  return (
    <div className="live-lobby">
      <section className="live-join-panel">
        <div className="live-join-text">
          <p className="live-join-step">
            Go to <strong>{shortUrl ?? "this site"}</strong>
          </p>
          <p className="live-join-step">and enter the PIN</p>
          <p className="live-pin" aria-label={`Game PIN ${state.pin.split("").join(" ")}`}>
            {state.pin.slice(0, 3)}
            <span className="live-pin-gap" />
            {state.pin.slice(3)}
          </p>
          {local && !base && (
            <p className="live-join-warn">
              This board is open as “localhost”, which phones cannot reach. Open the site using this
              computer's network address instead.
            </p>
          )}
        </div>
        {joinUrl && (
          <div className="live-qr-box">
            <QrCode text={joinUrl} label="Scan to join" />
            <span>Scan to join</span>
          </div>
        )}
      </section>

      <section className="live-players">
        <header className="live-players-head">
          <h2>
            <span className="material-symbols-outlined" aria-hidden="true">
              group
            </span>
            {count} player{count === 1 ? "" : "s"}
          </h2>
          <span className="live-players-meta">
            {state.question_count} questions · {state.mode === "choice" ? "Name it" : "Find it"}
            {state.category_name ? ` · ${state.category_name}` : ""}
          </span>
        </header>

        {count === 0 ? (
          <p className="live-waiting">Waiting for players to join...</p>
        ) : (
          <ul className="live-player-chips">
            {state.players.map((p) => (
              <li key={p.id} className={p.away ? "is-away" : ""}>
                <span>{p.name}</span>
                <button type="button" aria-label={`Remove ${p.name}`} title="Remove" onClick={() => onRemove(p.id)}>
                  <span className="material-symbols-outlined" aria-hidden="true">
                    close
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <footer className="live-lobby-bar">
        <button type="button" className="live-ghost-button" onClick={onClose}>
          <span className="material-symbols-outlined" aria-hidden="true">
            close
          </span>
          Cancel
        </button>
        <button type="button" className={`live-ghost-button ${state.locked ? "is-on" : ""}`} onClick={onLock}>
          <span className="material-symbols-outlined" aria-hidden="true">
            {state.locked ? "lock" : "lock_open"}
          </span>
          {state.locked ? "Locked" : "Lock room"}
        </button>
        <button type="button" className="live-go-button" onClick={onStart} disabled={busy || count === 0}>
          Start
          <span className="material-symbols-outlined" aria-hidden="true">
            play_arrow
          </span>
        </button>
      </footer>
    </div>
  );
}

// --- a question, then its answer ----------------------------------------------------

function QuestionBoard({ state, now, busy, onNext }) {
  const q = state.question;
  const reveal = state.reveal;
  const clock = questionClock(state, now);
  const inverted = state.mode === "inverted";
  const counts = Object.fromEntries((reveal?.counts ?? []).map((c) => [c.id, c.count]));
  const most = Math.max(1, ...Object.values(counts));
  const total = state.players.length;

  if (!q) return null;

  return (
    <div className={`live-question ${inverted ? "is-inverted" : ""} ${reveal ? "is-revealed" : ""}`}>
      <header className="live-q-top">
        <span className="live-q-count">
          {state.position} / {state.question_count}
        </span>
        {reveal ? (
          <span className="live-q-status">
            {reveal.right_count} of {total} got it right
          </span>
        ) : (
          <span className="live-q-status">
            {clock.reading ? "Get ready..." : inverted ? "Find the photo" : "What is this?"}
          </span>
        )}
        <span className="live-q-answers">
          <strong>{state.answered_count}</strong>
          answer{state.answered_count === 1 ? "" : "s"}
        </span>
      </header>

      <section className="live-q-stage">
        {!reveal && <Countdown {...clock} />}
        {inverted ? (
          <div className="live-q-prompt">
            <span>Find the</span>
            <strong>{q.prompt}</strong>
          </div>
        ) : (
          <div className="live-q-photo">
            <img src={imageSrc(q.image_url)} alt="" draggable="false" />
          </div>
        )}
        {reveal && (
          <aside className="live-q-explain">
            <span className="live-q-explain-label">Answer</span>
            <strong>{reveal.item.name}</strong>
            {reveal.item.description && <p>{reveal.item.description}</p>}
          </aside>
        )}
      </section>

      <ul className={`live-options ${inverted ? "is-photos" : ""}`}>
        {q.choices.map((choice, i) => {
          const style = OPTION_STYLES[i];
          const isRight = reveal && choice.id === reveal.correct_id;
          const n = counts[choice.id] ?? 0;
          return (
            <li
              key={choice.id}
              className={`live-option is-${style.key} ${reveal ? (isRight ? "is-right" : "is-dim") : ""}`}
            >
              <Shape index={i} size={inverted ? 30 : 38} />
              {inverted ? (
                <img src={imageSrc(choice.image_url)} alt={`${style.label}`} draggable="false" />
              ) : (
                <span className="live-option-text">{choice.name}</span>
              )}
              {reveal && (
                <span className="live-option-count">
                  <span className="live-option-bar" style={{ width: `${(n / most) * 100}%` }} />
                  <span className="live-option-n">{n}</span>
                  {isRight && (
                    <span className="material-symbols-outlined" aria-label="Right answer">
                      check_circle
                    </span>
                  )}
                </span>
              )}
            </li>
          );
        })}
      </ul>

      <button type="button" className="live-next-button" onClick={onNext} disabled={busy}>
        {reveal ? "Standings" : "Skip"}
        <span className="material-symbols-outlined" aria-hidden="true">
          {reveal ? "leaderboard" : "skip_next"}
        </span>
      </button>
    </div>
  );
}

// --- standings ------------------------------------------------------------------------

function Scoreboard({ state, busy, onNext }) {
  const last = state.position >= state.question_count;
  return (
    <div className="live-scoreboard">
      <h1>Standings</h1>
      <ol className="live-ranks">
        {state.leaderboard.map((p, i) => (
          <li key={p.id} style={{ animationDelay: `${i * 90}ms` }}>
            <span className="live-rank-n">{i + 1}</span>
            <span className="live-rank-name">{p.name}</span>
            {p.streak >= 2 && (
              <span className="live-rank-streak" title="Right answers in a row">
                <span className="material-symbols-outlined" aria-hidden="true">
                  local_fire_department
                </span>
                {p.streak}
              </span>
            )}
            <span className="live-rank-score">{p.score}</span>
          </li>
        ))}
      </ol>
      <button type="button" className="live-next-button" onClick={onNext} disabled={busy}>
        {last ? "Final results" : "Next question"}
        <span className="material-symbols-outlined" aria-hidden="true">
          arrow_forward
        </span>
      </button>
    </div>
  );
}

function Podium({ state, onNew }) {
  const [first, second, third] = state.leaderboard;
  const rest = state.leaderboard.slice(3);
  const steps = [
    [second, 2, "is-second"],
    [first, 1, "is-first"],
    [third, 3, "is-third"],
  ];
  return (
    <div className="live-podium-page">
      <h1>Final results</h1>
      <div className="live-podium">
        {steps.map(([p, place, cls]) => (
          <div key={place} className={`live-step ${cls}`}>
            {p && (
              <>
                <span className="live-step-name">{p.name}</span>
                <span className="live-step-score">{p.score}</span>
              </>
            )}
            <div className="live-step-block">{place}</div>
          </div>
        ))}
      </div>
      {rest.length > 0 && (
        <ol className="live-ranks live-ranks-rest" start={4}>
          {rest.map((p, i) => (
            <li key={p.id}>
              <span className="live-rank-n">{i + 4}</span>
              <span className="live-rank-name">{p.name}</span>
              <span className="live-rank-score">{p.score}</span>
            </li>
          ))}
        </ol>
      )}
      {state.owned && (
        <p className="live-podium-saved">
          Results saved. <Link to="/live/history">See past games</Link>
        </p>
      )}
      <button type="button" className="live-go-button" onClick={onNew}>
        New game
      </button>
    </div>
  );
}

export default LiveHostPage;
