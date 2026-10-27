#!/usr/bin/env bash
# Local dev server for site/. Binds all interfaces and prints only the tailnet link.
# Uses live-server (via npx, no repo dependency) for hot reload. Falls back to
# Python's plain static server (run through uv) if npx is missing. Server output goes to a log file.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
port="${PORT:-8000}"
log="${TMPDIR:-/tmp}/shaunporwal-site-dev-${port}.log"

# The machine's tailnet name, without the trailing dot. Falls back to the host name.
tailnet_host() {
  tailscale status --json 2>/dev/null | jq -r '.Self.DNSName // empty' | sed 's/\.$//' || true
}

port_is_busy() {
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

serve() {
  if command -v npx >/dev/null 2>&1; then
    npx --yes live-server "$repo_root/site" --host=0.0.0.0 --port="$port" --no-browser --quiet
  else
    cd "$repo_root/site"
    uv run --no-project python -m http.server "$port" --bind 0.0.0.0
  fi
}

if port_is_busy; then
  echo "Port ${port} is busy. Free it, or run: PORT=<free port> make dev" >&2
  exit 1
fi

host="$(tailnet_host)"
echo "http://${host:-$(hostname)}:${port}"

status=0
serve >"$log" 2>&1 || status=$?
if [ "$status" -ne 0 ] && [ "$status" -ne 130 ]; then
  echo "Dev server stopped with status ${status}. Log: ${log}" >&2
  exit "$status"
fi
