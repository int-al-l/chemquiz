import { useCallback, useEffect, useState } from "react";

/**
 * Run an async function on mount and whenever `deps` change, tracking the
 * loading and error states so pages do not each rewrite the same three
 * useStates.
 *
 * Loading is *derived*, not stored: state carries the key of the request it
 * came from, and anything whose key is not the current one is stale, which is
 * exactly what "loading" means. That avoids setting state synchronously inside
 * the effect, and it also fixes the out-of-order problem for free -- navigating
 * quickly between two categories can no longer leave the first response
 * overwriting the second, because a late reply carries an old key.
 *
 * `deps` must be JSON-serialisable; in practice they are route params.
 */
export function useApi(loader, deps = []) {
  const [reloadKey, setReloadKey] = useState(0);
  const key = JSON.stringify([...deps, reloadKey]);

  const [state, setState] = useState({ key: null, data: null, error: null });

  const reload = useCallback(() => setReloadKey((n) => n + 1), []);

  useEffect(() => {
    let active = true;

    loader()
      .then((data) => {
        if (active) setState({ key, data, error: null });
      })
      .catch((error) => {
        if (active) setState({ key, data: null, error });
      });

    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const settled = state.key === key;

  return {
    data: settled ? state.data : null,
    error: settled ? state.error : null,
    loading: !settled,
    reload,
  };
}
