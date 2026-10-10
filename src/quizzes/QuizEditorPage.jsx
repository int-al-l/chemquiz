import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { createQuiz, fetchMyQuiz, IS_DEMO, updateQuiz } from "../api/client";
import { useAuth } from "../auth/context";
import { rich, useLang, useT } from "../i18n";
import ImportPanel from "./ImportPanel";
import LibraryPicker from "./LibraryPicker";
import { blankQuestion, isBlank, move, tidy, TYPE_ICONS, TYPES } from "./model";
import QuestionForm from "./QuestionForm";

/**
 * Build or change a custom quiz: the questions on the left, the chosen one's
 * form on the right; add from scratch, from the library, or from a template.
 * Saved whole with one request; the server checks every question and names
 * the first one it refuses, which is then selected.
 */
function QuizEditorPage() {
  const { id } = useParams();
  const t = useT();
  const { user } = useAuth();

  if (IS_DEMO || !user) {
    return (
      <main className="setup-page">
        <div className="page-layout setup">
          <PageHeader title={t("quizzes.title")} backTo="/quizzes" />
          <p className="section-note">
            {IS_DEMO
              ? t("quizzes.demo")
              : rich(t("quizzes.signIn"), { signIn: <Link to="/sign-in">{t("common.signInLink")}</Link> })}
          </p>
        </div>
      </main>
    );
  }
  return <Editor key={id ?? "new"} id={id} />;
}

