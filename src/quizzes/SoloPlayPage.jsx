import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { imageSrc, IS_DEMO, playQuiz } from "../api/client";
import { useApi } from "../hooks/useApi";
import { useT } from "../i18n";
import AnswerInput from "./AnswerInput";
import { answerText, grade } from "./grade";

/**
 * Play your own quiz alone: one question at a time against its clock, right
 * or wrong straight after, the score at the end. Graded here in the browser
 * (grade.js): it is the author's own quiz, so there is nothing to keep secret.
 * Does not count towards XP or card progress, which belong to the library.
 */
function SoloPlayPage() {
  const { id } = useParams();
  const t = useT();
  const loader = useCallback(() => playQuiz(id), [id]);
  const { data, error, loading, reload } = useApi(loader, [id]);

  if (IS_DEMO) return <p className="section-note">{t("quizzes.demo")}</p>;
  return (
    <main className="live-phone solo-play">
      <PageHeader title={data?.title ?? t("quizzes.title")} backTo="/quizzes" />
      {loading && <Loading />}
      {error && <ErrorMessage error={error} onRetry={reload} />}
      {data && <Run key={data.id} quiz={data} t={t} />}
    </main>
  );
}

function Run({ quiz, t }) {
  const [index, setIndex] = useState(0);
  const [right, setRight] = useState(0);
  const [answered, setAnswered] = useState(null); // {correct} once answered
  const [left, setLeft] = useState(quiz.questions[0].time_limit);
  const q = quiz.questions[index];
  const done = index >= quiz.questions.length;
  // Running out of time is an answer too: derived, not stored.
  const result = answered ?? (left <= 0 ? { correct: false, timedOut: true } : null);

  const ticking = !done && !result;

  useEffect(() => {
    if (!ticking) return undefined;
    const timer = setTimeout(() => setLeft((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [left, ticking]);

  function answer(given) {
    if (result) return;
    const correct = grade(q, given);
    if (correct) setRight((n) => n + 1);
    setAnswered({ correct, timedOut: false });
  }

  function next() {
    const n = index + 1;
    setIndex(n);
    setAnswered(null);
    if (n < quiz.questions.length) setLeft(quiz.questions[n].time_limit);
  }

  function again() {
    setIndex(0);
    setRight(0);
    setAnswered(null);
    setLeft(quiz.questions[0].time_limit);
  }

  if (done) {
    return (
      <section className="live-phone-card">
        <h1>{t("quizzes.play.done", { right, total: quiz.questions.length })}</h1>
        <button type="button" className="primary-button live-inline-button" onClick={again}>
          {t("quizzes.play.again")}
        </button>
        <Link className="text-button" to="/quizzes">
          {t("quizzes.play.backToList")}
        </Link>
      </section>
    );
  }

  const answerWords = answerText(q);
  return (
    <section className="live-phone-question is-custom">
      <p className="live-phone-muted">{t("quizzes.play.question", { n: index + 1, total: quiz.questions.length })}</p>
      {!result && (
        <div className="live-phone-timer" aria-hidden="true">
          <span style={{ width: `${(left / q.time_limit) * 100}%` }} />
        </div>
      )}
      {q.prompt && <p className="live-phone-prompt">{q.prompt}</p>}
      {q.image_url && <img className="live-phone-photo" src={imageSrc(q.image_url)} alt="" draggable="false" />}
      {result ? (
        <div className={`solo-feedback live-phone-result ${result.correct ? "is-right" : "is-wrong"}`}>
          <h1>
            {result.timedOut ? t("quizzes.play.timeUp") : result.correct ? t("quizzes.play.right") : t("quizzes.play.wrong")}
          </h1>
          {!result.correct && answerWords && <p>{t("quizzes.play.itWas", { answer: answerWords })}</p>}
          <button type="button" className="primary-button live-inline-button" onClick={next}>
            {t("quizzes.play.next")}
          </button>
        </div>
      ) : (
        <AnswerInput key={index} question={q} onAnswer={answer} />
      )}
    </section>
  );
}

export default SoloPlayPage;
