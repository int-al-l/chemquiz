import { Link } from "react-router-dom";

import { titleKey, useT } from "../i18n";
import { useProgress } from "../progress/context";

/** A circular progress ring with optional content in the middle. */
export function Ring({ value, size = 56, stroke = 6, className = "", children, label }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const v = Math.max(0, Math.min(1, value || 0));
  return (
    <span
      className={`ring ${className}`}
      style={{ width: size, height: size }}
      role="img"
      aria-label={label}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
        <circle className="ring-track" cx={size / 2} cy={size / 2} r={r} strokeWidth={stroke} fill="none" />
        <circle
          className="ring-fill"
          cx={size / 2}
          cy={size / 2}
          r={r}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - v)}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      {children !== undefined && <span className="ring-center">{children}</span>}
    </span>
  );
}

/** A thin bar split by mastery: mastered, familiar, learning, new. */
export function MasteryBar({ summary, className = "" }) {
  const t = useT();
  const total = summary.total || 1;
  const part = (n) => `${(n / total) * 100}%`;
  return (
    <div
      className={`mastery-bar ${className}`}
      role="img"
      aria-label={t("mastery.bar", summary)}
    >
      <span className="mb-mastered" style={{ width: part(summary.mastered) }} />
      <span className="mb-familiar" style={{ width: part(summary.familiar) }} />
      <span className="mb-learning" style={{ width: part(summary.learning) }} />
    </div>
  );
}

/** Level, XP towards the next one, streak and today's goal -- one compact card. */
export function LevelCard({ compact = false }) {
  const { level, streak, today, goal } = useProgress();
  const t = useT();
  return (
    <Link to="/profile" className={`level-card ${compact ? "is-compact" : ""}`}>
      <Ring value={level.fraction} size={compact ? 48 : 60} stroke={5} className="level-ring" label={t("levelcard.level", { n: level.level })}>
        <span className="level-number">{level.level}</span>
      </Ring>

      <span className="level-text">
        <span className="level-title">{t(titleKey(level.title))}</span>
        <span className="level-xp">
          {level.into} / {level.span} XP
        </span>
        <span className="level-bar" aria-hidden="true">
          <span style={{ width: `${level.fraction * 100}%` }} />
        </span>
      </span>

      <span className="level-stats">
        <span className={`stat-pill ${streak > 0 ? "is-hot" : ""}`} title={t("levelcard.streak")}>
          <span className="material-symbols-outlined" aria-hidden="true">local_fire_department</span>
          {streak}
        </span>
        <span className="stat-pill" title={t("levelcard.todayGoal")}>
          <Ring value={today / goal} size={20} stroke={3} className="goal-ring" label={t("levelcard.dailyGoal")} />
          {Math.min(today, goal)}/{goal}
        </span>
      </span>
    </Link>
  );
}
