import { useCallback, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchCategory, fetchItems, imageSrc, startQuiz } from "../api/client";
import { useApi } from "../hooks/useApi";

const LENGTHS = [5, 10, 20];

const MODES = [
  {
    id: "choice",
    icon: "image_search",
    title: "Name it",
    note: "See a photo, pick the name",
  },
  {
    id: "inverted",
    icon: "grid_view",
    title: "Find it",
    note: "See a name, pick the photo",
  },
];

/** A few of the pictures the quiz will actually ask about, in a stable order. */
function previewOf(items) {
  const withPhoto = (items ?? []).filter((item) => item.image_url);
  if (withPhoto.length === 0) return [];

  // Evenly spaced through the list rather than the first four, so the strip
  // shows the range of a category instead of four variants of one piece.
  // Four, because five wrap onto a second line on a phone.
  const wanted = Math.min(4, withPhoto.length);
  const step = withPhoto.length / wanted;
  return Array.from({ length: wanted }, (_, i) => withPhoto[Math.floor(i * step)]);
}

/**
 * Choose how to play, then start a quiz.
 *
 * Reached with a category (/quiz/setup/condensers) or without
 * (/quiz/setup, the Play button), which draws from the whole library.
 *
 * The page opens with a strip of the photographs it is about to ask about.
 * That is not decoration: it says what a question will look like, and it tells
 * you at a glance whether you picked the category you meant.
 */
function QuizSetupPage() {
  const { slug } = useParams();
  const navigate = useNavigate();

  const [mode, setMode] = useState("choice");
  const [questionCount, setQuestionCount] = useState(10);
  // What is in the number field, which may be briefly empty while typing.
  const [countText, setCountText] = useState("10");
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState(null);

  const loader = useCallback(
    () =>
      Promise.all([
        slug ? fetchCategory(slug) : Promise.resolve(null),
        fetchItems(slug),
      ]).then(([category, items]) => ({ category, items })),
    [slug],
  );
  const { data, error, loading, reload } = useApi(loader, [slug]);

  const category = data?.category ?? null;
  const items = useMemo(() => data?.items ?? [], [data]);
  const preview = useMemo(() => previewOf(items), [items]);

  const available = slug ? (category?.quizzable_count ?? 0) : items.length;
  const title = slug ? (category?.name ?? "Quiz") : "All categories";
  const length = Math.min(questionCount, available || questionCount);

  function pickCount(n) {
    const clamped = Math.max(1, Math.min(n, available || n));
    setQuestionCount(clamped);
    setCountText(String(clamped));
  }

  async function handleStart() {
    setStarting(true);
    setStartError(null);
    try {
      const session = await startQuiz({
        categorySlug: slug,
        mode,
        questionCount: length,
      });
      // replace, so the back button from the quiz returns to the category
      // rather than dropping the player onto setup and starting a second quiz.
      navigate(`/quiz/${session.token}`, { replace: true });
    } catch (err) {
      setStartError(err);
      setStarting(false);
    }
  }

  return (
    <main className="setup-page">
      <div className="page-layout setup">
        <PageHeader title={title} backTo={slug ? `/explore/${slug}` : "/"} />

        <section className="setup-content">
          {loading && <Loading />}
          {error && <ErrorMessage error={error} onRetry={reload} />}

          {!loading && !error && (
            <>
              {available === 0 ? (
                <p className="status-message">
                  This category has no items yet, so there is nothing to quiz on.
                </p>
              ) : (
                <>
                  {preview.length > 0 && (
                    <div className="setup-preview" aria-hidden="true">
                      {preview.map((item) => (
                        <span className="setup-thumb" key={item.slug}>
                          <img src={imageSrc(item.image_url)} alt="" loading="lazy" />
                        </span>
                      ))}
                    </div>
                  )}

                  <p className="setup-lead">
                    {available} piece{available === 1 ? "" : "s"} to name
                    {slug ? ` in ${title.toLowerCase()}` : ""}.
                  </p>

                  <fieldset className="option-group">
                    <legend className="option-legend">Answer by</legend>

                    <div className="option-row">
                      {MODES.map((choice) => (
                        <button
                          key={choice.id}
                          className={`option-button ${mode === choice.id ? "is-selected" : ""}`}
                          onClick={() => setMode(choice.id)}
                          aria-pressed={mode === choice.id}
                          type="button"
                        >
                          <span
                            className="option-icon material-symbols-outlined"
                            aria-hidden="true"
                          >
                            {choice.icon}
                          </span>
                          {choice.title}
                          <span className="option-note">{choice.note}</span>
                        </button>
                      ))}
                    </div>
                  </fieldset>

                  <fieldset className="option-group">
                    <legend className="option-legend">Questions</legend>

                    <div className="option-row option-row-tight">
                      {LENGTHS.filter((n) => n < available).map((count) => (
                        <button
                          key={count}
                          className={`option-button option-button-small ${
                            questionCount === count ? "is-selected" : ""
                          }`}
                          onClick={() => pickCount(count)}
                          aria-pressed={questionCount === count}
                          type="button"
                        >
                          {count}
                        </button>
                      ))}
                      <button
                        className={`option-button option-button-small ${
                          questionCount === available ? "is-selected" : ""
                        }`}
                        onClick={() => pickCount(available)}
                        aria-pressed={questionCount === available}
                        type="button"
                      >
                        All
                        <span className="option-note">{available}</span>
                      </button>
                      <label className="count-field">
                        <span className="option-note">or type</span>
                        <input
                          type="number"
                          inputMode="numeric"
                          min={1}
                          max={available}
                          value={countText}
                          onChange={(e) => {
                            setCountText(e.target.value);
                            const n = parseInt(e.target.value, 10);
                            if (Number.isFinite(n) && n >= 1) {
                              setQuestionCount(Math.min(n, available));
                            }
                          }}
                          onBlur={() => pickCount(questionCount)}
                          aria-label="Number of questions"
                        />
                      </label>
                    </div>

                    {parseInt(countText, 10) > available && (
                      <p className="option-hint">
                        There {available === 1 ? "is" : "are"} {available} piece
                        {available === 1 ? "" : "s"} here, so the quiz will be {available} question
                        {available === 1 ? "" : "s"} long.
                      </p>
                    )}
                  </fieldset>

                  {startError && <ErrorMessage error={startError} />}

                  <button
                    className="primary-button"
                    onClick={handleStart}
                    disabled={starting}
                    type="button"
                  >
                    {starting ? "Starting..." : "Start quiz"}
                    {!starting && (
                      <span className="primary-button-note">
                        {length} question{length === 1 ? "" : "s"},{" "}
                        {mode === "choice" ? "photo to name" : "name to photo"}
                      </span>
                    )}
                  </button>
                </>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  );
}

export default QuizSetupPage;
