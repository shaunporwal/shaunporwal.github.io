# PR 3: Zero-Overhead 3D Print Shop & Multi-Channel Sales Funnel

Status: underway

Branch: `feature/3d-print-shop`

## Goal

Add a standalone 3D print shop section to the existing personal site with Stripe Payment Links for zero-overhead, instant checkout, while establishing cross-listing on Etsy and automated fulfillment via Pirate Ship.

## Context

The personal site lacks e-commerce capabilities. This PR introduces a dedicated landing page (`/shop` or hosted route) that leverages Stripe-hosted checkout and Stripe Payment Link Web Components (`<stripe-buy-button>`) to collect payments, calculate shipping, and capture customer addresses with zero custom backend API endpoints required.

**Reoriented after PR 4:** the site is no longer Quarto-based. It's now plain static HTML/CSS under `site/`, with a shared nav template (`templates/nav.html`, stamped into every page by `scripts/sync_nav.py`), site-wide constants in `data/site.json`, and SEO/sitemap generation scripts — see `docs/development.md` for the current conventions. `/shop` should be a new `site/shop.html` following that pattern (nav/SEO markers copied from an existing page, wired into `templates/nav.html` and `data/site.json`/`scripts/gen_sitemap.py` like any other page), not a Quarto page.

## Implementation Checklist

### Tier 1 — Quick Wins & Account Configuration (Low risk, isolated)

- [ ] Register and configure Stripe Account. Enable Stripe Checkout, set business details, and configure branding (logo/colors).
- [ ] Create 3D Print Product Catalog in Stripe Dashboard. Define prices, configure shipping address collection rules, and add flat-rate/calculated shipping options.
- [ ] Create Pirate Ship account. Connect Stripe and Etsy integrations for $0/mo Commercial Base Rate label importing.
- [ ] Create Etsy Seller Storefront. Mirror product titles, descriptions, and high-resolution print photos to capture organic marketplace traffic.

### Tier 2 — Frontend Integration & Web Components (Static UI & routing)

- [ ] Create `site/shop.html` (static HTML, same nav/SEO marker pattern as `site/about.html`/`site/stuff.html`). Build a responsive product grid displaying product photos, descriptions, specs (dimensions, materials), and inventory status.
- [ ] Embed Stripe Buy Buttons via `<stripe-buy-button>` Web Components or direct Stripe Payment Links per product card.
- [ ] Add a "Shop" link to `templates/nav.html` (propagates to every page via `scripts/sync_nav.py`); add `shop.html` to `scripts/gen_sitemap.py`'s `TOP_LEVEL_PAGES`.
- [ ] Test client-side redirects to ensure buyers return to `/shop?status=success` post-purchase.

### Tier 3 — Multi-Channel Launch & Cross-Linking (External channels)

- [ ] Generate shortened social checkout links for X/Twitter posts.
- [ ] Add Etsy product links as cross-channel fallback options on `/shop`.
- [ ] Publish demonstration videos/photos of prints on X/Twitter with direct shop links in replies.

## Smoke Tests

- [ ] Click `<stripe-buy-button>` on `/shop` → Correct Stripe-hosted Checkout opens with item, price, and shipping fields.
- [ ] Complete test purchase in Stripe Test Mode → Order appears instantly in Stripe Dashboard with full shipping address.
- [ ] Verify Pirate Ship integration → Stripe Test/Live order imports into Pirate Ship with pre-filled address ready for label purchase.
- [ ] Access `/shop` from mobile device → Responsive grid renders cleanly and redirects to Stripe Checkout without layout breakages.

## Product Decisions

- **Stripe Payment Links over Custom API:** Using Stripe's hosted checkout via Web Components eliminates the need to build and maintain custom backend serverless endpoints (`/create-checkout-session`, webhook handlers) or manage session states, reducing setup time to under an hour.
- **Hybrid Multi-Channel Approach:** Hosting shop on personal site maximizes margins (2.9% + $0.30 fee), while mirroring on Etsy taps into existing search discovery.
- **Pirate Ship for Shipping:** Chosen over native platform shipping label purchasing due to lower Commercial Base Rates and direct $0/mo multi-channel synchronization with both Stripe and Etsy.

## Scope

- Resolves requirement for a $0/month fixed-cost e-commerce setup.
- Resolves demand for frictionless X/Twitter link sharing to direct checkout.
- Enables physical address collection and payment processing for physical prints.

## Non-Goals

- Building custom shopping cart software, database models, or backend webhooks.
- Selling digital Stereolithography (STL) files or design licenses.
- Managing automated real-time inventory tracking (manual quantity caps via Stripe suffice for early launch).

## Related Docs

- None.
