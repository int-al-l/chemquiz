#!/usr/bin/env bash
# Deploys main to the public site on HONOR (WSL ~/work/chemquiz, tmux session chemquiz).
#
#   tools/deploy-honor.sh [sha]    deploy origin/main (or sha) now, no CI check
#   tools/deploy-honor.sh --watch  every 2 min: if origin/main moved and CI on it
#                                  is green, deploy it (tmux window chemquiz:deploy,
#                                  started by ~/bin/chemquiz-boot)
#
# Pull-based on purpose: the repo is public, so no self-hosted runner, and
# HONOR needs no inbound access or secrets.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/node/bin:$PATH"
REPO=int-al-l/chemquiz

log() { echo "$(date '+%F %T') $*"; }

ci_green() {  # CI jobs (ci.yml: frontend, backend) succeeded on commit $1
  local sha=$1 runs
  # Pages rebuilds ([skip ci]) carry the code of the commit below them: check that one
  while [[ $(git log -1 --format=%B "$sha") == *'[skip ci]'* ]]; do sha=$(git rev-parse "$sha^"); done
  runs=$(curl -fsS -m 30 "https://api.github.com/repos/$REPO/commits/$sha/check-runs?per_page=100") || return 1
  python3 -c 'import json, sys
runs = {r["name"]: r["conclusion"] for r in json.load(sys.stdin)["check_runs"]}
sys.exit(0 if runs.get("frontend") == runs.get("backend") == "success" else 1)' <<<"$runs"
}

deploy() {
  local old new
  old=$(git rev-parse HEAD)
  new=$(git rev-parse "$1")
  log "deploying $(git log -1 --format='%h %s' "$new")"

  cp backend/chemquiz.db "backend/chemquiz.db.bak-$(date +%Y%m%d-%H%M%S)"
  ls -t backend/chemquiz.db.bak-* | tail -n +11 | xargs -r rm --  # keep the last 10

  git merge --ff-only -q "$new"
  changed() { ! git diff --quiet "$old" "$new" -- "$@"; }
  if changed backend/requirements.txt; then
    # only the site's deps; the catalog pipeline ones below that comment are heavy
    backend/.venv/bin/pip install -q -r <(sed '/^# the content pipelines/,$d' backend/requirements.txt)
  fi
  if changed backend/seed_data.py backend/content_ru.py backend/app/seeding.py; then
    # card texts live in the database; the backend only seeds an empty one.
    # Upsert by slug: accounts and custom quizzes stay, dropped cards go.
    (cd backend && .venv/bin/python seed.py) || log "seed.py: see the warnings above"  # exits 1 on a missing photo
  fi
  if changed package-lock.json; then npm ci --no-audit --no-fund; fi
  npm run build

  # same commands as when ~/bin/chemquiz-boot created the windows
  tmux respawn-window -k -t chemquiz:backend
  tmux respawn-window -k -t chemquiz:frontend
  curl -fsS -o /dev/null --retry 15 --retry-connrefused --retry-delay 2 http://127.0.0.1:8000/api/health
  curl -fsS -o /dev/null --retry 15 --retry-connrefused --retry-delay 2 http://127.0.0.1:4173/
  log "deployed $(git log -1 --format=%h), site is up"
}

if [ "${1:-}" != --watch ]; then
  [ -n "${1:-}" ] || git fetch -q origin main
  deploy "${1:-origin/main}"
  exit
fi

log "watching origin/main"
while sleep 120; do
  git fetch -q origin main || continue
  sha=$(git rev-parse origin/main)
  [ "$sha" = "$(git rev-parse HEAD)" ] && continue
  ci_green "$sha" || continue  # CI still running or red: try again next round
  # a separate process so `set -e` works; after a deploy re-exec to pick up a new version of this script
  if "$0" "$sha"; then exec "$0" --watch; fi
  log "DEPLOY FAILED, see above; the site may be down until it is fixed (backup in backend/chemquiz.db.bak-*)"
done
