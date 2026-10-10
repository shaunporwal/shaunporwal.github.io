# site/

This directory is the published website. GitHub Pages serves it as it is, with no build step. A push to `main` publishes it. Treat that push as a production deployment.

## What Is Hand-Written

- The page content of `index.html`, `about.html`, `stuff.html`, and each `posts/<slug>/index.html`, outside the marker blocks.
- `styles/site.css`, and the inline styles in `resume.html`. Every color in `site.css` is a token in its `:root` block. `tests/test_css_tokens.py` fails on a color literal anywhere else. The resume keeps its own print palette.
- Files in `media/` and the images in each post directory.

## What Is Generated

- Every block between `<!-- NAME:START -->` and `<!-- NAME:END -->` markers: the nav, the SEO tags, the social blocks, the blog listing, and the resume body.
- The `<title>` of every page and post. `sync_seo.py` writes it from `data/pages.json`, or from a post's heading.
- `sitemap.xml`, `robots.txt`, `llms.txt`, and `CNAME`.

Never edit generated content. Edit its source in `data/`, `templates/`, or the post itself, then run `make sync`. To find the source of a block, search `scripts/` for its marker name.

## Posts

- Add a post: create `posts/<slug>/index.html`. Copy the structure of an existing post, including its marker comments. Commit, and the hook fills in the nav, the SEO tags, the listing, and the sitemap.
- The title goes in `<h1 class="page-title">`. The date and categories go in `<p class="page-meta">`. The first paragraph becomes the description.
- The first image file in the post directory becomes the social image.
- A `.draft` file in the post directory keeps the post out of the listing, the sitemap, and `llms.txt`, and adds `noindex`. The URL still works.

## Rules

- `resume.html` is a standalone print document with no site nav. Its print layout must never split an entry across pages or leave a heading alone at the bottom of a page.
- Keep pages plain HTML and CSS. Do not add a framework or a build step.
- Do not add analytics, tracking, or third-party scripts without Shaun's named approval.
- Large files in `media/` are published and downloaded by visitors. Keep new images small. The default social image is `media/og-image.jpg`.
- 3D models and Blender files do not belong here. They live in the `3d-printing-lab` repo (`projects/website-models/`).
