import { useCallback, useEffect, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import BottomSheet from "../components/BottomSheet";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchQuiz, imageSrc, submitAnswer } from "../api/client";
import { useApi } from "../hooks/useApi";
import { useProgress } from "../progress/context";
import { useSaved } from "../saved/context";

/**
 * Playing a quiz, laid out to fit one phone screen: a slim top bar, the
 * question filling the middle, and a bottom bar that always holds the Next
 * button -- nothing to scroll to. The explanation of an answer opens in a
 * sheet from the bottom ("Why?") instead of pushing the button off screen.
 *
 * Two modes:
 *   choice    a photograph and four names
 *   inverted  a name and four photographs
 *
 * The session lives on the server, so a refresh resumes at the first
 * unanswered question. Answers are graded by the backend.
 */
function QuizPage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const progress = useProgress();
  const { has, toggle } = useSaved();

  const loader = useCallback(() => fetchQuiz(token), [token]);
  const { data: session, error, loading, reload } = useApi(loader, [token]);

  const [cursor, setCursor] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [answerError, setAnswerError] = useState(null);
  const [combo, setCombo] = useState(0);
  const [xp, setXp] = useState(0);
  const [bestCombo, setBestCombo] = useState(0);
  const [sheetOpen, setSheetOpen] = useState(false);

  const firstUnanswered = session?.questions.find((q) => !q.answered)?.position ?? null;
  const position = cursor ?? firstUnanswered;
  const question = session?.questions.find((q) => q.position === position);
  const answered = Boolean(feedback);

  async function send(choiceId) {
    if (submitting || answered) return;
    setSubmitting(true);
    setAnswerError(null);
    try {
      const result = await submitAnswer(token, { position, choiceId });
      const nextCombo = result.is_correct ? combo + 1 : 0;
      let gained = progress.quizAnswer(result.correct_item.slug, result.is_correct, nextCombo);
      if (result.is_complete) {
        gained += progress.quizFinished({
          correct: result.correct_count,
          total: session.question_count,
        });
      }
      setCombo(nextCombo);
      setBestCombo((b) => Math.max(b, nextCombo));
      setXp((x) => x + gained);
      setFeedback(result);
    } catch (err) {
      setAnswerError(err);
    } finally {
      setSubmitting(false);
    }
  }

  function handleNext() {
    if (!feedback) return;
    const wasLast = feedback.is_complete;
    setFeedback(null);
    setSheetOpen(false);
    setAnswerError(null);
    if (wasLast) {
      navigate(`/quiz/${token}/results`, { replace: true, state: { xp, bestCombo } });
    } else {
      setCursor(position + 1);
    }
  }

  // 1-4 pick an option, Enter or → moves on.
  useEffect(() => {
    function onKey(event) {
      if (!question) return;
      if (sheetOpen && event.key !== "Enter") return;
      const n = Number(event.key);
      if (!answered && n >= 1 && n <= question.choices.length) {
        send(question.choices[n - 1].id);
      } else if (answered && (event.key === "Enter" || event.key === "ArrowRight")) {
        event.preventDefault();
        handleNext();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (loading || (!question && !error && !(session && firstUnanswered === null))) {
    return (
      <main className="quiz-screen">
        <Loading />
      </main>
    );
  }

  if (error) {
    return (
      <main className="quiz-screen">
        <ErrorMessage error={error} onRetry={reload} />
      </main>
    );
  }

  if (session && firstUnanswered === null && !feedback) {
    return <Navigate to={`/quiz/${token}/results`} replace />;
  }

  const inverted = session.mode === "inverted";
  const correctId = feedback?.correct_choice_id;
  const pickedId = feedback?.given_choice_id;
  const item = feedback?.correct_item;

  const stateOf = (choiceId) => {
    if (!answered) return "";
    if (choiceId === correctId) return "is-correct";
    if (choiceId === pickedId) return "is-wrong";
    return "is-dim";
  };

  return (
    <main className={`quiz-screen ${inverted ? "is-inverted" : ""}`}>
      <header className="quiz-top">
        <button className="icon-button" onClick={() => navigate("/")} aria-label="Leave the quiz" type="button">
          <span className="material-symbols-outlined">close</span>
        </button>
        <div
          className="quiz-progress-bar"
          role="progressbar"
          aria-valuenow={position}
          aria-valuemin={1}
          aria-valuemax={session.question_count}
          aria-label={`Question ${position} of ${session.question_count}`}
        >
          <div
            className="quiz-progress-fill"
            style={{ width: `${((position - (answered ? 0 : 1)) / session.question_count) * 100}%` }}
          />
        </div>
        <span className="quiz-count">
          {position}/{session.question_count}
        </span>
        <span className={`combo-pill ${combo >= 2 ? "is-hot" : ""}`} title="Correct in a row">
          <span className="material-symbols-outlined" aria-hidden="true">local_fire_department</span>
          {combo}
        </span>
      </header>

      {inverted ? (
        <section className="quiz-stage">
          <div className="quiz-prompt">
            <span className="quiz-prompt-label">Find the</span>
            <span className="quiz-prompt-name">{question.prompt}</span>
          </div>
          <div className="photo-options">
            {question.choices.map((choice, i) => (
              <button
                key={choice.id}
                className={`photo-option ${stateOf(choice.id)}`}
                onClick={() => send(choice.id)}
                disabled={answered || submitting}
                aria-label={`Photo ${i + 1}`}
                type="button"
              >
                <img src={imageSrc(choice.image_url)} alt="" draggable="false" />
                <span className="option-key" aria-hidden="true">{i + 1}</span>
                {answered && choice.id === correctId && (
                  <span className="photo-option-mark material-symbols-outlined" aria-hidden="true">check_circle</span>
                )}
                {answered && choice.id === pickedId && choice.id !== correctId && (
                  <span className="photo-option-mark is-wrong material-symbols-outlined" aria-hidden="true">cancel</span>
                )}
              </button>
            ))}
          </div>
        </section>
      ) : (
        <section className="quiz-stage">
          <div className="quiz-photo">
            <img src={imageSrc(question.image_url)} alt="Name this piece of glassware" draggable="false" />
          </div>
          <div className="name-options">
            {question.choices.map((choice, i) => (
              <button
                key={choice.id}
                className={`name-option ${stateOf(choice.id)}`}
                onClick={() => send(choice.id)}
                disabled={answered || submitting}
                type="button"
              >
                <span className="option-key" aria-hidden="true">{i + 1}</span>
                <span className="name-option-text">{choice.name}</span>
                {answered && choice.id === correctId && (
                  <span className="material-symbols-outlined" aria-hidden="true">check</span>
                )}
                {answered && choice.id === pickedId && choice.id !== correctId && (
                  <span className="material-symbols-outlined" aria-hidden="true">close</span>
                )}
              </button>
            ))}
          </div>
        </section>
      )}

      <footer className={`quiz-bottom ${answered ? (feedback.is_correct ? "is-correct" : "is-wrong") : ""}`}>
        {answerError && <ErrorMessage error={answerError} />}
        <div className="quiz-verdict" role="status">
          {answered ? (
            <>
              <span className="verdict-icon material-symbols-outlined" aria-hidden="true">
                {feedback.is_correct ? "check_circle" : "cancel"}
              </span>
              <span className="verdict-text">
                <strong>
                  {feedback.is_correct
                    ? combo >= 3
                      ? `${combo} in a row!`
                      : "Correct!"
                    : "Not quite"}
                </strong>
                <span className="verdict-answer">{item.name}</span>
              </span>
              <button className="why-button" onClick={() => setSheetOpen(true)} type="button">
                <span className="material-symbols-outlined" aria-hidden="true">info</span>
                Why?
              </button>
            </>
          ) : (
            <span className="verdict-hint">
              {inverted ? "Tap the matching photo" : "Tap the right name"}
            </span>
          )}
        </div>
        <button className="next-button" onClick={handleNext} disabled={!answered} type="button">
          {feedback?.is_complete ? "See results" : "Next"}
          <span className="material-symbols-outlined" aria-hidden="true">arrow_forward</span>
        </button>
      </footer>

      <BottomSheet open={sheetOpen} onClose={() => setSheetOpen(false)} title={item?.name ?? ""}>
        {item && (
          <div className="why-body">
            {item.image_url && <img className="why-photo" src={imageSrc(item.image_url)} alt="" />}
            <p>{item.description ?? "No description yet."}</p>
            <button
              className={`secondary-button ${has(item.slug) ? "is-on" : ""}`}
              onClick={() => toggle(item.slug)}
              type="button"
            >
              <span className="material-symbols-outlined" aria-hidden="true">
                {has(item.slug) ? "star" : "star_outline"}
              </span>
              {has(item.slug) ? "In my list" : "Save to my list"}
            </button>
          </div>
        )}
      </BottomSheet>
    </main>
  );
}

export default QuizPage;
