# PR 18: uv-only backlog

Status: underway

Branch: `chore/uv-only-backlog`

## Goal

`make` and the tests workflow start Python only through `uv`. One publish-workflow hit stays, listed under Non-Goals.

## Context

The `uv-only` rule lints changed lines only. A full scan (`ops check --all --lint-only`) finds 3 older hits: `Makefile:3` (`PYTHON ?= python3`), `.github/workflows/test.yaml:19` (`pipx install`), `.github/workflows/publish.yaml:18` (`python3`). All scripts and tests import only the standard library.

## Implementation Checklist

### Tier 1 - Tests first

- [ ] `tests/test_uv_only.py`: the Makefile default starts with `uv run`, the pre-commit hook does not restate it, the tests workflow uses `astral-sh/setup-uv` and `uv tool install`, and no `pipx`. Fails first.

### Tier 2 - Make and hook

- [ ] `Makefile`: `PYTHON ?= uv run --quiet --no-project python`.
- [ ] `.githooks/pre-commit`: drop the `PYTHON` export. The Makefile default now holds it.

### Tier 3 - CI

- [ ] `test.yaml`: add `astral-sh/setup-uv` (same pin as swarm-infra). Install ruff with `uv tool install`, version still read from `ruff.toml`.

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

- 2 of 3 `uv-only` hits.

## Non-Goals

- `.github/workflows/publish.yaml:18` stays `python3 scripts/render_pdf.py`. It is the production publish path. A by-hand test would publish to GitHub Pages. Decision pending (Shaun).

## Rollback

- Revert the merge commit. No site output changes.
