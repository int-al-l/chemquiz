import { Link } from "react-router-dom";

import { LevelCard } from "../components/ProgressBits";
import { IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { useProgress } from "../progress/context";
import { dueSlugs } from "../progress/engine";
import { useSaved } from "../saved/context";
import { useT } from "../i18n";
import LanguageSwitch from "../i18n/LanguageSwitch";

/**
 * The menu: where you stand (level, streak, today's goal), then what to do.
 * When cards are due for review, reviewing them is offered first -- that is
 * the single most useful thing to do on a return visit.
 */
function MainPage() {
  const t = useT();
  const { user } = useAuth();
  const { slugs } = useSaved();
  const { doc, catalog } = useProgress();

  const due = dueSlugs(doc, (catalog?.items ?? []).map((i) => i.slug)).length;

  const tiles = [
    due > 0 && {
      to: "/review",
      icon: "event_repeat",
      title: t("common.review"),
      blurb: t("main.reviewBlurb", { n: due }),
      variant: "is-primary",
      badge: due,
    },
    {
      to: "/quiz/setup",
      icon: "science",
      title: t("main.play"),
      blurb: t("main.playBlurb"),
      variant: due > 0 ? "" : "is-primary",
    },
    {
      to: "/explore",
      icon: "style",
      title: t("common.explore"),
      blurb: t("main.exploreBlurb"),
    },
    {
      to: "/join",
      icon: "phone_iphone",
      title: t("main.join"),
      blurb: t("main.joinBlurb"),
    },
    {
      to: "/live",
      icon: "cast_for_education",
      title: t("main.host"),
      blurb: t("main.hostBlurb"),
    },
    {
      to: "/list",
      icon: "star",
      title: t("common.myList"),
      blurb: t("main.myListBlurb"),
      badge: slugs.length || null,
    },
  ].filter(Boolean);

  return (
    <main className="main-page">
      <div className="page-layout home">
        <header className="home-header">
          <h1 className="home-title">{t("main.title")}</h1>
          <LanguageSwitch />
        </header>

        <LevelCard />

        <nav className="tile-grid" aria-label={t("main.menu")}>
          {tiles.map((tile) => (
            <Link key={tile.to} to={tile.to} className={`tile ${tile.variant ?? ""}`}>
              <span className="tile-icon material-symbols-outlined" aria-hidden="true">
                {tile.icon}
              </span>

              <span className="tile-text">
                <span className="tile-title">
                  {tile.title}
                  {tile.badge ? <span className="tile-badge">{tile.badge}</span> : null}
                </span>
                <span className="tile-blurb">{tile.blurb}</span>
              </span>

              <span className="tile-chevron material-symbols-outlined" aria-hidden="true">
                chevron_right
              </span>
            </Link>
          ))}
        </nav>

        <footer className="home-footer">
          <Link className="account-chip" to={user ? "/profile" : "/sign-in"}>
            <span className="material-symbols-outlined" aria-hidden="true">
              account_circle
            </span>
            {user ? t("main.signedInAs", { name: user.name }) : t("main.signInPrompt")}
          </Link>
          {IS_DEMO && (
            <p className="demo-note">
              {t("main.demoNote")}
            </p>
          )}
        </footer>
      </div>
    </main>
  );
}

export default MainPage;
