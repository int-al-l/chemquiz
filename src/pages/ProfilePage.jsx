import { Link, useNavigate } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { Ring } from "../components/ProgressBits";
import { IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { badgeText, rich, titleKey, useLang, useT } from "../i18n";
import LanguageSwitch from "../i18n/LanguageSwitch";
import { useProgress } from "../progress/context";
import { BADGES, GOAL_CHOICES, deckBadges, deckSummary, recentDays } from "../progress/engine";

/** One-letter weekday names, Sunday first (index = Date.getDay()). */
function weekdayLetters(lang) {
  const format = new Intl.DateTimeFormat(lang, { weekday: "narrow", timeZone: "UTC" });
  // 2026-01-04 was a Sunday.
  return Array.from({ length: 7 }, (_, i) => format.format(Date.UTC(2026, 0, 4 + i)));
}

/** Level, streak, activity, badges, the daily goal -- and the account. */
function ProfilePage() {
  const t = useT();
  const { lang } = useLang();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const { doc, level, streak, today, goal, setGoal, catalog, syncing } = useProgress();

  const allSlugs = (catalog?.items ?? []).map((i) => i.slug);
  const summary = deckSummary(doc, allSlugs);
  const week = recentDays(doc, 7);
  const weekday = weekdayLetters(lang);
  const peak = Math.max(goal, ...week.map((d) => d.xp));
  const badges = [...BADGES, ...deckBadges(catalog?.decks)];
  const unlocked = badges.filter((b) => doc.badges?.[b.id]).length;

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title={t("profile.title")} backTo="/" />

        <section className="categories-content narrow profile">
          <div className="profile-hero">
            <Ring value={level.fraction} size={112} stroke={9} className="level-ring" label={t("levelcard.level", { n: level.level })}>
              <span className="profile-level">{level.level}</span>
              <span className="profile-level-label">{t("profile.level")}</span>
            </Ring>
            <div>
              <p className="profile-title">{t(titleKey(level.title))}</p>
              <p className="profile-xp">
                {t("profile.xp", { xp: level.xp, n: level.toNext, next: level.level + 1 })}
              </p>
              {user ? (
                <p className="profile-account">
                  {user.name} · {user.email}
                  {syncing ? t("profile.syncing") : ""}
                </p>
              ) : (
                <p className="profile-account">
                  {rich(t("profile.local"), {
                    signIn: <Link to="/sign-in">{t("common.signInLink")}</Link>,
                  })}
                </p>
              )}
            </div>
          </div>

          <LanguageSwitch />

          <div className="stat-grid">
            <div className="stat-box">
              <span className="material-symbols-outlined is-fire" aria-hidden="true">local_fire_department</span>
              <strong>{streak}</strong>
              <span>{t("profile.streak", { n: streak })}</span>
            </div>
            <div className="stat-box">
              <span className="material-symbols-outlined is-gold" aria-hidden="true">emoji_events</span>
              <strong>{summary.mastered}</strong>
              <span>{t("profile.mastered")}</span>
            </div>
            <div className="stat-box">
              <span className="material-symbols-outlined" aria-hidden="true">style</span>
              <strong>{summary.total - summary.new}</strong>
              <span>{t("profile.studied", { total: summary.total })}</span>
            </div>
            <div className="stat-box">
              <span className="material-symbols-outlined" aria-hidden="true">bolt</span>
              <strong>{doc.stats?.bestCombo ?? 0}</strong>
              <span>{t("profile.bestCombo")}</span>
            </div>
          </div>

          <h2 className="section-heading">{t("profile.week")}</h2>
          <div className="week-chart" role="img" aria-label={t("profile.weekChart")}>
            {week.map((d) => (
              <span key={d.key} className="week-col">
                <span className="week-bar-wrap">
                  <span
                    className={`week-bar ${d.xp >= goal ? "is-goal" : ""}`}
                    style={{ height: `${peak ? (d.xp / peak) * 100 : 0}%` }}
                    title={`${d.xp} XP`}
                  />
                </span>
                <span className="week-day">{weekday[d.weekday]}</span>
              </span>
            ))}
          </div>

          <h2 className="section-heading">{t("levelcard.dailyGoal")}</h2>
          <p className="section-note">
            {t("profile.goalNote", { done: Math.min(today, goal), goal })}
          </p>
          <div className="option-row option-row-tight">
            {GOAL_CHOICES.map((g) => (
              <button
                key={g}
                className={`option-button option-button-small ${goal === g ? "is-selected" : ""}`}
                onClick={() => setGoal(g)}
                aria-pressed={goal === g}
                type="button"
              >
                {g}
                <span className="option-note">
                  {t(`profile.goal${g}`)}
                </span>
              </button>
            ))}
          </div>

          <h2 className="section-heading">
            {t("profile.badges")} <span className="muted">{unlocked} / {badges.length}</span>
          </h2>
          <div className="badge-grid">
            {badges.map((b) => {
              const got = Boolean(doc.badges?.[b.id]);
              const text = badgeText(t, b);
              return (
                <div key={b.id} className={`badge ${got ? "is-unlocked" : ""}`} title={text.blurb}>
                  <span className="badge-icon material-symbols-outlined" aria-hidden="true">
                    {got ? b.icon : "lock"}
                  </span>
                  <span className="badge-title">{text.title}</span>
                  <span className="badge-blurb">{text.blurb}</span>
                </div>
              );
            })}
          </div>

          {user && !IS_DEMO && (
            <Link className="secondary-button" to="/live/history">
              {t("profile.pastGames")}
            </Link>
          )}

          {user && (
            <button
              className="secondary-button"
              onClick={() => {
                signOut();
                navigate("/", { replace: true });
              }}
              type="button"
            >
              {t("profile.signOut")}
            </button>
          )}
        </section>
      </div>
    </main>
  );
}

export default ProfilePage;
