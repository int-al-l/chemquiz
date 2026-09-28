import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchLiveGames, IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { useApi } from "../hooks/useApi";
import { useLang, useT } from "../i18n";
import { DemoNotice, SignInToKeep } from "./components";
import { describeGame, playedOn } from "./history";

/** A teacher's past class games, newest first. */
function LiveHistoryPage() {
  const { user } = useAuth();
  const t = useT();
  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title={t("live.setup.pastGames")} backTo="/live" />
        <section className="categories-content narrow">
          {IS_DEMO ? <DemoNotice /> : user ? <GameList /> : <SignInToKeep />}
        </section>
      </div>
    </main>
  );
}

function GameList() {
  const { data: games, error, loading, reload } = useApi(fetchLiveGames);
  const t = useT();
  const { lang } = useLang();

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} onRetry={reload} />;
  if (!games.length) {
    return <EmptyMessage>{t("live.history.empty")}</EmptyMessage>;
  }

  return (
    <ul className="live-history-list">
      {games.map((game) => (
        <li key={game.id}>
          <Link className="live-history-row" to={`/live/history/${game.id}`}>
            <span className="live-history-when">{playedOn(game.played_at, lang)}</span>
            <span className="live-history-what">{describeGame(game, t)}</span>
            <span className="live-history-foot">
              <span className={`live-status is-${game.status}`}>{t(`history.status.${game.status}`)}</span>
              {game.winner && <span>{t("live.history.winner", { name: game.winner })}</span>}
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

export default LiveHistoryPage;
