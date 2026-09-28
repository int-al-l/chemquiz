import { useCallback } from "react";
import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import SavedError from "../components/SavedError";
import Thumbnail from "../components/Thumbnail";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchItems } from "../api/client";
import { useApi } from "../hooks/useApi";

import { useSaved } from "../saved/context";

/**
 * Saved items.
 *
 * The list of slugs lives in this browser; the item details come from the API,
 * so a saved item's name or picture stays current after the catalog is edited.
 */
function MyListPage() {
  const { slugs, remove, isSignedIn } = useSaved();

  const loader = useCallback(() => fetchItems(), []);
  const { data: items, error, loading, reload } = useApi(loader);

  const saved = (items ?? []).filter((item) => slugs.includes(item.slug));

  // An item saved before it was deleted from the catalog just disappears here.
  const missing = slugs.length - saved.length;

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="My list" backTo="/" />

        <section className="categories-content">
          <SavedError />

          {loading && <Loading />}
          {error && <ErrorMessage error={error} onRetry={reload} />}

          {items && slugs.length === 0 && (
            <EmptyMessage>
              Nothing saved yet. Tap the star on any card in{" "}
              <Link to="/explore">Explore</Link> to keep it here.
            </EmptyMessage>
          )}

          {saved.length > 0 && (
            <Link className="primary-button" to="/explore/saved">
              Study these as flashcards
              <span className="button-note">
                {saved.length} card{saved.length === 1 ? "" : "s"}
              </span>
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
                    aria-label={`Remove ${item.name} from my list`}
                    title="Remove from my list"
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
              {missing} saved item{missing === 1 ? " is" : "s are"} no longer in
              the catalog.
            </p>
          )}

          <p className="section-note">
            {isSignedIn ? (
              "Saved to your account, so they follow you to another device."
            ) : (
              <>
                Saved in this browser only.{" "}
                <Link to="/sign-in">Sign in</Link> to keep them.
              </>
            )}
          </p>
        </section>
      </div>
    </main>
  );
}

export default MyListPage;
