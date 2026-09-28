import { useCallback } from "react";
import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import SavedError from "../components/SavedError";
import Thumbnail from "../components/Thumbnail";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchItems } from "../api/client";
import { useApi } from "../hooks/useApi";
import { rich, useT } from "../i18n";

import { useSaved } from "../saved/context";

/**
 * Saved items.
 *
 * The list of slugs lives in this browser; the item details come from the API,
 * so a saved item's name or picture stays current after the catalog is edited.
 */
function MyListPage() {
  const t = useT();
  const { slugs, remove, isSignedIn } = useSaved();

  const loader = useCallback(() => fetchItems(), []);
  const { data: items, error, loading, reload } = useApi(loader);

  const saved = (items ?? []).filter((item) => slugs.includes(item.slug));

  // An item saved before it was deleted from the catalog just disappears here.
  const missing = slugs.length - saved.length;

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title={t("common.myList")} backTo="/" />

        <section className="categories-content">
          <SavedError />

          {loading && <Loading />}
          {error && <ErrorMessage error={error} onRetry={reload} />}

          {items && slugs.length === 0 && (
            <EmptyMessage>
              {rich(t("mylist.empty"), {
                explore: <Link to="/explore">{t("common.explore")}</Link>,
              })}
            </EmptyMessage>
          )}

          {saved.length > 0 && (
            <Link className="primary-button" to="/explore/saved">
              {t("mylist.study")}
              <span className="button-note">{t("common.cards", { n: saved.length })}</span>
            </Link>
          )}

          {saved.length > 0 && (
            <div className="categories-list">
              {saved.map((item) => (
                <article key={item.slug} className="item-card">
                  <Thumbnail
                    imageUrl={item.image_url}
                    alt={item.name}
                    className="thumbnail-item"
                  />

                  <div className="item-text">
                    <span className="category-name">{item.name}</span>
                    {item.description && (
                      <p className="item-description">{item.description}</p>
                    )}
                  </div>

                  <button
                    className="save-button"
                    onClick={() => remove(item.slug)}
                    aria-label={t("common.removeItem", { name: item.name })}
                    title={t("common.removeFromList")}
                    type="button"
                  >
                    <span className="material-symbols-outlined">star</span>
                  </button>
                </article>
              ))}
            </div>
          )}

          {items && missing > 0 && (
            <p className="section-note">
              {t("mylist.missing", { n: missing })}
            </p>
          )}

          <p className="section-note">
            {isSignedIn ? (
              t("mylist.synced")
            ) : (
              rich(t("mylist.local"), { signIn: <Link to="/sign-in">{t("common.signInLink")}</Link> })
            )}
          </p>
        </section>
      </div>
    </main>
  );
}

export default MyListPage;
