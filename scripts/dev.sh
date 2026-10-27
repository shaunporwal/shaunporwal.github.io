#!/usr/bin/env bash
# Local dev server for site/. Binds all interfaces and prints only the tailnet link.
# Uses live-server (via npx, no repo dependency) for hot reload. Falls back to
# Python's plain static server if npx is missing.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
port="${PORT:-8000}"

# The machine's tailnet name, without the trailing dot. Falls back to the host name.
host="$(tailscale status --json 2>/dev/null | jq -r '.Self.DNSName // empty' | sed 's/\.$//' || true)"
echo "http://${host:-$(hostname)}:${port}"

if command -v npx >/dev/null 2>&1; then
  exec npx --yes live-server "$repo_root/site" --host=0.0.0.0 --port="$port" --no-browser --quiet >/dev/null 2>&1
else
  cd "$repo_root/site"
  exec uv run --no-project python -m http.server "$port" --bind 0.0.0.0 >/dev/null 2>&1
fi
