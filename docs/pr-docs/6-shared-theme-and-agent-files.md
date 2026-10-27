# PR 6: Shared Theme, Editorial Restyle and Agent Files

Status: underway

Branch: `feature/shared-theme-and-agent-files`

## Goal

Restyle shaunporwal.com on the same theme as cheminventory.co. Keep its tokens, layout grid and motion. Give this site an editorial style. Add the search and agent files that every public Junto site has.

## Context

The site uses a navy, cream and apricot palette with no motion. cheminventory.co uses one accent on a quiet neutral base, a sticky header, scroll reveal, a sliding nav indicator and a card lift. Shaun wants one theme for all his sites, with a different style on each.

`llms.txt` and the About page JSON-LD contain an email address. The site has no `agents.txt`, no `.well-known/agents.json`, no feed and no 404 page. `robots.txt` names no AI crawler.

## Implementation Checklist

Ordered from least consequential/complex to highest blast radius. Follow TDD:
write the focused failing test before implementing changed behavior.

### Tier 1 — Safe fixes and tooling

- [ ] Test, then remove the email address from `llms.txt` and the Person JSON-LD.
- [ ] Add a `PYTHON` variable to the `Makefile`, so `uv` can run every generator.
- [ ] Make `scripts/dev.sh` bind all interfaces and print only the tailnet link.
- [ ] Allow a JavaScript file and a CSS block to carry generated markers in `lib_blocks.py`.

### Tier 2 — Search and agent files

- [ ] Add a `seo` section to `data/site.json` and its schema: crawlers, agent rules.
- [ ] Generate `robots.txt` with each crawler named.
- [ ] Generate `agents.txt` and `.well-known/agents.json`.
- [ ] Generate `llms.txt` with Work and Elsewhere sections, and a link to `llms-full.txt`.
- [ ] Generate `llms-full.txt`: the full text of each published post.
- [ ] Generate `feed.xml` (Atom) and the feed link in each page head.
- [ ] Add `404.html` with `noindex`. Add a `noindex` switch to `data/pages.json`.
- [ ] Add WebSite and Person JSON-LD with `sameAs`, `jobTitle` and `worksFor`. Add BreadcrumbList to posts.
- [ ] Add `theme-color`, an SVG favicon, an Apple touch icon and a web manifest.

### Tier 3 — Theme and restyle

- [ ] Add `data/theme.json` and its schema. Generate the token block in `site/styles/site.css`.
- [ ] Rewrite `site/styles/site.css`: shell, grid, header, popover menu, buttons, lift, reveal, hero entrance, serif display type.
- [ ] Add `site/js/motion.js`: scroll reveal, header state, sliding nav indicator. Pages must work without it.
- [ ] Add a JavaScript code-shape test: docstring, no arrow functions, no nested functions, 15 lines per function.
- [ ] Rewrite `templates/nav.html`. Add `templates/footer.html` and `scripts/sync_footer.py`. Mark the current page.
- [ ] Generate the home hero from `data/site.json` and the current role. Generate the Work cards from `projects` in `data/site.json`.
- [ ] Restyle the blog listing, About, Stuff and post pages.
- [ ] Render a new Open Graph image in the new theme.

### Tier 4 — Ship

- [ ] Run `make test` with `ruff`. All checks must pass.
- [ ] Walk every page at 360, 390, 430, 820 and 1440 px, light and dark, on the tailnet link.
- [ ] Update `AGENTS.md`, `site/AGENTS.md`, `data/AGENTS.md`, `templates/AGENTS.md` and `docs/development.md`.
- [ ] Merge the PR. Shaun authorized the merge on 2026-10-27. Watch the publish run. Check the live site.

## Smoke Tests

Run on the tailnet dev link, then on the live site after the merge.

- [ ] Home at 1440 px: hero, Work cards and Writing list show. The nav indicator slides under the hovered link.
- [ ] Home at 390 px: no sideways scroll. The buttons share one width. The menu button opens the popover.
- [ ] Dark mode follows the operating system. Text keeps its contrast.
- [ ] With reduced motion on: nothing animates and all content shows.
- [ ] One post: the reading column is narrow. Images fit. The nav marks Blog as current.
- [ ] `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/llms-full.txt`, `/agents.txt`, `/.well-known/agents.json` and `/feed.xml` return 200 with the right type.
- [ ] A missing URL shows the 404 page.
- [ ] `resume.html` still prints with clean page breaks.

## Product Decisions

- The accent is a warm vermilion, close to the apricot and coral of the old palette. The neutrals, radius, motion and grid match cheminventory.co.
- Display type is a system serif stack. Body type on the pages is the system sans stack. Post bodies use the serif stack for long reading.
- One small first-party script carries the motion. It adds no framework, no build step and no third-party code. Every page works without it.
- The email address stays out of every generated and search file. The About page and the resume keep their existing visible email link.
- The summary drops the word "compliance". It says "chemical inventory software".
- Work cards link the other Junto sites. The facts come from `data/site.json`.

## Scope

- The theme, the home, About, Stuff, post and 404 pages.
- The generated search and agent files.
- Tooling: `Makefile`, `dev.sh`, the JavaScript shape test.

## Non-Goals

- `resume.html` keeps its own print palette and layout.
- No new posts, no text edits to existing posts.
- No analytics, tracking or third-party script.
- No search console or webmaster account setup. Those need Shaun's login.

## Related Docs

- [PR 3: 3D Print Shop](./3-3d-print-shop.md)
