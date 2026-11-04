# PR 18: uv-only backlog

Status: underway

Branch: `chore/uv-only-backlog`

## Goal

`make`, the pre-commit hook, the tests workflow and every script shebang start Python only through `uv`. One publish-workflow hit stays, listed under Non-Goals.

## Context

The `uv-only` rule lints changed lines only. A full scan (`ops check --all --lint-only`) found 3 hits: `Makefile:3` (`PYTHON ?= python3`), `.github/workflows/test.yaml:19` (`pipx install`), `.github/workflows/publish.yaml:18` (`python3`). The checker then gained the shebang rule (agent-skills PR 56): 18 more hits, `#!/usr/bin/env python3` in `scripts/*.py`. All scripts and tests import only the standard library.

## Implementation Checklist

### Tier 1 - Tests first

- [x] `tests/test_uv_only.py`: the Makefile default starts with `uv run`, the pre-commit hook does not restate it, the tests workflow uses `astral-sh/setup-uv` and `uv tool install` and no `pipx`, every script shebang is the uv one. Failed first.

### Tier 2 - Make, hook, scripts

- [x] `Makefile`: `PYTHON ?= uv run --quiet --no-project python`.
- [x] `.githooks/pre-commit`: drop the `PYTHON` export. The Makefile default now holds it.
- [x] 18 `scripts/*.py`: line 1 becomes `#!/usr/bin/env -S uv run --script`. No file is executable, nothing runs a script by its shebang.

### Tier 3 - CI

- [x] `test.yaml`: add `astral-sh/setup-uv` (same pin as swarm-infra). Install ruff with `uv tool install`, version still read from `ruff.toml`.

## Smoke Tests

Not applicable: no UI, no site output change. Covered by:

| Check | Covered by |
|---|---|
| Generators and tests run under uv | `make test`, `make sync` (no site diff) |
| Tests workflow green on the runner | PR check |
| No uv-only hit left in scope | `ops check --all --lint-only` |

## Product Decisions

- No Python pin in CI. `uv` takes the runner Python (3.12), as `python3` did before.
- The Makefile default is the one home of the uv command. The hook no longer sets it.

## Scope

- 20 of 21 `uv-only` hits (2 in the Makefile and `test.yaml`, 18 shebangs).
- Proved: `make test` passes locally (ruff clean, 473 tests OK). `make sync` leaves no diff.

## Non-Goals

- `.github/workflows/publish.yaml:18` stays `python3 scripts/render_pdf.py`. It is the production publish path. A by-hand test would publish to GitHub Pages. Decision pending (Shaun).

## Rollback

- Revert the merge commit. No site output changes.
