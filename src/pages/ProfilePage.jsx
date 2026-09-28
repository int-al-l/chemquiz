import { Link, useNavigate } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { Ring } from "../components/ProgressBits";
import { IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import LanguageSwitch from "../i18n/LanguageSwitch";
import { useProgress } from "../progress/context";
import { BADGES, GOAL_CHOICES, deckBadges, deckSummary, recentDays } from "../progress/engine";

const WEEKDAY = ["S", "M", "T", "W", "T", "F", "S"];

/** Level, streak, activity, badges, the daily goal -- and the account. */
function ProfilePage() {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const { doc, level, streak, today, goal, setGoal, catalog, syncing } = useProgress();

  const allSlugs = (catalog?.items ?? []).map((i) => i.slug);
  const summary = deckSummary(doc, allSlugs);
  const week = recentDays(doc, 7);
  const peak = Math.max(goal, ...week.map((d) => d.xp));
  const badges = [...BADGES, ...deckBadges(catalog?.decks)];
  const unlocked = badges.filter((b) => doc.badges?.[b.id]).length;

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="Your progress" backTo="/" />

        <section className="categories-content narrow profile">
          <div className="profile-hero">
            <Ring value={level.fraction} size={112} stroke={9} className="level-ring" label={`Level ${level.level}`}>
              <span className="profile-level">{level.level}</span>
              <span className="profile-level-label">level</span>
            </Ring>
            <div>
              <p className="profile-title">{level.title}</p>
              <p className="profile-xp">
                {level.xp} XP · {level.toNext} to level {level.level + 1}
              </p>
              {user ? (
                <p className="profile-account">
                  {user.name} · {user.email}
                  {syncing ? " · syncing…" : ""}
                </p>
              ) : (
                <p className="profile-account">
                  Saved in this browser only. <Link to="/sign-in">Sign in</Link> to keep it.
                </p>
              )}
            </div>
          </div>

          <LanguageSwitch />

          <div className="stat-grid">
            <div className="stat-box">
              <span className="material-symbols-outlined is-fire" aria-hidden="true">local_fire_department</span>
              <strong>{streak}</strong>
              <span>day streak</span>
            </div>
            <div className="stat-box">
              <span className="material-symbols-outlined is-gold" aria-hidden="true">emoji_events</span>
              <strong>{summary.mastered}</strong>
              <span>mastered</span>
            </div>
            <div className="stat-box">
              <span className="material-symbols-outlined" aria-hidden="true">style</span>
              <strong>{summary.total - summary.new}</strong>
              <span>of {summary.total} studied</span>
            </div>
            <div className="stat-box">
              <span className="material-symbols-outlined" aria-hidden="true">bolt</span>
              <strong>{doc.stats?.bestCombo ?? 0}</strong>
              <span>best combo</span>
            </div>
          </div>

          <h2 className="section-heading">This week</h2>
          <div className="week-chart" role="img" aria-label="XP earned on each of the last 7 days">
            {week.map((d) => (
              <span key={d.key} className="week-col">
                <span className="week-bar-wrap">
                  <span
                    className={`week-bar ${d.xp >= goal ? "is-goal" : ""}`}
                    style={{ height: `${peak ? (d.xp / peak) * 100 : 0}%` }}
                    title={`${d.xp} XP`}
                  />
                </span>
                <span className="week-day">{WEEKDAY[d.weekday]}</span>
              </span>
            ))}
          </div>

          <h2 className="section-heading">Daily goal</h2>
          <p className="section-note">
            {Math.min(today, goal)} of {goal} XP today. Reaching it gives a 20 XP bonus.
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
                  {g === 30 ? "casual" : g === 50 ? "regular" : g === 100 ? "serious" : "intense"}
                </span>
              </button>
            ))}
          </div>

          <h2 className="section-heading">
            Badges <span className="muted">{unlocked} / {badges.length}</span>
          </h2>
          <div className="badge-grid">
            {badges.map((b) => {
              const got = Boolean(doc.badges?.[b.id]);
              return (
                <div key={b.id} className={`badge ${got ? "is-unlocked" : ""}`} title={b.blurb}>
                  <span className="badge-icon material-symbols-outlined" aria-hidden="true">
                    {got ? b.icon : "lock"}
                  </span>
                  <span className="badge-title">{b.title}</span>
                  <span className="badge-blurb">{b.blurb}</span>
                </div>
              );
            })}
          </div>

          {user && !IS_DEMO && (
            <Link className="secondary-button" to="/live/history">
              Past class games
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
              Sign out
            </button>
          )}
        </section>
      </div>
    </main>
  );
}

export default ProfilePage;
