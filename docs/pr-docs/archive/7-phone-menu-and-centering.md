# PR 7: Phone Menu and Centring

Status: done

Branch: `fix/phone-menu-and-centering`

## Goal

Make the phone menu look natural. Centre the phone layout of every page. Remove the phone bugs a full scan found.

## Context

- Shaun sent a screenshot of the menu on an iPhone browser. The four links sit about 120 px apart, with no rows and no structure. A WebKit browser stretched the grid rows over the whole panel. Chromium does not stretch them.
- The hero is centred, but the Work and Writing headings are left-aligned. Stuff and the 404 page also have a left-aligned heading above a centred caption.
- The footer links "X" and "Feed" are 9 px and 32 px wide. That is too small to tap.
- The resume shows a "Save as PDF" note and trailing `|` separators on a phone.

## Implementation Checklist

### Tier 1 - Phone layout

- [x] Centre each home section heading below 1024 px. Align it left from 1024 px, like the hero.
- [x] Add `page-plain` to Stuff and 404. Centre its heading and text.
- [x] Make each footer link at least 44 px wide.
- [x] Hide the resume print note and the contact separators on a phone. Stack the contact items.

### Tier 2 - Phone menu

- [x] Test, then make the panel `height: fit-content` and a flex column. Each row keeps its own height.
- [x] Give each row a hairline, a 52 px height and a larger label.
- [x] Mark the current page with a dot. Mark a link that opens a new tab with an arrow.
- [x] Round the bottom corners. Add the soft shadow as the `shadow-menu` theme token.
- [x] Pull the menu button right so its icon lines up with the page gutter.

### Tier 3 - Ship

- [x] `make test` passes (295 tests).
- [x] Audit all 15 pages at 360, 390 and 430 px: no broken image, no off-centre text, no small target.
- [x] Walk five sizes in light and dark: no sideways scroll, no console error.
- [x] Merge the PR. Merged as `a85f55c`. The publish run passed. The live site passed the audit at 360, 390 and 430 px in light and dark.

## Smoke Tests

- [ ] **Menu on a phone** · as Shaun
  1. Open shaunporwal.com on the iPhone browser. Tap the menu button.

  **Pass if:**
  - The links sit in rows about 52 px tall, with a line between them.
  - The panel ends under the Book a call button.
  - The current page shows a dot. Resume shows an arrow.
- [ ] **Home on a phone** · as Shaun
  1. Scroll the home page.

  **Pass if:** the Work and Writing headings sit in the centre, like the hero.

## Product Decisions

- Centre the headings of short pages. Keep posts and lists left-aligned, because long text reads better that way.
- No scrim behind the menu. A scrim would dim the header and its close button.
- The menu cannot be tested in WebKit here, because no WebKit browser is installed. The panel now has no way to stretch, in any engine.

## Scope

- `site/styles/site.css`, the Stuff, 404 and resume pages, the theme token, the menu test.

## Non-Goals

- No new pages, no text edits to posts.
- Five older posts show "(content missing)". They are drafts and stay unlisted.

## Related Docs

- [PR 6: Shared Theme, Editorial Restyle and Agent Files](./6-shared-theme-and-agent-files.md)
