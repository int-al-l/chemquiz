import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { deleteLiveGame, fetchLiveGame, fetchLiveGameCsv, IS_DEMO, replayLiveGame } from "../api/client";
import { useAuth } from "../auth/context";
import { useApi } from "../hooks/useApi";
import { useLang, useT } from "../i18n";
import { DemoNotice, SignInToKeep } from "./components";
import { saveHostToken } from "./game";
import { describeGame, playedOn, saveFile } from "./history";

/** One past class game: the standings, the results file, and what to play next. */
function LiveGamePage() {
  const { id } = useParams();
  const { user } = useAuth();
  const t = useT();
  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title={t("live.setup.title")} backTo="/live/history" />
        <section className="categories-content narrow">
          {IS_DEMO ? <DemoNotice /> : user ? <GameDetail id={id} /> : <SignInToKeep />}
        </section>
      </div>
    </main>
  );
}

function GameDetail({ id }) {
  const navigate = useNavigate();
  const t = useT();
  const { lang } = useLang();
  const { data: game, error, loading, reload } = useApi(() => fetchLiveGame(id), [id]);
  const [busy, setBusy] = useState(null); // which button is working
  const [actionError, setActionError] = useState(null);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} onRetry={reload} />;

  async function run(name, work) {
    setBusy(name);
    setActionError(null);
    try {
      await work();
    } catch (err) {
      setActionError(err);
    } finally {
      setBusy(null);
    }
  }

  const replay = (kind) =>
    run(kind, async () => {
      const room = await replayLiveGame(id, kind);
      saveHostToken(room.pin, room.host_token);
      navigate(`/live/host/${room.pin}`);
    });

  const download = () => run("csv", async () => saveFile(await fetchLiveGameCsv(id)));

  const remove = () => {
    if (!window.confirm(t("live.game.deleteConfirm"))) return;
    run("delete", async () => {
      await deleteLiveGame(id);
      navigate("/live/history", { replace: true });
    });
  };

  const stillPlaying = game.status === "live";
  const played = game.standings.length > 0;

  return (
    <>
      <p className="live-history-when">
        {playedOn(game.played_at, lang)}{" "}
        <span className={`live-status is-${game.status}`}>{t(`history.status.${game.status}`)}</span>
      </p>
      <p className="section-note">
        {t("live.game.summary", { game: describeGame(game, t), n: game.time_limit })}
      </p>

      <h2 className="section-heading">{t("live.game.standings")}</h2>
      {played ? (
        <ol className="live-standings">
          {game.standings.map((row) => (
            <li key={row.id}>
              <span className="live-standings-place">{row.place}</span>
              <span className="live-standings-name">{row.name}</span>
              <span className="live-standings-correct">
                {t("live.game.right", { correct: row.correct, asked: game.asked_count })}
              </span>
              <span className="live-standings-score">{row.score}</span>
            </li>
          ))}
        </ol>
      ) : (
        <EmptyMessage>{t("live.game.nobody")}</EmptyMessage>
      )}

      {actionError && <ErrorMessage error={actionError} />}

      <div className="live-history-actions">
        <button type="button" className="secondary-button" onClick={download} disabled={busy !== null}>
          <span className="material-symbols-outlined" aria-hidden="true">download</span>
          {busy === "csv" ? t("live.game.preparing") : t("live.game.csv")}
        </button>
        <button type="button" className="secondary-button" onClick={() => replay("same")} disabled={busy !== null}>
          <span className="material-symbols-outlined" aria-hidden="true">replay</span>
          {busy === "same" ? t("live.opening") : t("live.game.same")}
        </button>
        <button
          type="button"
          className="secondary-button"
          onClick={() => replay("mistakes")}
          disabled={busy !== null || !game.has_mistakes}
        >
          <span className="material-symbols-outlined" aria-hidden="true">school</span>
          {busy === "mistakes" ? t("live.opening") : t("live.game.mistakes")}
        </button>
        <button
          type="button"
          className="text-button live-history-delete"
          onClick={remove}
          disabled={busy !== null || stillPlaying}
        >
          {t("live.game.delete")}
        </button>
      </div>

      {played && !game.has_mistakes && (
        <p className="section-note">{t("live.game.allRight")}</p>
      )}
      {stillPlaying && (
        <p className="section-note">{t("live.game.stillPlaying")}</p>
      )}
    </>
  );
}

export default LiveGamePage;
