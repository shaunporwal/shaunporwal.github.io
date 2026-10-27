# PR 8: Monthly Download Refresh

Status: done

Branch: `feature/refresh-downloads`

## Goal

Keep the dcurves download count in `resume.html` fresh with no manual step. A monthly workflow pushes the new count to `main`.

## Context

- The count refreshes only when someone commits, because the pre-commit hook runs the refresh script.
- Shaun, 2026-10-27: the refresh should be automatic. It is inconsequential, so no PR and a push straight to `main`.
- A push made with the workflow token does not start other push workflows. The publish workflow would not run.

## Implementation Checklist

### Tier 1 - Script and workflow

- [x] Test, then add `scripts/commit-downloads.sh`. It refreshes the count, accepts only the one-line change, and pushes as the bot.
- [x] Add `.github/workflows/refresh-downloads.yaml`: monthly cron, by-hand run, `contents: write` and `actions: write` only.
- [x] Start `publish.yaml` from the refresh, because a token push does not start it.
- [x] Add a `republish` switch to the by-hand run, so the publish step has a test path.
- [x] Add `tests/test_refresh_workflow.py`.

### Tier 2 - Docs and ship

- [x] Update `docs/development.md` and `AGENTS.md`.
- [x] Run the script against a local bare repository: it pushes as the bot.
- [x] Merge the PR. Merged as `3e0b765`. A by-hand run with `republish` on was green, logged "No change" and started a publish run (`workflow_dispatch`) that passed.

## Smoke Tests

- [x] **Refresh run** · as Shaun
  1. Open the Actions tab. Run "Refresh dcurves downloads" with `republish` on.

  **Pass if:** the run is green, the log says "No change", and a "Publish static site" run follows.

## Product Decisions

- The count shows in thousands, rounded down, so the workflow commits about once for each 1,000 new downloads.
- The script stops with an error when the diff is more than the one count line.

## Scope

- One script, one workflow, one test, two docs.

## Non-Goals

- No change to the hook, to the count format or to `resume.html` itself.

## Related Docs

- [PR 7: Phone Menu and Centring](./7-phone-menu-and-centering.md)
