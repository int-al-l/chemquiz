import { useState } from "react";

import { imageSrc, questionsFromCards } from "../api/client";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { useT } from "../i18n";
import { useProgress } from "../progress/context";

/** Pick cards from our library; each becomes a "photo → names" or "name → photos" question. */
function LibraryPicker({ lang, onAdd }) {
  const t = useT();
  const { catalog } = useProgress();
  const [deck, setDeck] = useState(null);
  const [mode, setMode] = useState("choice");
  const [picked, setPicked] = useState(() => new Set());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  if (!catalog) return <Loading />;
  const decks = catalog.decks ?? [];
  const inDeck = deck ? new Set(decks.find((d) => d.slug === deck)?.cards ?? []) : null;
  const cards = catalog.items.filter((item) => !inDeck || inDeck.has(item.slug));

  function toggle(slug) {
    const next = new Set(picked);
    if (next.has(slug)) next.delete(slug);
    else next.add(slug);
    setPicked(next);
  }

  async function add() {
    setBusy(true);
    setError(null);
    try {
      const { questions } = await questionsFromCards({ slugs: [...picked], mode, lang });
      onAdd(questions);
      setPicked(new Set());
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="quiz-panel">
      <label>
        {t("quizzes.library.deck")}{" "}
        <select value={deck ?? ""} onChange={(e) => setDeck(e.target.value || null)}>
          <option value="">{t("history.everything")}</option>
          {decks.map((d) => (
            <option key={d.slug} value={d.slug}>
              {d.group ? `${d.group} · ${d.name}` : d.name}
            </option>
          ))}
        </select>
      </label>
      <div className="option-row option-row-tight">
        {["choice", "inverted"].map((m) => (
          <button
            key={m}
            type="button"
            className={`option-button option-button-small ${mode === m ? "is-selected" : ""}`}
            aria-pressed={mode === m}
            onClick={() => setMode(m)}
          >
            {t(`mode.${m}`)}
          </button>
        ))}
        <button type="button" className="text-button" onClick={() => setPicked(new Set(cards.map((c) => c.slug)))}>
          {t("quizzes.library.selectAll")}
        </button>
      </div>
      <div className="quiz-card-grid">
        {cards.map((card) => (
          <button
            key={card.slug}
            type="button"
            className={`quiz-card ${picked.has(card.slug) ? "is-selected" : ""}`}
            aria-pressed={picked.has(card.slug)}
            onClick={() => toggle(card.slug)}
          >
            {card.image_url && <img src={imageSrc(card.image_url)} alt="" loading="lazy" />}
            {card.name}
          </button>
        ))}
      </div>
      {error && <ErrorMessage error={error} />}
      <button type="button" className="primary-button" disabled={busy || picked.size === 0} onClick={add}>
        {t("quizzes.library.add", { n: picked.size })}
      </button>
    </section>
  );
}

export default LibraryPicker;
