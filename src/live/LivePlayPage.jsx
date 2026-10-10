import { useEffect, useRef, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";

import { ErrorMessage } from "../components/StatusMessage";
import { fetchLivePlayer, imageSrc, IS_DEMO, liveAnswer } from "../api/client";
import { rich, useLang, useT } from "../i18n";
import { LanguageScope } from "../i18n/LanguageProvider";
import { useProgress } from "../progress/context";
import AnswerInput from "../quizzes/AnswerInput";
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
    if (!state.reveal.item) return; // a custom question: not a card, nothing to learn into
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

  // `given` is {choice_id}, {text} or {value}, whichever the question asks for.
  async function send(given) {
    if (!state || picked?.position === state.position || state.you.answered) return;
    setPicked({ position: state.position, id: given.choice_id ?? -1 });
    setAnswerError(null);
    if (navigator.vibrate) navigator.vibrate(30);
    try {
      apply(
        await liveAnswer(pin, token, {
          position: state.position,
          choiceId: given.choice_id,
          text: given.text,
          value: given.value,
        }),
      );
    } catch (err) {
      setPicked(null);
      setAnswerError(err);
    }
  }

  return (
    <LanguageScope lang={state?.lang}>
      <PlayScreen
        pin={pin}
        token={token}
        state={state}
        error={error}
        status={status}
        now={now}
        picked={picked}
        answerError={answerError}
        send={send}
      />
    </LanguageScope>
  );
}

/** The phone's texts, drawn inside the game's language scope. */
function PlayScreen({ pin, token, state, error, status, now, picked, answerError, send }) {
  const t = useT();
  const { lang } = useLang();
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
          <h1>{status === 410 ? t("live.play.removed") : t("live.play.ended")}</h1>
          <p>{status === 410 ? t("live.play.removedText") : t("live.play.thanks")}</p>
          <Link className="primary-button live-inline-button" to="/join">
            {t("live.play.joinAnother")}
          </Link>
          <Link className="text-button" to="/">
            {t("live.play.home")}
          </Link>
        </div>
      </main>
    );
  }

  if (!state) {
    return (
      <main className="live-phone live-phone-center">
        {error ? <ErrorMessage error={error} /> : <p className="status-message">{t("live.play.connecting")}</p>}
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

      {error && <div className="live-offline">{t("live.play.reconnecting")}</div>}

      {state.phase === "lobby" && (
        <section className="live-phone-card">
          <span className="live-phone-big material-symbols-outlined" aria-hidden="true">
            check_circle
          </span>
          <h1>{t("live.play.in")}</h1>
          <p>{t("live.play.lookAtBoard")}</p>
          <p className="live-phone-muted">
            {t("live.play.soFar", { n: state.player_count })}
          </p>
        </section>
      )}

      {state.phase === "question" && (
        <PhoneQuestion
          t={t}
          state={state}
          now={now}
          picked={picked?.position === state.position ? picked.id : you.answered ? you.answered_id : null}
          onPick={send}
          error={answerError}
        />
      )}

      {state.phase === "reveal" && <PhoneResult state={state} t={t} lang={lang} />}

      {state.phase === "scoreboard" && (
        <section className="live-phone-card">
          <span className="live-phone-rank">{ordinal(you.rank, lang)}</span>
          <h1>{t("live.play.place")}</h1>
          <p>
            {you.streak >= 2
              ? t("live.play.pointsStreak", { n: you.score, streak: you.streak })
              : t("live.play.points", { n: you.score })}
          </p>
          <p className="live-phone-muted">{t("live.play.nextSoon")}</p>
        </section>
      )}

      {state.phase === "finished" && (
        <section className={`live-phone-card ${you.rank <= 3 ? "is-medal" : ""}`}>
          <span className="live-phone-big material-symbols-outlined" aria-hidden="true">
            {you.rank <= 3 ? "workspace_premium" : "flag"}
          </span>
          <h1>{t("live.play.finished", { place: ordinal(you.rank, lang) })}</h1>
          <p>{t("live.play.points", { n: you.score })}</p>
          <Link className="primary-button live-inline-button" to="/">
            {t("live.play.done")}
          </Link>
        </section>
      )}
    </main>
  );
}

