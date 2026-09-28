import { useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import SavedError from "../components/SavedError";
import Thumbnail from "../components/Thumbnail";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchResults } from "../api/client";
import { useApi } from "../hooks/useApi";
import { useSaved } from "../saved/context";
import { LevelCard } from "../components/ProgressBits";

/** One answered question in the review list. */
function ResultRow({ question, has, toggle }) {
  const item = question.item;
  const saved = has(item.slug);

  return (
    <article
      className={`item-card result-card ${
        question.is_correct ? "is-correct" : "is-wrong"
      }`}
    >
      <Thumbnail
        imageUrl={question.image_url ?? item.image_url}
        alt={item.name}
        className="thumbnail-item"
      />

      <div className="item-text">
        <span className="category-name">{item.name}</span>
        {!question.is_correct && (
          <p className="item-description">
            {question.given_answer
              ? `You picked: ${question.given_answer}`
              : "No answer given"}
          </p>
        )}
      </div>

      <button
        className="save-button"
        onClick={() => toggle(item.slug)}
        aria-pressed={saved}
        aria-label={
          saved
            ? `Remove ${item.name} from my list`
            : `Save ${item.name} to my list`
        }
        title={saved ? "In my list" : "Save to my list"}
        type="button"
      >
        <span className="material-symbols-outlined">
          {saved ? "star" : "star_outline"}
        </span>
      </button>
    </article>
  );
}

function QuizResultsPage() {
  const { token } = useParams();
  const location = useLocation();
  const earned = location.state?.xp;
  const bestCombo = location.state?.bestCombo;
  const { has, toggle } = useSaved();

  const loader = useCallback(() => fetchResults(token), [token]);
  const { data: results, error, loading, reload } = useApi(loader, [token]);

  const playAgain = results?.category_slug
    ? `/quiz/setup/${results.category_slug}`
    : "/quiz/setup";

  const answered = results?.questions.filter((q) => q.answered && q.item) ?? [];
  const missed = answered.filter((q) => !q.is_correct);
  const correct = answered.filter((q) => q.is_correct);

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="Results" backTo="/" />

        <section className="categories-content">
          <SavedError />

          {loading && <Loading />}
          {error && <ErrorMessage error={error} onRetry={reload} />}

          {results && (
            <>
              <div className="score-card">
                <p className="score-value">
                  {results.correct_count} / {results.question_count}
                </p>
                <p className="score-label">
                  {results.category_name ?? "All categories"}
                  {" · "}
                  {results.mode === "inverted" ? "find the photo" : "name the photo"}
                </p>
                {earned > 0 && (
                  <p className="score-xp">
                    +{earned} XP
                    {bestCombo >= 2 && <span> · best streak {bestCombo}</span>}
                  </p>
                )}
              </div>

              <LevelCard compact />

              <div className="results-actions">
                <Link className="primary-button" to={playAgain}>
                  Play again
                </Link>
                <Link className="secondary-button" to="/explore">
                  Explore
                </Link>
              </div>

              {missed.length > 0 && (
                <>
                  <h2 className="section-heading">Worth another look</h2>
                  <p className="section-note">
                    They will come back in your next Review. Star any to keep them in My list.
                  </p>
                  <div className="categories-list">
                    {missed.map((question) => (
                      <ResultRow
                        key={question.position}
                        question={question}
                        has={has}
                        toggle={toggle}
                      />
                    ))}
                  </div>
                </>
              )}

              {correct.length > 0 && (
                <>
                  <h2 className="section-heading">You knew these</h2>
                  <div className="categories-list">
                    {correct.map((question) => (
                      <ResultRow
                        key={question.position}
                        question={question}
                        has={has}
                        toggle={toggle}
                      />
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  );
}

export default QuizResultsPage;
