import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { LevelCard, MasteryBar } from "../components/ProgressBits";
import Thumbnail from "../components/Thumbnail";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { useProgress } from "../progress/context";
import { deckSummary, dueSlugs } from "../progress/engine";
import { useSaved } from "../saved/context";

/**
 * Every deck at once, each with how far through it you are. Opening a deck
 * goes straight to its cards.
 */
function ExplorePage() {
  const { catalog, doc, reloadCatalog } = useProgress();
  const { slugs: saved } = useSaved();

  const decks = catalog?.decks ?? [];
  const allSlugs = (catalog?.items ?? []).map((i) => i.slug);
  const due = dueSlugs(doc, allSlugs).length;

  const groups = [];
  for (const deck of decks) {
    const name = deck.group ?? "";
    let group = groups.find((g) => g.name === name);
    if (!group) groups.push((group = { name, decks: [] }));
    group.decks.push(deck);
  }

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="Explore" backTo="/" />

        <section className="categories-content">
          <LevelCard compact />

          {!catalog && <Loading />}
          {catalog?.failed && (
            <ErrorMessage error={new Error("Could not load the decks.")} onRetry={reloadCatalog} />
          )}
          {catalog && !catalog.failed && decks.length === 0 && (
            <EmptyMessage>
              <strong>The content database is empty.</strong> Run{" "}
              <code>python seed.py --reset</code> in the <code>backend</code> folder and restart it.
            </EmptyMessage>
          )}

          {decks.length > 0 && (
            <div className="quick-decks">
              <Link to="/review" className={`quick-deck ${due ? "is-due" : ""}`}>
                <span className="material-symbols-outlined" aria-hidden="true">event_repeat</span>
                <span>
                  <strong>Review</strong>
                  <small>{due ? `${due} due now` : "Nothing due"}</small>
                </span>
              </Link>
              <Link to="/explore/all" className="quick-deck">
                <span className="material-symbols-outlined" aria-hidden="true">stacks</span>
                <span>
                  <strong>All cards</strong>
                  <small>{allSlugs.length} cards</small>
                </span>
              </Link>
              <Link to="/explore/saved" className="quick-deck">
                <span className="material-symbols-outlined" aria-hidden="true">star</span>
                <span>
                  <strong>My list</strong>
                  <small>{saved.length} saved</small>
                </span>
              </Link>
            </div>
          )}

          {groups.map((group) => (
            <section key={group.name} className="deck-group">
              {group.name && <h2 className="section-heading">{group.name}</h2>}
              <div className="deck-grid">
                {group.decks.map((deck) => {
                  const s = deckSummary(doc, deck.cards);
                  const done = s.mastered === s.total;
                  return (
                    <Link key={deck.slug} to={`/explore/${deck.slug}`} className="deck-tile">
                      <Thumbnail imageUrl={deck.image_url} className="deck-thumb" />
                      <span className="deck-tile-name">
                        {deck.name}
                        {done && (
                          <span className="material-symbols-outlined deck-trophy" aria-label="Mastered">
                            emoji_events
                          </span>
                        )}
                      </span>
                      <span className="deck-tile-meta">
                        {s.total} cards
                        {s.due > 0 && <span className="due-chip">{s.due} due</span>}
                      </span>
                      <MasteryBar summary={s} />
                    </Link>
                  );
                })}
              </div>
            </section>
          ))}

          {decks.length > 0 && (
            <p className="legend">
              <span className="legend-dot is-mastered" /> mastered
              <span className="legend-dot is-familiar" /> familiar
              <span className="legend-dot is-learning" /> learning
            </p>
          )}
        </section>
      </div>
    </main>
  );
}

export default ExplorePage;
