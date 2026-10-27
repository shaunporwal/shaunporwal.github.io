# PR 10: Picture-First Work Cards

Status: done

Branch: `feature/picture-first-cards`

## Goal

Each Work card on the home page leads with a picture, then the name and one short line. The picture is a looping clip, a logo or a sample decision curve. It matches the picture-first cards on the Junto hub.

## Context

- Shaun, 2026-10-27: every project card leads with its own visual and a one-line subtitle. No fact lists. No YouTube embed. Looping silent clips are fine.
- The four cards (Junto Technologies, ChemInventory, Bench Bridge, dcurves) had text only.
- The hub already holds the ChemInventory and Bench Bridge stills and clips, the Junto logo, and the decision curve maths (`assets/js/decision-curve.js`). This PR copies the files and mirrors the maths. It edits nothing in the hub.

## Implementation Checklist

Ordered from least consequential to most consequential. Tests come first.

### Tier 1 - Data and media

- [x] Test, then extend `data/site.schema.json`: each project has a `picture` of kind `clip`, `logo` or `decision-curve`, with the keys that kind needs.
- [x] Copy the two stills and four clips from the hub into `site/media/projects/`. Downscale the Junto logo to WebP (19 KB from 848 KB).
- [x] Test, then shorten each summary. Keep the dcurves wording "I created it at Memorial Sloan Kettering Cancer Center".
- [x] Test the media: each clip is 450 KB or less, each still is 100 KB or less, each still is 16:10, and every file is used.

### Tier 2 - Generators

- [x] Test, then add `scripts/lib_curve.py`: the decision curve maths and the plot geometry. Compare it with the hub values.
- [x] Test, then add `scripts/lib_curve_svg.py`: the inline SVG with no color and no style.
- [x] Test, then add `scripts/lib_pictures.py`: one renderer per kind, picked from a table.
- [x] Test, then change `render_card` in `scripts/sync_home.py`: picture, then name with the arrow, then one line.

### Tier 3 - Style and motion

- [x] Test, then add the 16:10 plate, the logo plate and the curve classes to `site/styles/site.css`. Every color is a token.
- [x] Test, then add the draw-in and the ring pulse. Both run only while the script marks the picture as playing. Reduced motion turns them off.
- [x] Test, then add the play rules to `site/js/motion.js`: play on screen only, pause when the tab is hidden, keep the still for reduced motion and `saveData`.
- [x] Test that no card says "software", holds an email address, or claims compliance.

### Tier 4 - Docs

- [x] Update `docs/development.md`, `site/AGENTS.md` and `tests/AGENTS.md`. Run `make sync` for the script list.

## Smoke Tests

Walked with Playwright Chromium at the tailnet link of the dev server (`make dev`).

- [x] **Phone, 360 and 390 px, light and dark** · scroll the Work section
  1. Open the home page and scroll to Work.

  **Pass if:** one column, the picture spans the card, nothing scrolls sideways, and the console has no error.

- [x] **Tablet and desktop, 820 and 1440 px, light and dark** · look at the two-column grid
  1. Open the home page and scroll to Work.

  **Pass if:** four balanced cards, equal margins, each picture 16:10 and inside its card.

- [x] **Playback** · scroll a clip off screen and on again
  1. Open the home page. Scroll until a clip shows.

  **Pass if:** the clip plays on screen and pauses off screen. The curve draws in and its point pulses.

- [x] **Reduced motion** · turn on "reduce motion"
  1. Open the home page and scroll to Work.

  **Pass if:** no clip plays. The curve is still.

- [x] **No script** · turn JavaScript off
  1. Open the home page.

  **Pass if:** each card shows its still, the curve is whole, and no player bar shows.

- [x] **Live site** · after the merge and the Pages run
  1. Open the live home page and scroll to Work.

  **Pass if:** the same result as the local walk.

## Product Decisions

- The Junto card shows the real logo on a quiet plate. The hub logo is 848 KB, so the site holds a 400 px WebP copy.
- The dcurves picture is generated inline SVG, not an image file. It uses the page tokens, so it follows the light and dark modes and holds no color literal. The visible note says "Illustration only. Not real data."
- Bench Bridge is a demo with sample data. The alt text says so. No card claims built hardware, compliance or a price.
- Summaries are one short line each. `llms.txt` shows the same lines, because it reads the same data.
- The card padding is 0.5 rem and the card radius is 1 rem, so the plate radius (0.5 rem) is concentric.

## Scope

- The four home page Work cards, their data, schema, generator, style, script, tests and docs.

## Non-Goals

- The hub, `cheminventory.co`, and the ChemInventory app repo. Nothing there changes.
- The About page, the Stuff page, the resume and the blog.
- A theme toggle. The site has no toggle, only `prefers-color-scheme`.

## Related Docs

- [PR 9: Alive Motion and Junto Wording](./9-alive-motion.md): the pointer light, `.lift` and the rise that these cards keep.
