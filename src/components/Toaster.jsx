import { useProgress } from "../progress/context";

/** XP pops, level-ups and new badges, floating above whatever page is open. */
function Toaster() {
  const { toasts, dismissToast } = useProgress();
  if (!toasts.length) return null;

  return (
    <div className="toaster" aria-live="polite">
      {toasts.map((t) => {
        if (t.type === "xp") {
          return (
            <div key={`${t.id}-${t.bump}`} className="toast toast-xp">
              +{t.amount} XP
            </div>
          );
        }
        let icon = "celebration";
        let title = "";
        let text = "";
        if (t.type === "level") {
          icon = "military_tech";
          title = `Level ${t.level}!`;
          text = t.newTitle ? `New title: ${t.title}` : "Keep it up!";
        } else if (t.type === "badge") {
          icon = t.badge.icon;
          title = "Badge unlocked";
          text = t.badge.title;
        } else if (t.type === "goal") {
          icon = "flag";
          title = "Daily goal reached";
          text = "+20 XP bonus";
        }
        return (
          <button
            key={t.id}
            className={`toast toast-${t.type}`}
            onClick={() => dismissToast(t.id)}
            type="button"
          >
            <span className="toast-icon material-symbols-outlined" aria-hidden="true">{icon}</span>
            <span className="toast-text">
              <strong>{title}</strong>
              <span>{text}</span>
            </span>
          </button>
        );
      })}
    </div>
  );
}

export default Toaster;
