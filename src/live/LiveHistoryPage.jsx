import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchLiveGames, IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { useApi } from "../hooks/useApi";
import { DemoNotice, SignInToKeep } from "./components";
import { describeGame, playedOn, STATUS_LABELS } from "./history";

/** A teacher's past class games, newest first. */
function LiveHistoryPage() {
  const { user } = useAuth();
  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="Past games" backTo="/live" />
        <section className="categories-content narrow">
          {IS_DEMO ? <DemoNotice /> : user ? <GameList /> : <SignInToKeep />}
        </section>
      </div>
    </main>
  );
}

function GameList() {
  const { data: games, error, loading, reload } = useApi(fetchLiveGames);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} onRetry={reload} />;
  if (!games.length) {
    return <EmptyMessage>No games yet. Class games you host while signed in appear here.</EmptyMessage>;
  }

  return (
    <ul className="live-history-list">
      {games.map((game) => (
        <li key={game.id}>
          <Link className="live-history-row" to={`/live/history/${game.id}`}>
            <span className="live-history-when">{playedOn(game.played_at)}</span>
            <span className="live-history-what">{describeGame(game)}</span>
            <span className="live-history-foot">
              <span className={`live-status is-${game.status}`}>{STATUS_LABELS[game.status]}</span>
              {game.winner && <span>Winner: {game.winner}</span>}
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

export default LiveHistoryPage;
