/** Small pieces drawn on both the board and the phones. */
import qrcode from "qrcode-generator";
import { Link } from "react-router-dom";

export function Shape({ index, size = 28 }) {
  const paths = [
    <polygon key="t" points="12,3 22,20 2,20" />,
    <polygon key="d" points="12,2 22,12 12,22 2,12" />,
    <circle key="c" cx="12" cy="12" r="10" />,
    <rect key="s" x="3" y="3" width="18" height="18" rx="1.5" />,
  ];
  return (
    <svg className="live-shape" viewBox="0 0 24 24" width={size} height={size} aria-hidden="true">
      {paths[index % 4]}
    </svg>
  );
}

export function Countdown({ left, fraction, reading }) {
  const r = 26;
  const c = 2 * Math.PI * r;
  return (
    <div className={`live-countdown ${reading ? "is-reading" : ""} ${!reading && left <= 5 ? "is-low" : ""}`}>
      <svg viewBox="0 0 60 60" aria-hidden="true">
        <circle className="live-countdown-track" cx="30" cy="30" r={r} />
        <circle
          className="live-countdown-fill"
          cx="30"
          cy="30"
          r={r}
          strokeDasharray={c}
          strokeDashoffset={c * (1 - fraction)}
        />
      </svg>
      <span className="live-countdown-number" role="timer">
        {left}
      </span>
    </div>
  );
}

/** A QR code drawn as SVG squares, so it is sharp on a projector. */
export function QrCode({ text, label }) {
  const qr = qrcode(0, "M");
  qr.addData(text);
  qr.make();
  const n = qr.getModuleCount();
  const cells = [];
  for (let y = 0; y < n; y += 1) {
    for (let x = 0; x < n; x += 1) {
      if (qr.isDark(y, x)) cells.push(`M${x + 2} ${y + 2}h1v1h-1z`);
    }
  }
  return (
    <svg className="live-qr" viewBox={`0 0 ${n + 4} ${n + 4}`} role="img" aria-label={label}>
      <rect width={n + 4} height={n + 4} fill="#fff" />
      <path d={cells.join("")} fill="#000" shapeRendering="crispEdges" />
    </svg>
  );
}

export function DemoNotice() {
  return (
    <div className="live-demo-note">
      <span className="material-symbols-outlined" aria-hidden="true">
        cast_for_education
      </span>
      <p>
        Class games connect phones to a shared board, so they need the ChemQuiz server. This demo
        runs entirely in your browser and cannot do that. Run the site with its backend (see the
        README) to play with a class.
      </p>
    </div>
  );
}

/** Shown where a signed-out teacher would otherwise see their past games. */
export function SignInToKeep() {
  return (
    <p className="section-note">
      <Link to="/sign-in">Sign in</Link> to keep the results of the class games you host.
    </p>
  );
}
