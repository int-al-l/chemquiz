import { Link, NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/context";
import { useProgress } from "../progress/context";
import { dueSlugs } from "../progress/engine";
import { useSaved } from "../saved/context";
import { useT } from "../i18n";
import LanguageSwitch from "../i18n/LanguageSwitch";

/**
 * The frame around every "place" in the app (OdanQuiz Figma): a sidebar on
 * wide screens, a tab bar on phones, and the page in between. Focused screens
 * -- a quiz in progress, a deck of flashcards, the class-game board and the
 * players' phones -- sit outside it and use the whole window.
 */
function AppShell() {
  const t = useT();
  const { user } = useAuth();
  const { slugs } = useSaved();
  const { doc, catalog } = useProgress();
  const due = dueSlugs(doc, (catalog?.items ?? []).map((i) => i.slug)).length;

  return (
    <div className="oq-shell">
      <aside className="oq-sidebar">
        <div className="oq-logo-row">
          <Link to="/" className="oq-logo">OdanQuiz</Link>
          <LanguageSwitch />
        </div>

        <nav className="oq-nav" aria-label={t("main.menu")}>
          <SideLink to="/" icon="home" end>{t("main.home")}</SideLink>
          <SideLink to="/review" icon="event_repeat" pill={due || null}>{t("common.review")}</SideLink>
          <SideLink to="/explore" icon="style">{t("common.explore")}</SideLink>
          <SideLink to="/quiz/setup" icon="science">{t("main.quiz")}</SideLink>
          <SideLink to="/list" icon="star" pill={slugs.length || null}>{t("common.myList")}</SideLink>

          <p className="oq-nav-group">{t("main.classGroup")}</p>
          <SideLink to="/live" icon="cast_for_education" end>{t("main.hostShort")}</SideLink>
          <SideLink to="/join" icon="qr_code_scanner">{t("main.joinShort")}</SideLink>
          <SideLink to="/live/history" icon="history">{t("main.pastGames")}</SideLink>
        </nav>

        <div className="oq-sidebar-bottom">
          <SideLink to={user ? "/profile" : "/sign-in"} icon="account_circle">
            {user ? t("main.profile") : t("common.signIn")}
          </SideLink>
          <p className="oq-copyright">© 2026 OdanChem</p>
        </div>
      </aside>

      <div className="oq-content">
        <Outlet />
      </div>

      <nav className="oq-tabbar" aria-label={t("main.menu")}>
        <TabLink to="/" icon="home" end>{t("main.home")}</TabLink>
        <TabLink to="/explore" icon="style">{t("common.explore")}</TabLink>
        <TabLink to="/quiz/setup" icon="science">{t("main.quiz")}</TabLink>
        <TabLink to="/list" icon="star">{t("main.list")}</TabLink>
        <TabLink to={user ? "/profile" : "/sign-in"} icon="account_circle">{t("main.profile")}</TabLink>
      </nav>
    </div>
  );
}

export function Icon({ name, className = "" }) {
  return <span className={`material-symbols-rounded oq-icon ${className}`} aria-hidden="true">{name}</span>;
}

function SideLink({ to, icon, pill, end, children }) {
  return (
    <NavLink to={to} end={end} className={({ isActive }) => `oq-nav-item ${isActive ? "is-active" : ""}`}>
      <Icon name={icon} />
      <span className="oq-nav-label">{children}</span>
      {pill ? <span className="oq-pill">{pill}</span> : null}
    </NavLink>
  );
}

function TabLink({ to, icon, end, children }) {
  return (
    <NavLink to={to} end={end} className={({ isActive }) => `oq-tab ${isActive ? "is-active" : ""}`}>
      <Icon name={icon} />
      <span>{children}</span>
    </NavLink>
  );
}

export default AppShell;
