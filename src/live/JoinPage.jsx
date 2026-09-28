import { useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage } from "../components/StatusMessage";
import { IS_DEMO, joinLiveGame, peekLiveGame } from "../api/client";
import { DemoNotice } from "./components";
import { playerToken, savePlayerToken } from "./game";

/**
 * A student joins a class game: the PIN from the board (already filled in when
 * they scanned the QR code), then a nickname.
 */
function JoinPage() {
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
      setError({ message: "The PIN has 6 digits -- it is on the board." });
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const game = await peekLiveGame(clean);
      if (playerToken(clean)) {
        navigate(`/play/${clean}`, { replace: true });
        return;
      }
      if (!game.joinable) {
        setError({
          message: game.phase === "finished" ? "That game has finished." : "The host has locked that game.",
        });
      } else {
        setCheckedPin(clean);
      }
    } catch (err) {
      setError(err.status === 404 ? { message: "No game with that PIN. Check the board." } : err);
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
        setError({ message: "No game with that PIN. Check the board." });
      } else {
        setError(err);
      }
      setBusy(false);
    }
  }

  return (
    <main className="setup-page live-join-page">
      <div className="page-layout setup live-join-layout">
        <PageHeader title="Join a game" backTo="/" />

        {IS_DEMO ? (
          <DemoNotice />
        ) : !onNameStep ? (
          <form className="live-join-form" onSubmit={checkPin}>
            <label htmlFor="live-pin">Game PIN</label>
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
              {busy ? "Looking..." : "Next"}
            </button>
          </form>
        ) : (
          <form className="live-join-form" onSubmit={join}>
            <label htmlFor="live-name">Your name</label>
            <input
              id="live-name"
              className="live-big-input"
              autoComplete="nickname"
              maxLength={20}
              placeholder="Nickname"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
            <p className="option-hint">This is what the board shows.</p>
            {error && <ErrorMessage error={error} />}
            <button className="primary-button" type="submit" disabled={busy || !name.trim()}>
              {busy ? "Joining..." : "Join"}
            </button>
            <button className="text-button" type="button" onClick={() => setCheckedPin(null)}>
              Different PIN
            </button>
          </form>
        )}
      </div>
    </main>
  );
}

export default JoinPage;
