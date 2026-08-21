#!/usr/bin/env bash
# Refreshes the dcurves PyPI download count shown in resume.html from pepy.tech's
# public badge endpoint (no API key required, unlike api.pepy.tech).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
resume_file="$repo_root/site/resume.html"

raw=$(curl -fsS "https://static.pepy.tech/personalized-badge/dcurves?period=total&units=none&left_color=grey&right_color=blue&left_text=downloads")
count=$(printf '%s' "$raw" | grep -oE '>[0-9,]+<' | tail -1 | tr -d '><,')

if [[ -z "$count" ]]; then
  echo "update-dcurves-downloads: could not parse download count, leaving resume.html unchanged" >&2
  exit 0
fi

thousands=$((count / 1000))
label="${thousands}k+"

sed -i.bak -E "s#(class=\"dcurves-downloads\">)[^<]*(<)#\1${label}\2#g" "$resume_file"
rm -f "$resume_file.bak"

echo "update-dcurves-downloads: dcurves-downloads set to ${label} (raw: ${count})"
