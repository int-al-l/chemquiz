import { useState } from "react";

import { imageSrc } from "../api/client";
import { MASTERY_LABEL } from "../progress/engine";

/**
 * A study card: the photograph fills the front, the name sits in a strip at
 * the bottom (or is hidden, for self-testing), and the back carries the name
 * and the description. Tapping turns it over -- the tap itself is detected by
 * the deck (see useSwipe), which passes `flipped`.
 *
 * Several photographs of the same piece page through with the dots, without
 * leaving the card.
 */
function FlipCard({ item, flipped, hideName, masteryKey, saved, onToggleSave, onFlip }) {
  const photos = item.photo_urls?.length ? item.photo_urls : [item.image_url].filter(Boolean);
  const [photoIndex, setPhotoIndex] = useState(0);
  const [failed, setFailed] = useState({});
  const current = photos[Math.min(photoIndex, photos.length - 1)];

  const chip = masteryKey && (
    <span className={`mastery-chip is-${masteryKey}`}>{MASTERY_LABEL[masteryKey]}</span>
  );

  const star = onToggleSave && (
    <button
      className={`card-icon-button ${saved ? "is-on" : ""}`}
      onClick={(e) => {
        e.stopPropagation();
        onToggleSave();
      }}
      aria-pressed={saved}
      aria-label={saved ? `Remove ${item.name} from my list` : `Save ${item.name} to my list`}
      title={saved ? "In my list" : "Save to my list"}
      type="button"
    >
      <span className="material-symbols-outlined">{saved ? "star" : "star_outline"}</span>
    </button>
  );

  return (
    <div className={`flip-card ${flipped ? "is-flipped" : ""}`}>
      <div className="flip-inner">
        {/* front */}
        <section className="flip-face flip-front" aria-hidden={flipped}>
          <div className="flip-top">
            {chip}
            {star}
          </div>

          <div className="flip-photo">
            {current && !failed[current] ? (
              <img
                src={imageSrc(current)}
                alt={hideName ? "Which piece of glassware is this?" : item.name}
                draggable="false"
                onError={() => setFailed((f) => ({ ...f, [current]: true }))}
              />
            ) : (
              <span className="flip-photo-empty material-symbols-outlined" aria-hidden="true">
                science
              </span>
            )}
          </div>

          {photos.length > 1 && (
            <div className="photo-dots" data-no-swipe>
              {photos.map((url, i) => (
                <button
                  key={url}
                  className={`photo-dot ${i === photoIndex ? "is-active" : ""}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    setPhotoIndex(i);
                  }}
                  aria-label={`Photo ${i + 1} of ${photos.length}`}
                  type="button"
                />
              ))}
            </div>
          )}

          <div className="flip-strip">
            {hideName ? (
              <span className="flip-strip-hint">
                <span className="material-symbols-outlined" aria-hidden="true">touch_app</span>
                Tap to reveal
              </span>
            ) : (
              <span className="flip-name">{item.name}</span>
            )}
          </div>
        </section>

        {/* back */}
        <section className="flip-face flip-back" aria-hidden={!flipped}>
          <div className="flip-top">
            {chip}
            {star}
          </div>
          <div className="flip-back-body">
            {current && (
              <img className="flip-back-thumb" src={imageSrc(current)} alt="" draggable="false" />
            )}
            <h2 className="flip-back-name">{item.name}</h2>
            {item.description ? (
              <p className="flip-back-text">{item.description}</p>
            ) : (
              <p className="flip-back-text is-muted">No description yet.</p>
            )}
          </div>
          <button className="flip-back-turn" onClick={onFlip} type="button">
            <span className="material-symbols-outlined" aria-hidden="true">flip</span>
            Turn back
          </button>
        </section>
      </div>
    </div>
  );
}

export default FlipCard;
