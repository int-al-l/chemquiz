import { useEffect, useRef, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";

import { ErrorMessage } from "../components/StatusMessage";
import { fetchLivePlayer, imageSrc, IS_DEMO, liveAnswer } from "../api/client";
import { useProgress } from "../progress/context";
import { DemoNotice, Shape } from "./components";
import { OPTION_STYLES, ordinal, playerToken, questionClock, savePlayerToken, useLivePoll, useServerNow } from "./game";

/**
 * A student's phone during a class game: a controller, not a second board.
 * It shows four big buttons while a question is open and, afterwards, whether
 * they were right, what they scored and where they stand.
 *
 * Right and wrong answers also count towards the player's own XP and spaced
 * repetition, the same as a solo quiz.
 */
function LivePlayPage() {
  const { pin } = useParams();
  const token = playerToken(pin);
  const progress = useProgress();

  const { state, error, apply, offset } = useLivePoll(
    () => fetchLivePlayer(pin, token),
    1000,
    Boolean(token) && !IS_DEMO,
  );
  const now = useServerNow(offset, state?.phase === "question");
  const [picked, setPicked] = useState(null); // {position, id} while the answer is on its way
  const [answerError, setAnswerError] = useState(null);

  // Credit each revealed question to the player's own progress, once.
  const credited = useRef(new Set());
  const correctSoFar = useRef(0);
  useEffect(() => {
    if (!state?.reveal || !state.you.result) return;
    const key = state.position;
    if (credited.current.has(key)) return;
    credited.current.add(key);
    if (!state.you.result.answered) return;
    if (state.you.result.correct) correctSoFar.current += 1;
    progress.quizAnswer(state.reveal.item.slug, state.you.result.correct, state.you.streak);
  }, [state, progress]);
  const finishedCredited = useRef(false);
  useEffect(() => {
    if (state?.phase !== "finished" || finishedCredited.current || credited.current.size === 0) return;
    finishedCredited.current = true;
    progress.quizFinished({ correct: correctSoFar.current, total: state.question_count });
  }, [state, progress]);

  const status = error?.status;
  useEffect(() => {
    if (status === 404 || status === 410) savePlayerToken(pin, null);
  }, [status, pin]);

  async function send(choiceId) {
    if (!state || picked?.position === state.position || state.you.answered_id) return;
    setPicked({ position: state.position, id: choiceId });
    setAnswerError(null);
    if (navigator.vibrate) navigator.vibrate(30);
    try {
      apply(await liveAnswer(pin, token, { position: state.position, choiceId }));
    } catch (err) {
      setPicked(null);
      setAnswerError(err);
    }
  }

  if (IS_DEMO) {
    return (
      <main className="live-phone">
        <DemoNotice />
      </main>
    );
  }

  if (!token || status === 403) return <Navigate to={`/join/${pin}`} replace />;

  if (status === 404 || status === 410) {
    return (
      <main className="live-phone live-phone-center">
        <div className="live-message">
          <h1>{status === 410 ? "You were removed" : "The game has ended"}</h1>
          <p>{status === 410 ? "The host removed you from this game." : "Thanks for playing!"}</p>
          <Link className="primary-button live-inline-button" to="/join">
            Join another game
          </Link>
          <Link className="text-button" to="/">
            Home
          </Link>
        </div>
      </main>
    );
  }

  if (!state) {
    return (
      <main className="live-phone live-phone-center">
        {error ? <ErrorMessage error={error} /> : <p className="status-message">Connecting...</p>}
      </main>
    );
  }

  const you = state.you;

  return (
    <main className={`live-phone phase-${state.phase}`}>
      <header className="live-phone-top">
        <span className="live-phone-name">{you.name}</span>
        {state.position > 0 && (
          <span className="live-phone-count">
            {state.position}/{state.question_count}
          </span>
        )}
        <span className="live-phone-score">{you.score}</span>
      </header>

      {error && <div className="live-offline">Reconnecting...</div>}

      {state.phase === "lobby" && (
        <section className="live-phone-card">
          <span className="live-phone-big material-symbols-outlined" aria-hidden="true">
            check_circle
          </span>
          <h1>You're in!</h1>
          <p>Look at the board. The game starts soon.</p>
          <p className="live-phone-muted">
            {state.player_count} player{state.player_count === 1 ? "" : "s"} so far
          </p>
        </section>
      )}

      {state.phase === "question" && (
        <PhoneQuestion
          state={state}
          now={now}
          picked={picked?.position === state.position ? picked.id : you.answered_id}
          onPick={send}
          error={answerError}
        />
      )}

      {state.phase === "reveal" && <PhoneResult state={state} />}

      {state.phase === "scoreboard" && (
        <section className="live-phone-card">
          <span className="live-phone-rank">{ordinal(you.rank)}</span>
          <h1>place</h1>
          <p>
            {you.score} points{you.streak >= 2 ? ` · ${you.streak} in a row` : ""}
          </p>
          <p className="live-phone-muted">Next question coming up...</p>
        </section>
      )}

      {state.phase === "finished" && (
        <section className={`live-phone-card ${you.rank <= 3 ? "is-medal" : ""}`}>
          <span className="live-phone-big material-symbols-outlined" aria-hidden="true">
            {you.rank <= 3 ? "workspace_premium" : "flag"}
          </span>
          <h1>You finished {ordinal(you.rank)}</h1>
          <p>{you.score} points</p>
          <Link className="primary-button live-inline-button" to="/">
            Done
          </Link>
        </section>
      )}
    </main>
  );
}

function PhoneQuestion({ state, now, picked, onPick, error }) {
  const q = state.question;
  const clock = questionClock(state, now);
  const inverted = state.mode === "inverted";

  if (!q) return null;

  if (clock.reading) {
    return (
      <section className="live-phone-card">
        <p className="live-phone-muted">Question {state.position}</p>
        <span className="live-phone-rank">{clock.left}</span>
        <h1>Get ready</h1>
      </section>
    );
  }

  if (picked != null) {
    const index = q.choices.findIndex((c) => c.id === picked);
    const style = OPTION_STYLES[index] ?? OPTION_STYLES[0];
    return (
      <section className={`live-phone-card live-phone-sent is-${style.key}`}>
        <Shape index={Math.max(index, 0)} size={72} />
        <h1>Answer sent</h1>
        <p>Waiting for the others...</p>
      </section>
    );
  }

  if (clock.left === 0) {
    return (
      <section className="live-phone-card">
        <h1>Time's up</h1>
      </section>
    );
  }

  return (
    <section className={`live-phone-question ${inverted ? "is-inverted" : ""}`}>
      <div className="live-phone-timer" aria-hidden="true">
        <span style={{ width: `${clock.fraction * 100}%` }} />
      </div>
      {inverted ? (
        <p className="live-phone-prompt">
          Find the <strong>{q.prompt}</strong>
        </p>
      ) : (
        q.image_url && <img className="live-phone-photo" src={imageSrc(q.image_url)} alt="" draggable="false" />
      )}
      {error && <ErrorMessage error={error} />}
      <div className="live-phone-options">
        {q.choices.map((choice, i) => {
          const style = OPTION_STYLES[i];
          return (
            <button
              key={choice.id}
              type="button"
              className={`live-phone-option is-${style.key}`}
              onClick={() => onPick(choice.id)}
              aria-label={inverted ? style.label : choice.name}
            >
              <Shape index={i} size={inverted ? 22 : 28} />
              {inverted ? (
                <img src={imageSrc(choice.image_url)} alt="" draggable="false" />
              ) : (
                <span>{choice.name}</span>
              )}
            </button>
          );
        })}
      </div>
    </section>
  );
}

function PhoneResult({ state }) {
  const { you, reveal } = state;
  const result = you.result ?? { answered: false, correct: false, points: 0 };
  const kind = !result.answered ? "is-missed" : result.correct ? "is-right" : "is-wrong";
  return (
    <section className={`live-phone-result ${kind}`}>
      <span className="live-phone-big material-symbols-outlined" aria-hidden="true">
        {!result.answered ? "timer_off" : result.correct ? "check_circle" : "cancel"}
      </span>
      <h1>{!result.answered ? "Time's up" : result.correct ? "Correct!" : "Not quite"}</h1>
      {result.correct && <p className="live-phone-points">+{result.points}</p>}
      {result.correct && you.streak >= 2 && (
        <p className="live-phone-streak">
          <span className="material-symbols-outlined" aria-hidden="true">
            local_fire_department
          </span>
          {you.streak} in a row
        </p>
      )}
      {!result.correct && reveal && <p>It was the {reveal.item.name}</p>}
      <p className="live-phone-place">You're {ordinal(you.rank)}</p>
    </section>
  );
}

export default LivePlayPage;
