import { Link } from "react-router-dom";

import { LevelCard } from "../components/ProgressBits";
import { useAuth } from "../auth/context";
import { useProgress } from "../progress/context";
import { dueSlugs } from "../progress/engine";
import { useSaved } from "../saved/context";

/**
 * The menu: where you stand (level, streak, today's goal), then what to do.
 * When cards are due for review, reviewing them is offered first -- that is
 * the single most useful thing to do on a return visit.
 */
function MainPage() {
  const { user } = useAuth();
  const { slugs } = useSaved();
  const { doc, catalog } = useProgress();

  const due = dueSlugs(doc, (catalog?.items ?? []).map((i) => i.slug)).length;

  const tiles = [
    due > 0 && {
      to: "/review",
      icon: "event_repeat",
      title: "Review",
      blurb: `${due} card${due === 1 ? " is" : "s are"} ready to refresh`,
      variant: "is-primary",
      badge: due,
    },
    {
      to: "/quiz/setup",
      icon: "science",
      title: "Play",
      blurb: "Name the glassware, or find it by name",
      variant: due > 0 ? "" : "is-primary",
    },
    {
      to: "/explore",
      icon: "style",
      title: "Explore",
      blurb: "Learn with flashcards, deck by deck",
    },
    {
      to: "/list",
      icon: "star",
      title: "My list",
      blurb: "The ones you saved to revise",
      badge: slugs.length || null,
    },
  ].filter(Boolean);

  return (
    <main className="main-page">
      <div className="page-layout home">
        <header className="home-header">
          <h1 className="home-title">Chemical Quiz</h1>
        </header>

        <LevelCard />

        <nav className="tile-grid" aria-label="Main menu">
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
            {user ? `Signed in as ${user.name}` : "Sign in to keep your progress"}
          </Link>
        </footer>
      </div>
    </main>
  );
}

export default MainPage;
