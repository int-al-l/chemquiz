import { useCallback } from "react";
import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { deleteQuiz, fetchQuizzes, IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { useApi } from "../hooks/useApi";
import { rich, useT } from "../i18n";

/** A teacher's own quizzes: make one, change it, play it, or take it to class. */
function MyQuizzesPage() {
  const t = useT();
  const { user } = useAuth();

  return (
    <main className="setup-page">
      <div className="page-layout setup">
        <PageHeader title={t("quizzes.title")} backTo="/" />
        <section className="setup-content">
          {IS_DEMO ? (
            <p className="section-note">{t("quizzes.demo")}</p>
          ) : !user ? (
            <p className="section-note">
              {rich(t("quizzes.signIn"), { signIn: <Link to="/sign-in">{t("common.signInLink")}</Link> })}
            </p>
          ) : (
            <QuizList t={t} />
          )}
        </section>
      </div>
    </main>
  );
}

function QuizList({ t }) {
  const loader = useCallback(() => fetchQuizzes(), []);
  const { data: quizzes, error, loading, reload } = useApi(loader);

  async function remove(quiz) {
    if (!window.confirm(t("quizzes.confirmDelete", { title: quiz.title }))) return;
    await deleteQuiz(quiz.id);
    reload();
  }

  return (
    <>
      <p className="setup-lead">{t("quizzes.lead")}</p>
      <Link className="primary-button" to="/quizzes/new">
        {t("quizzes.create")}
      </Link>
      {loading && <Loading />}
      {error && <ErrorMessage error={error} onRetry={reload} />}
      {quizzes && quizzes.length === 0 && <EmptyMessage>{t("quizzes.empty")}</EmptyMessage>}
      {quizzes && quizzes.length > 0 && (
        <ul className="quiz-list">
          {quizzes.map((quiz) => (
            <li key={quiz.id}>
              <span className="quiz-list-title">
                {quiz.title}
                <span className="option-note"> · {t("quizzes.questions", { n: quiz.question_count })}</span>
              </span>
              <Link className="secondary-button" to={`/live?quiz=${quiz.id}`}>
                {t("quizzes.host")}
              </Link>
              <Link className="secondary-button" to={`/quizzes/${quiz.id}/play`}>
                {t("quizzes.playSolo")}
              </Link>
              <Link className="text-button" to={`/quizzes/${quiz.id}`}>
                {t("quizzes.edit")}
              </Link>
              <button type="button" className="text-button" onClick={() => remove(quiz)}>
                {t("quizzes.delete")}
              </button>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

export default MyQuizzesPage;
