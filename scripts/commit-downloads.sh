#!/usr/bin/env bash
# Refreshes the dcurves download count in resume.html, then commits and pushes the change to main as the bot.
# Run by .github/workflows/refresh-downloads.yml. Writes changed=true or changed=false to $GITHUB_OUTPUT.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
resume="site/resume.html"
output="${GITHUB_OUTPUT:-/dev/null}"

cd "$repo_root"
./scripts/update-dcurves-downloads.sh

# Only the one count line may change. Any other change means the page moved under the script.
changed_lines="$(git diff -U0 -- "$resume" | grep -cE '^[+-][^+-]' || true)"
if [ "$changed_lines" -eq 0 ]; then
  echo "changed=false" >>"$output"
  echo "No change: the count is the same."
  exit 0
fi
if [ "$changed_lines" -ne 2 ]; then
  echo "Unexpected diff of ${changed_lines} lines in ${resume}. Nothing pushed." >&2
  exit 1
fi

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git commit -q -m "chore: refresh the dcurves download count" -- "$resume"
git push -q origin HEAD:main
echo "changed=true" >>"$output"
echo "Pushed the new count to main."
