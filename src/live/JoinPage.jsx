import { useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage } from "../components/StatusMessage";
import { IS_DEMO, joinLiveGame, peekLiveGame } from "../api/client";
import { LanguageScope } from "../i18n/LanguageProvider";
import { useT } from "../i18n";
import { DemoNotice } from "./components";
import { playerToken, savePlayerToken } from "./game";

/**
 * A student joins a class game: the PIN from the board (already filled in when
 * they scanned the QR code), then a nickname.
 */
function JoinPage() {
  const [gameLang, setGameLang] = useState(null); // the game's language, once the server has told us
  return (
    <LanguageScope lang={gameLang}>
      <JoinForm onGameLang={setGameLang} />
    </LanguageScope>
  );
}

function JoinForm({ onGameLang }) {
  const t = useT();
  const { pin: pinFromUrl } = useParams();
  const navigate = useNavigate();
  const [pin, setPin] = useState(pinFromUrl ?? "");
  // Scanning the QR code skips the PIN step; a bad PIN still fails on Join.
  const [checkedPin, setCheckedPin] = useState(pinFromUrl ?? null);
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  // Already in this game on this phone (a reload, or the QR scanned twice).
  if (pinFromUrl && playerToken(pinFromUrl)) {
    return <Navigate to={`/play/${pinFromUrl}`} replace />;
  }

  const onNameStep = checkedPin !== null;

  async function checkPin(event) {
    event.preventDefault();
    const clean = pin.replace(/\D/g, "");
    if (clean.length !== 6) {
      setError({ message: t("live.join.badPin") });
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const game = await peekLiveGame(clean);
      onGameLang(game.lang ?? null);
      if (playerToken(clean)) {
        navigate(`/play/${clean}`, { replace: true });
        return;
      }
      if (!game.joinable) {
        setError({
          message: game.phase === "finished" ? t("live.join.finished") : t("live.join.locked"),
        });
      } else {
        setCheckedPin(clean);
      }
    } catch (err) {
      setError(err.status === 404 ? { message: t("live.join.noGame") } : err);
    } finally {
      setBusy(false);
    }
  }

  async function join(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const joined = await joinLiveGame(checkedPin, name);
      savePlayerToken(checkedPin, joined.token);
      navigate(`/play/${checkedPin}`, { replace: true });
    } catch (err) {
      if (err.status === 404) {
        setCheckedPin(null);
        setError({ message: t("live.join.noGame") });
      } else {
        setError(err);
      }
      setBusy(false);
    }
  }

  return (
    <main className="setup-page live-join-page">
      <div className="page-layout setup live-join-layout">
        <PageHeader title={t("live.join.title")} backTo="/" />

        {IS_DEMO ? (
          <DemoNotice />
        ) : !onNameStep ? (
          <form className="live-join-form" onSubmit={checkPin}>
            <label htmlFor="live-pin">{t("live.join.pin")}</label>
            <input
              id="live-pin"
              className="live-big-input"
              inputMode="numeric"
              autoComplete="off"
              maxLength={7}
              placeholder="123 456"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/[^\d ]/g, ""))}
              autoFocus
            />
            {error && <ErrorMessage error={error} />}
            <button className="primary-button" type="submit" disabled={busy}>
              {busy ? t("live.join.looking") : t("live.join.next")}
            </button>
          </form>
        ) : (
          <form className="live-join-form" onSubmit={join}>
            <label htmlFor="live-name">{t("live.join.name")}</label>
            <input
              id="live-name"
              className="live-big-input"
              autoComplete="nickname"
              maxLength={20}
              placeholder={t("live.join.nickname")}
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
            <p className="option-hint">{t("live.join.hint")}</p>
            {error && <ErrorMessage error={error} />}
            <button className="primary-button" type="submit" disabled={busy || !name.trim()}>
              {busy ? t("live.join.joining") : t("live.join.join")}
            </button>
            <button className="text-button" type="button" onClick={() => setCheckedPin(null)}>
              {t("live.join.otherPin")}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}

export default JoinPage;
