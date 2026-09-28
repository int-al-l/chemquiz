import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { LevelCard, MasteryBar } from "../components/ProgressBits";
import Thumbnail from "../components/Thumbnail";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { rich, useT } from "../i18n";
import { useProgress } from "../progress/context";
import { deckSummary, dueSlugs } from "../progress/engine";
import { useSaved } from "../saved/context";

/**
 * Every deck at once, each with how far through it you are. Opening a deck
 * goes straight to its cards.
 */
function ExplorePage() {
  const t = useT();
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
        <PageHeader title={t("common.explore")} backTo="/" />

        <section className="categories-content">
          <LevelCard compact />

          {!catalog && <Loading />}
          {catalog?.failed && (
            <ErrorMessage error={new Error(t("explore.loadFailed"))} onRetry={reloadCatalog} />
          )}
          {catalog && !catalog.failed && decks.length === 0 && (
            <EmptyMessage>
              {rich(t("explore.empty"), {
                title: <strong>{t("explore.emptyTitle")}</strong>,
                command: <code>python seed.py --reset</code>,
                folder: <code>backend</code>,
              })}
            </EmptyMessage>
          )}

          {decks.length > 0 && (
            <div className="quick-decks">
              <Link to="/review" className={`quick-deck ${due ? "is-due" : ""}`}>
                <span className="material-symbols-outlined" aria-hidden="true">event_repeat</span>
                <span>
                  <strong>{t("common.review")}</strong>
                  <small>{due ? t("explore.dueNow", { n: due }) : t("explore.nothingDue")}</small>
                </span>
              </Link>
              <Link to="/explore/all" className="quick-deck">
                <span className="material-symbols-outlined" aria-hidden="true">stacks</span>
                <span>
                  <strong>{t("common.allCards")}</strong>
                  <small>{t("common.cards", { n: allSlugs.length })}</small>
                </span>
              </Link>
              <Link to="/explore/saved" className="quick-deck">
                <span className="material-symbols-outlined" aria-hidden="true">star</span>
                <span>
                  <strong>{t("common.myList")}</strong>
                  <small>{t("explore.saved", { n: saved.length })}</small>
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
                          <span className="material-symbols-outlined deck-trophy" aria-label={t("explore.deckMastered")}>
                            emoji_events
                          </span>
                        )}
                      </span>
                      <span className="deck-tile-meta">
                        {t("common.cards", { n: s.total })}
                        {s.due > 0 && <span className="due-chip">{t("explore.deckDue", { n: s.due })}</span>}
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
              <span className="legend-dot is-mastered" /> {t("explore.legendMastered")}
              <span className="legend-dot is-familiar" /> {t("explore.legendFamiliar")}
              <span className="legend-dot is-learning" /> {t("explore.legendLearning")}
            </p>
          )}
        </section>
      </div>
    </main>
  );
}

export default ExplorePage;
