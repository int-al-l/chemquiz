import { useState } from "react";

import { imageSrc } from "../api/client";
import { useT } from "../i18n";
import { Shape } from "../live/components";
import { OPTION_STYLES } from "../live/game";
import { formatNumber } from "./grade";

/**
 * How a player answers one question of a custom quiz: the coloured option
 * buttons, a text box, or a slider. Shared by the phone in a class game and
 * the solo player. `question` is the answer-free shape; `onAnswer` receives
 * {choice_id}, {text} or {value}.
 */
function AnswerInput({ question, onAnswer, disabled = false }) {
  const t = useT();
  const kind = question.type ?? "quiz";
  if (kind === "type") return <TypedAnswer onAnswer={onAnswer} disabled={disabled} />;
  if (kind === "slider") return <SliderAnswer question={question} onAnswer={onAnswer} disabled={disabled} />;
  return (
    <div className={`live-phone-options ${kind === "tf" ? "is-two" : ""}`}>
      {question.choices.map((choice, i) => {
        const style = OPTION_STYLES[i];
        return (
          <button
            key={choice.id}
            type="button"
            className={`live-phone-option is-${style.key}`}
            disabled={disabled}
            onClick={() => onAnswer({ choice_id: choice.id })}
            aria-label={choice.name ?? t(`live.shape.${style.key}`)}
          >
            <Shape index={i} size={choice.image_url ? 22 : 28} />
            {choice.image_url && <img src={imageSrc(choice.image_url)} alt="" draggable="false" />}
            {choice.name && <span>{choice.name}</span>}
          </button>
        );
      })}
    </div>
  );
}

function TypedAnswer({ onAnswer, disabled }) {
  const t = useT();
  const [text, setText] = useState("");
  return (
    <form
      className="answer-typed"
      onSubmit={(e) => {
        e.preventDefault();
        if (text.trim()) onAnswer({ text });
      }}
    >
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        maxLength={40}
        autoComplete="off"
        autoCapitalize="off"
        aria-label={t("quizzes.play.typeHere")}
        placeholder={t("quizzes.play.typeHere")}
        disabled={disabled}
      />
      <button type="submit" className="primary-button" disabled={disabled || !text.trim()}>
        {t("quizzes.play.send")}
      </button>
    </form>
  );
}

function SliderAnswer({ question, onAnswer, disabled }) {
  const t = useT();
  const { min, max, step, unit } = question;
  // Start in the middle, on a step; never past max by float rounding.
  const [value, setValue] = useState(() => Math.min(max, min + Math.round((max - min) / 2 / step) * step));
  return (
    <form
      className="answer-slider"
      onSubmit={(e) => {
        e.preventDefault();
        onAnswer({ value });
      }}
    >
      <output className="answer-slider-value">
        {formatNumber(value)} {unit}
      </output>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => setValue(Number(e.target.value))}
        aria-label={t("quizzes.play.pickValue")}
        disabled={disabled}
      />
      <div className="answer-slider-ends">
        <span>{formatNumber(min)}</span>
        <span>{formatNumber(max)}</span>
      </div>
      <button type="submit" className="primary-button" disabled={disabled}>
        {t("quizzes.play.send")}
      </button>
    </form>
  );
}

export default AnswerInput;
