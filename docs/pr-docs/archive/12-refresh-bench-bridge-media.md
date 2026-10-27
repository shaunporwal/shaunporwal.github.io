# PR 12: Refresh the Bench Bridge and ChemInventory Pictures

Status: done (merged on 2026-10-27, commit `1c65b34`)

Branch: `chore/refresh-bench-bridge-media`

## Goal

The Work cards show the current look of Bench Bridge and ChemInventory. The files match the hub files byte for byte.

## Context

- Bench Bridge now has a sample-data tag, calm motion cues and larger touch targets. The cards here still showed the old look.
- The hub recorded both pictures again (hub PR 21). PR 10 copied the first set from the hub.

## Implementation Checklist

- [x] Copy the two stills and the four clips from the hub into `site/media/projects/`.
- [x] Run `make test`. Each clip is 450 KB or less. Each still is 100 KB or less.
- [x] Keep the alt text. It still describes the new picture.

## Smoke Tests

- [x] The live files equal the hub files byte for byte (the agent compared all six with `cmp` on 2026-10-27).
- [ ] Play the clips on a phone. The agent did not watch them play.

## Product Decisions

- Copy the files from the hub. Do not record them again here. One recording keeps both sites equal.

## Scope

- Six media files.

## Non-Goals

- No change to the page, the data or the code.

## Related Docs

- [PR 10: Picture-First Work Cards](./10-picture-first-cards.md)
