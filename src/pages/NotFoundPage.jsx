import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";

function NotFoundPage() {
  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="Not found" backTo="/" />

        <section className="categories-content">
          <p className="status-message">
            That page does not exist. <Link to="/">Back to the menu</Link>.
          </p>
        </section>
      </div>
    </main>
  );
}

export default NotFoundPage;