function Editor({ id }) {
  const t = useT();
  const navigate = useNavigate();
  const { lang: userLang } = useLang();

  const [quiz, setQuiz] = useState(id ? null : { title: "", lang: userLang, questions: [blankQuestion("quiz")] });
  const [loadError, setLoadError] = useState(null);
  const [selected, setSelected] = useState(0);
  const [panel, setPanel] = useState(null); // null | "library" | "import"
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null); // {message, question}

  useEffect(() => {
    if (!id) return undefined;
    let active = true;
    fetchMyQuiz(id)
      .then((q) => active && setQuiz({ title: q.title, lang: q.lang, questions: q.questions }))
      .catch((err) => active && setLoadError(err));
    return () => {
      active = false;
    };
  }, [id]);

  useEffect(() => {
    if (!dirty) return undefined;
    const warn = (e) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);

  if (loadError) return <ErrorMessage error={loadError} />;
  if (!quiz) return <Loading />;

  const questions = quiz.questions;
  const current = questions[Math.min(selected, questions.length - 1)];

  // Every change works on the quiz as it is when it lands, not as it was when
  // it started: uploads and imports finish while the teacher keeps typing.
  function change(update) {
    setQuiz((q) => ({ ...q, ...(typeof update === "function" ? update(q) : update) }));
    setDirty(true);
    setSaved(false);
  }
  const setQuestions = (update) => change((q) => ({ questions: update(q.questions) }));

  // The import panel stays open afterwards: it lists the rows it could not read.
  function append(list, { close = true } = {}) {
    if (!list.length) return;
    // A new quiz's untouched blank question gives way to what was added.
    const replacesBlank = questions.length === 1 && isBlank(questions[0]);
    setQuestions((qs) => (qs.length === 1 && isBlank(qs[0]) ? list : [...qs, ...list]));
    setSelected(replacesBlank ? 0 : questions.length);
    if (close) setPanel(null);
  }

  function remove(index) {
    setQuestions((qs) => {
      const next = qs.filter((_, i) => i !== index);
      return next.length ? next : [blankQuestion("quiz")];
    });
    setSelected(Math.max(0, Math.min(selected, questions.length - 2)));
  }

  async function save() {
    setSaving(true);
    setError(null);
    const body = { ...quiz, questions: questions.map(tidy) };
    try {
      const result = id ? await updateQuiz(id, body) : await createQuiz(body);
      setDirty(false);
      setSaved(true);
      if (!id) navigate(`/quizzes/${result.id}`, { replace: true });
    } catch (err) {
      const question = err.body?.question ?? null;
      setError({ message: err.message, question });
      if (question) setSelected(question - 1);
    } finally {
      setSaving(false);
    }
  }

  function back() {
    if (!dirty || window.confirm(t("quizzes.editor.unsaved"))) navigate("/quizzes");
  }

  const errorHere = error?.question === selected + 1 ? error : null;

  return (
    <main className="setup-page">
      <div className="page-layout">
        <PageHeader title={id ? quiz.title || t("quizzes.title") : t("quizzes.editor.newTitle")} onBack={back} />

        <div className="question-form">
          <label>
            {t("quizzes.editor.title")}
            <input type="text" value={quiz.title} maxLength={120} onChange={(e) => change({ title: e.target.value })} />
          </label>
          <div className="option-row option-row-tight" role="group" aria-label={t("quizzes.editor.lang")}>
            {["en", "ru"].map((code) => (
              <button
                key={code}
                type="button"
                className={`option-button option-button-small ${quiz.lang === code ? "is-selected" : ""}`}
                aria-pressed={quiz.lang === code}
                onClick={() => change({ lang: code })}
              >
                {t(`live.setup.lang.${code}`)}
              </button>
            ))}
          </div>
        </div>

        <div className="quiz-actions">
          {TYPES.map((type) => (
            <button key={type} type="button" className="secondary-button" onClick={() => append([blankQuestion(type)])}>
              + {t(`quizzes.type.${type}`)}
            </button>
          ))}
          <button type="button" className="secondary-button" onClick={() => setPanel(panel === "library" ? null : "library")}>
            {t("quizzes.editor.fromLibrary")}
          </button>
          <button type="button" className="secondary-button" onClick={() => setPanel(panel === "import" ? null : "import")}>
            {t("quizzes.editor.import")}
          </button>
        </div>

        {panel === "library" && <LibraryPicker lang={quiz.lang} onAdd={append} />}
        {panel === "import" && <ImportPanel onAdd={(list) => append(list, { close: false })} />}

        <div className="quiz-editor">
          <ol className="quiz-editor-list">
            {questions.map((q, i) => (
              <li key={i}>
                <button
                  type="button"
                  className={`quiz-editor-item ${i === selected ? "is-selected" : ""} ${error?.question === i + 1 ? "has-error" : ""}`}
                  onClick={() => setSelected(i)}
                >
                  <span className="material-symbols-outlined" aria-hidden="true">
                    {TYPE_ICONS[q.type]}
                  </span>
                  {i + 1}. {q.text || t("quizzes.editor.untitled")}
                </button>
                <button type="button" className="quiz-icon-button" disabled={i === 0} aria-label={t("quizzes.editor.up")}
                  onClick={() => { setQuestions((qs) => move(qs, i, -1)); setSelected(i - 1); }}>
                  ↑
                </button>
                <button type="button" className="quiz-icon-button" disabled={i === questions.length - 1}
                  aria-label={t("quizzes.editor.down")}
                  onClick={() => { setQuestions((qs) => move(qs, i, 1)); setSelected(i + 1); }}>
                  ↓
                </button>
                <button type="button" className="quiz-icon-button" aria-label={t("quizzes.editor.remove")} onClick={() => remove(i)}>
                  ×
                </button>
              </li>
            ))}
          </ol>

          <QuestionForm
            question={current}
            error={errorHere}
            onChange={(update) => {
              const index = selected; // the question the update was made for
              setQuestions((qs) => qs.map((old, i) => (i === index ? update(old) : old)));
            }}
          />
        </div>

        {error && !error.question && <ErrorMessage error={error} />}
        <button type="button" className="primary-button" onClick={save} disabled={saving}>
          {saving ? t("quizzes.editor.saving") : saved ? t("quizzes.editor.saved") : t("quizzes.editor.save")}
        </button>
      </div>
    </main>
  );
}

export default QuizEditorPage;
