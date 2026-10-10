import { useRef, useState } from "react";

import { imageSrc, uploadImage } from "../api/client";
import { ErrorMessage } from "../components/StatusMessage";
import { useT } from "../i18n";
import { OPTION_STYLES } from "../live/game";
import { blankQuestion, TIME_LIMITS, TYPES } from "./model";

/** The selected question's fields; they change with its type. `onChange` gets the whole new question. */
function QuestionForm({ question: q, onChange, error }) {
  const t = useT();
  const set = (patch) => onChange({ ...q, ...patch });

  function changeType(type) {
    if (type === q.type) return;
    // Keep what carries over: the text, the picture and the time.
    onChange({ ...blankQuestion(type), text: q.text, image: q.image, time_limit: q.time_limit });
  }

  return (
    <div className="question-form">
      {error && <ErrorMessage error={error} />}
      <div className="option-row option-row-tight" role="group" aria-label={t("quizzes.form.type")}>
        {TYPES.map((type) => (
          <button
            key={type}
            type="button"
            className={`option-button option-button-small ${q.type === type ? "is-selected" : ""}`}
            aria-pressed={q.type === type}
            onClick={() => changeType(type)}
          >
            {t(`quizzes.type.${type}`)}
          </button>
        ))}
      </div>

      <label>
        {t("quizzes.form.text")}
        <textarea value={q.text} maxLength={300} onChange={(e) => set({ text: e.target.value })} />
      </label>

      <ImageField label={t("quizzes.form.image")} value={q.image} onChange={(image) => set({ image })} />

      <label>
        {t("quizzes.form.time")}
        <select value={q.time_limit} onChange={(e) => set({ time_limit: Number(e.target.value) })}>
          {TIME_LIMITS.map((s) => (
            <option key={s} value={s}>
              {t("quizzes.form.seconds", { n: s })}
            </option>
          ))}
        </select>
      </label>

      {q.type === "quiz" && <QuizOptions q={q} set={set} t={t} />}
      {q.type === "tf" && (
        <fieldset className="option-group">
          <legend className="option-legend">{t("quizzes.form.statementIs")}</legend>
          <div className="option-row option-row-tight">
            {[true, false].map((value) => (
              <button
                key={String(value)}
                type="button"
                className={`option-button option-button-small ${q.answer === value ? "is-selected" : ""}`}
                aria-pressed={q.answer === value}
                onClick={() => set({ answer: value })}
              >
                {value ? t("live.tf.true") : t("live.tf.false")}
              </button>
            ))}
          </div>
        </fieldset>
      )}
      {q.type === "type" && <AcceptedAnswers q={q} set={set} t={t} />}
      {q.type === "slider" && <SliderFields q={q} set={set} t={t} />}
    </div>
  );
}

function QuizOptions({ q, set, t }) {
  const setOption = (i, patch) => set({ options: q.options.map((o, j) => (j === i ? { ...o, ...patch } : o)) });
  return (
    <div className="question-options">
      {q.options.map((o, i) => (
        <div key={i} className={`question-option is-${OPTION_STYLES[i].key}`}>
          <input
            type="text"
            value={o.text}
            maxLength={75}
            aria-label={t("quizzes.form.answer", { n: i + 1 })}
            placeholder={t("quizzes.form.answer", { n: i + 1 })}
            onChange={(e) => setOption(i, { text: e.target.value })}
          />
          <div className="question-option-row">
            <label className="question-option-row">
              <input type="checkbox" checked={o.correct} onChange={(e) => setOption(i, { correct: e.target.checked })} />
              {t("quizzes.form.correct")}
            </label>
          </div>
          <ImageField value={o.image} onChange={(image) => setOption(i, { image })} small />
        </div>
      ))}
    </div>
  );
}

function AcceptedAnswers({ q, set, t }) {
  return (
    <fieldset className="option-group">
      <legend className="option-legend">{t("quizzes.form.accepted")}</legend>
      {q.accepted.map((a, i) => (
        <input
          key={i}
          type="text"
          value={a}
          maxLength={20}
          aria-label={t("quizzes.form.answer", { n: i + 1 })}
          onChange={(e) => set({ accepted: q.accepted.map((b, j) => (j === i ? e.target.value : b)) })}
        />
      ))}
      {q.accepted.length < 4 && (
        <button type="button" className="text-button" onClick={() => set({ accepted: [...q.accepted, ""] })}>
          {t("quizzes.form.addAccepted")}
        </button>
      )}
    </fieldset>
  );
}

function SliderFields({ q, set, t }) {
  const num = (key) => (
    <label key={key}>
      {t(`quizzes.form.${key === "answer" ? "value" : key}`)}
      <input
        type="number"
        value={q[key]}
        step="any"
        onChange={(e) => set({ [key]: e.target.value === "" ? "" : Number(e.target.value) })}
      />
    </label>
  );
  return (
    <div className="question-numbers">
      {["min", "max", "step", "answer", "tolerance"].map(num)}
      <label>
        {t("quizzes.form.unit")}
        <input type="text" value={q.unit} maxLength={10} onChange={(e) => set({ unit: e.target.value })} />
      </label>
    </div>
  );
}

/** Pick a picture from the device; it is uploaded straight away and its URL kept. */
function ImageField({ label, value, onChange, small = false }) {
  const t = useT();
  const input = useRef(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function pick(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      onChange((await uploadImage(file)).url);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="question-image">
      {label && !small && <span>{label}</span>}
      {value && <img src={imageSrc(value)} alt="" />}
      <input ref={input} type="file" accept="image/*" hidden onChange={pick} />
      <button type="button" className="text-button" disabled={busy} onClick={() => input.current?.click()}>
        {busy ? t("quizzes.form.uploading") : t("quizzes.form.addImage")}
      </button>
      {value && (
        <button type="button" className="text-button" onClick={() => onChange(null)}>
          {t("quizzes.form.removeImage")}
        </button>
      )}
      {error && <ErrorMessage error={error} />}
    </div>
  );
}

export default QuestionForm;
