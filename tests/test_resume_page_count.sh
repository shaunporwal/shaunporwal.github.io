#!/usr/bin/env bash
# Guards against the resume silently growing past 2 printed pages as bullets
# get added over time. Renders site/resume.html to PDF via `npx playwright`
# (ad hoc, nothing added to the repo) and counts pages. Run via:
#   bash tests/test_resume_page_count.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
resume_file="$repo_root/site/resume.html"
max_pages=2
tmp_dir="$(mktemp -d)"
tmp_pdf="$tmp_dir/resume.pdf"
trap 'rm -rf "$tmp_dir"' EXIT

if ! command -v npx >/dev/null 2>&1; then
  echo "test_resume_page_count: npx not found, skipping (install Node to run this check)" >&2
  exit 0
fi

npx --yes playwright pdf "file://$resume_file" "$tmp_pdf" >/dev/null 2>&1

# Page objects (/Type /Page, not /Type /Pages) are one per printed page in a
# Chromium-generated PDF; \b distinguishes the two (a plain substring match
# would double-count /Pages as containing /Page).
pages=$(grep -aoE '/Type */Page\b' "$tmp_pdf" | wc -l | tr -d ' ')

if [[ -z "$pages" || "$pages" -eq 0 ]]; then
  echo "test_resume_page_count: could not determine page count from $tmp_pdf" >&2
  exit 1
fi

echo "resume.html prints to ${pages} page(s) (max: ${max_pages})"

if [[ "$pages" -gt "$max_pages" ]]; then
  echo "FAIL: resume.html now prints to ${pages} pages, exceeding the ${max_pages}-page budget." >&2
  echo "Trim a bullet in data/resume.json, or tighten @media print in site/resume.html." >&2
  exit 1
fi

echo "OK: resume.html fits within ${max_pages} pages"
