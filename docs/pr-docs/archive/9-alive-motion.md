# PR 9: Alive Motion and Junto Wording

Status: done

Branch: `feature/alive-motion`

## Goal

Make the site feel alive and modern with a few quiet effects, and stop calling Junto a software company. The effects follow the same kit as the hub (`juntotechnologies.com`).

## Context

- Shaun, 2026-10-27: study two designer sites for the "alive" idea, apply it to the hub first, then this site, then cheminventory.co. Take ideas only. Do not copy code, text or images.
- Shaun, 2026-10-27: Junto is not a software brand. It also connects older instruments and moves into hardware.
- The site already has a scroll reveal, a header hairline and a sliding nav marker.
- A research note rates the effects by gain for effort. A library review found no outside component worth copying. Each effect here is written by hand.

## Implementation Checklist

Ordered from least consequential to most consequential.

### Tier 1 - Wording

- [x] Test, then change the Junto card, the llms.txt line and the home lead so none says "software" for Junto. The resume job title and the resume text keep their facts.

### Tier 2 - Theme tokens

- [x] Add the glow, sheen and raised-surface tokens to `data/theme.json` and its schema. Add the timing tokens.
- [x] Test the new tokens in the generated block.

### Tier 3 - Effects

- [x] A light follows the pointer on buttons and cards (`motion.js` writes `--gx` and `--gy`; CSS draws and eases it).
- [x] Raised button surfaces and a press that dips.
- [x] The main hero button gets a light that circles its edge.
- [x] The hero enters with a small scale and blur. Dots near the pointer light up in the hero.
- [x] The header gets a soft shadow after a scroll.
- [x] A CSS test: each effect is off under reduced motion, and hover effects sit inside `(hover: hover)`.

## Smoke Tests

Manual checks Shaun performs in the previewed site.

- [x] **Home on a desktop** · move the pointer over the hero and the buttons
  1. Open the home page in a desktop browser.

  **Pass if:** dots light up near the pointer, buttons and cards show a soft light, and the main button has a light that circles its edge.

- [x] **Home on a phone** · scroll the page
  1. Open the home page on a phone.

  **Pass if:** no hover effect shows, nothing scrolls sideways, and the header shows a soft shadow after you scroll.

- [x] **Reduced motion** · turn on "reduce motion" in the system settings
  1. Open the home page.

  **Pass if:** the page is still. No light circles the button.

## Product Decisions

- The effects use the vermilion accent and the existing neutrals. No new color family.
- No effect states a fact. The text of the page does not change, except the Junto wording.
- The site keeps one script. The glow code lives in `site/js/motion.js`.

## Scope

- One stylesheet, one script, the theme data, the Junto wording and the tests for them.

## Non-Goals

- No local time, no status line and no video. Those need facts only Shaun can state.
- No outside component library.
- No change to the resume layout or to the print styles.

## Related Docs

- [PR 7: Phone Menu and Centring](./7-phone-menu-and-centering.md)
