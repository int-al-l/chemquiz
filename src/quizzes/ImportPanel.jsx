import { useState } from "react";

import { importQuiz } from "../api/client";
import { ErrorMessage } from "../components/StatusMessage";
import { useT } from "../i18n";

const TEMPLATES = `${import.meta.env.BASE_URL}templates/chemquiz-template`;

/** Download a template, fill it in, upload it: the questions are appended to the editor. */
function ImportPanel({ onAdd }) {
  const t = useT();
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function upload(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const res = await importQuiz(file);
      onAdd(res.questions);
      setResult(res);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="quiz-panel">
      <p>{t("quizzes.import.lead")}</p>
      <div className="quiz-actions">
        <a className="secondary-button" href={`${TEMPLATES}.xlsx`} download>
          {t("quizzes.import.excel")}
        </a>
        <a className="secondary-button" href={`${TEMPLATES}.docx`} download>
          {t("quizzes.import.word")}
        </a>
        <label className="primary-button">
          {t("quizzes.import.choose")}
          <input type="file" accept=".xlsx,.docx" hidden disabled={busy} onChange={upload} />
        </label>
      </div>
      {error && <ErrorMessage error={error} />}
      {result && <p>{t("quizzes.import.added", { n: result.questions.length })}</p>}
      {result?.errors.length > 0 && (
        <ul className="quiz-errors">
          {result.errors.map((e) => (
            <li key={e.row}>{t("quizzes.import.row", e)}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default ImportPanel;