function PhoneQuestion({ t, state, now, picked, onPick, error }) {
  const q = state.question;
  const clock = questionClock(state, now);
  const inverted = state.mode === "inverted";

  if (!q) return null;

  if (clock.reading) {
    return (
      <section className="live-phone-card">
        <p className="live-phone-muted">{t("live.play.question", { n: state.position })}</p>
        <span className="live-phone-rank">{clock.left}</span>
        <h1>{t("live.play.getReady")}</h1>
      </section>
    );
  }

  if (picked != null) {
    const index = q.choices ? q.choices.findIndex((c) => c.id === picked) : -1;
    if (index < 0) {
      // A typed or slider answer: no colour to echo back.
      return (
        <section className="live-phone-card live-phone-sent">
          <h1>{t("live.play.sent")}</h1>
          <p>{t("live.play.waiting")}</p>
        </section>
      );
    }
    const style = OPTION_STYLES[index];
    return (
      <section className={`live-phone-card live-phone-sent is-${style.key}`}>
        <Shape index={Math.max(index, 0)} size={72} />
        <h1>{t("live.play.sent")}</h1>
        <p>{t("live.play.waiting")}</p>
      </section>
    );
  }

  if (clock.left === 0) {
    return (
      <section className="live-phone-card">
        <h1>{t("live.play.timeUp")}</h1>
      </section>
    );
  }

  if (state.mode === "custom") {
    return (
      <section className="live-phone-question is-custom">
        <div className="live-phone-timer" aria-hidden="true">
          <span style={{ width: `${clock.fraction * 100}%` }} />
        </div>
        {q.prompt && <p className="live-phone-prompt">{q.prompt}</p>}
        {q.image_url && <img className="live-phone-photo" src={imageSrc(q.image_url)} alt="" draggable="false" />}
        {error && <ErrorMessage error={error} />}
        <AnswerInput question={q} onAnswer={onPick} />
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
          {rich(t("live.play.findThe", { name: "{name}" }), { name: <strong>{q.prompt}</strong> })}
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
              onClick={() => onPick({ choice_id: choice.id })}
              aria-label={inverted ? t(`live.shape.${style.key}`) : choice.name}
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

function PhoneResult({ state, t, lang }) {
  const { you, reveal } = state;
  const result = you.result ?? { answered: false, correct: false, points: 0 };
  const kind = !result.answered ? "is-missed" : result.correct ? "is-right" : "is-wrong";
  return (
    <section className={`live-phone-result ${kind}`}>
      <span className="live-phone-big material-symbols-outlined" aria-hidden="true">
        {!result.answered ? "timer_off" : result.correct ? "check_circle" : "cancel"}
      </span>
      <h1>{!result.answered ? t("live.play.timeUp") : result.correct ? t("live.play.correct") : t("live.play.wrong")}</h1>
      {result.correct && <p className="live-phone-points">+{result.points}</p>}
      {result.correct && you.streak >= 2 && (
        <p className="live-phone-streak">
          <span className="material-symbols-outlined" aria-hidden="true">
            local_fire_department
          </span>
          {t("live.play.inARow", { n: you.streak })}
        </p>
      )}
      {!result.correct && reveal?.item && <p>{t("live.play.itWas", { name: reveal.item.name })}</p>}
      {!result.correct && !reveal?.item && reveal?.answer_text && (
        <p>{t("live.play.itWasAnswer", { answer: reveal.answer_text })}</p>
      )}
      <p className="live-phone-place">{t("live.play.youAre", { place: ordinal(you.rank, lang) })}</p>
    </section>
  );
}

export default LivePlayPage;
