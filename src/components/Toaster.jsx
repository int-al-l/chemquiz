import { badgeText, titleKey, useT } from "../i18n";
import { useProgress } from "../progress/context";

/** XP pops, level-ups and new badges, floating above whatever page is open. */
function Toaster() {
  const { toasts, dismissToast } = useProgress();
  const tr = useT();
  if (!toasts.length) return null;

  return (
    <div className="toaster" aria-live="polite">
      {toasts.map((t) => {
        if (t.type === "xp") {
          return (
            <div key={`${t.id}-${t.bump}`} className="toast toast-xp">
              {tr("toast.xp", { amount: t.amount })}
            </div>
          );
        }
        let icon = "celebration";
        let title = "";
        let text = "";
        if (t.type === "level") {
          icon = "military_tech";
          title = tr("toast.level", { n: t.level });
          text = t.newTitle ? tr("toast.newTitle", { title: tr(titleKey(t.title)) }) : tr("toast.keepItUp");
        } else if (t.type === "badge") {
          icon = t.badge.icon;
          title = tr("toast.badge");
          text = badgeText(tr, t.badge).title;
        } else if (t.type === "goal") {
          icon = "flag";
          title = tr("toast.goal");
          text = tr("toast.goalBonus");
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
