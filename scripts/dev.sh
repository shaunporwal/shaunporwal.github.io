#!/usr/bin/env bash
# Local dev server for site/. Prefers live-server (via npx, no repo dependency,
# nothing committed) for hot reload on save; falls back to python's plain
# static server if npx/Node isn't available.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
port="${PORT:-8000}"

if command -v npx >/dev/null 2>&1; then
  echo "Starting live-server (hot reload) on http://localhost:${port} ..."
  exec npx --yes live-server "$repo_root/site" --port="$port"
else
  echo "npx not found; falling back to python3 -m http.server (no hot reload)."
  echo "Serving http://localhost:${port} ..."
  cd "$repo_root/site"
  exec python3 -m http.server "$port"
fi
