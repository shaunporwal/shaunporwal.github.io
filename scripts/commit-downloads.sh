#!/usr/bin/env bash
# Refreshes the dcurves download count in resume.html, then commits and pushes the change to main as the bot.
# Run by .github/workflows/refresh-downloads.yaml. Writes changed=true or changed=false to $GITHUB_OUTPUT.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
resume="site/resume.html"
output="${GITHUB_OUTPUT:-/dev/null}"

cd "$repo_root"
./scripts/update-dcurves-downloads.sh

# Only lines that hold the count may change. Any other change means the page moved under the script.
diff_lines="$(git diff -U0 -- "$resume" | grep -E '^[+-][^+-]' || true)"
if [ -z "$diff_lines" ]; then
  echo "changed=false" >>"$output"
  echo "No change: the count is the same."
  exit 0
fi
if printf '%s\n' "$diff_lines" | grep -qv 'class="dcurves-downloads"'; then
  echo "Unexpected change in ${resume} outside the count. Nothing pushed." >&2
  exit 1
fi

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git commit -q -m "chore: refresh the dcurves download count" -- "$resume"
git push -q origin HEAD:main
echo "changed=true" >>"$output"
echo "Pushed the new count to main."
