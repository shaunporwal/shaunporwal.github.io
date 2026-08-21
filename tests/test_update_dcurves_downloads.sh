#!/usr/bin/env bash
# Unit test for update-dcurves-downloads.sh's parsing/rewrite logic, without
# hitting the network: feeds a fixture pepy.tech badge SVG through the same
# extraction the script uses, and checks the sed rewrite against a fixture
# resume.html. Run via: bash tests/test_update_dcurves_downloads.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

# --- test 1: count extraction from a fixture SVG badge (units=none shape: bare integer) ---
fixture_svg_int='<svg><text>downloads</text><text x="835" y="140">72027</text></svg>'
extracted_int=$(printf '%s' "$fixture_svg_int" | grep -oE '>[0-9,]+<' | tail -1 | tr -d '><,')
[[ "$extracted_int" == "72027" ]] || fail "expected 72027, got '$extracted_int'"

# --- test 2: the sed rewrite updates both spans and only the target class ---
fixture_html="$tmp_dir/resume.html"
cat > "$fixture_html" <<'EOF'
<li>Downloads: <span class="dcurves-downloads">1k+</span></li>
<div><span class="dcurves-downloads">1k+</span> PyPI downloads</div>
<span class="other-class">1k+</span>
EOF

label="72k+"
sed -i.bak -E "s#(class=\"dcurves-downloads\">)[^<]*(<)#\1${label}\2#g" "$fixture_html"
rm -f "$fixture_html.bak"

count_updated=$(grep -c "dcurves-downloads\">${label}<" "$fixture_html")
[[ "$count_updated" -eq 2 ]] || fail "expected 2 spans updated, got $count_updated"
grep -q 'other-class">1k+<' "$fixture_html" || fail "unrelated span with class=other-class was modified"

echo "OK: update-dcurves-downloads parsing/rewrite logic (2 checks)"
