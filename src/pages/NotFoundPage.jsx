import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { rich, useT } from "../i18n";

function NotFoundPage() {
  const t = useT();
  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title={t("notfound.title")} backTo="/" />

        <section className="categories-content">
          <p className="status-message">
            {rich(t("notfound.text"), { link: <Link to="/">{t("notfound.back")}</Link> })}
          </p>
        </section>
      </div>
    </main>
  );
}

export default NotFoundPage;
