# site/

This directory is the published website. GitHub Pages serves it as it is, with no build step. A push to `main` publishes it. Shaun authorized merges to `main` on 2026-10-27. See the root `AGENTS.md`.

## What Is Hand-Written

- The page content of `index.html`, `about.html`, `stuff.html`, `404.html`, and each `posts/<slug>/index.html`, outside the marker blocks.
- `styles/site.css` outside its generated `THEME` block, `js/motion.js`, and the inline styles in `resume.html`. Every color in `site.css` is a token in its `:root` block. `tests/test_css_tokens.py` fails on a color literal anywhere else. The resume keeps its own print palette.
- Files in `media/` and the images in each post directory.

## What Is Generated

- Every block between `<!-- NAME:START -->` and `<!-- NAME:END -->` markers: the nav, the SEO tags, the social blocks, the blog listing, and the resume body.
- The `<title>` of every page and post. `sync_seo.py` writes it from `data/pages.json`, or from a post's heading.
- The `THEME` block of `styles/site.css`, from `data/theme.json`.
- `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, `agents.txt`, `.well-known/agents.json`, `feed.xml`, `manifest.webmanifest`, and `CNAME`.
- `media/favicon.svg`, from the light colors in `data/theme.json`.

The PNG icons and `media/og-image.jpg` are rendered files. No generator makes them, because the generators use only the Python standard library. After a change to the theme colors, the name, or the hero lead, render them again from `media/favicon.svg` and the data with a rasterizer, such as `sharp` for the icons and Chromium for the social card. `tests/test_media_sizes.py` checks their sizes.

Never edit generated content. Edit its source in `data/`, `templates/`, or the post itself, then run `make sync`. To find the source of a block, search `scripts/` for its marker name.

## Posts

- Add a post: create `posts/<slug>/index.html`. Copy the structure of an existing post, including its marker comments. Commit, and the hook fills in the nav, the SEO tags, the listing, and the sitemap.
- The title goes in `<h1 class="page-title">`. The date and categories go in `<p class="page-meta">`. The first paragraph becomes the description.
- The first image file in the post directory becomes the social image.
- A `.draft` file in the post directory keeps the post out of the listing, the sitemap, `feed.xml`, `llms.txt` and `llms-full.txt`, and adds `noindex`. The URL still works.

## Rules

- `resume.html` is a standalone print document with no site nav. Its print layout must never split an entry across pages or leave a heading alone at the bottom of a page.
- Keep pages plain HTML and CSS. The only script is `js/motion.js`. It is first-party, has no framework and no build step, and every page works without it. `tests/test_js_shape.py` holds it to the code-shape rules. Add no other script.
- Respect reduced motion. The stylesheet and `js/motion.js` must show every page as a still page when the visitor asks for less motion.
- No generated file, no discovery file and no structured data holds the email address. `tests/test_site_contract.py` fails if one does. `resume.html` shows it as a normal resume contact line.
- Every page except `resume.html` has one `<main id="main">`. The skip link targets it.
- On phones the hero, each home section heading, and the plain pages (`page-plain`: Stuff and 404) are centred. Posts, lists and card text stay left-aligned. Every link and button is 44 px tall and wide or more.
- The phone menu is a column of rows that keeps its content height. `tests/test_menu_css.py` guards this, because some WebKit browsers stretch grid rows over the whole panel.
- Do not add analytics, tracking, or third-party scripts without Shaun's named approval.
- Large files in `media/` are published and downloaded by visitors. Keep new images small. The default social image is `media/og-image.jpg`.
- Every file in `media/` must be used. `tests/test_media_refs.py` fails on an unused file, because an unused file is still published.
- 3D models and Blender files do not belong here. They live in the `3d-printing-lab` repo (`projects/website-models/`).
