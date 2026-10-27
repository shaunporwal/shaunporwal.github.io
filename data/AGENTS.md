# data/

This directory holds the JSON sources of truth for the site. Generators in `scripts/` read these files and write every place that shows their facts.

## Files

- `experiences.json`: every experience fact (jobs, education, projects, skills, languages, publications). It generates the resume (`site/resume.html`) and the full record (`docs/all-experiences.md`).
- `site.json`: the name, the canonical base URL, the summary, the contact links, the `profiles` list (label and key of each profile, in display order), the hero lead, the work cards, the icon paths, the crawler and agent rules in `seo`, and the phrases in `brand.avoid` that no built page may hold (Junto is the company that makes the lab modern, not a software company; `tests/test_brand_copy.py` enforces it).
- `theme.json`: the color, type, motion and shadow tokens. It generates the `THEME` block of `site/styles/site.css`, `site/media/favicon.svg` and the web app manifest colors. The neutrals, radius and ease match `cheminventory.co`. The accent is this site's own.
- `pages.json`: each top-level page in `site/`, in nav menu order, with its title, SEO text, `sitemap` and `nav` switches, and an optional `menu` entry for the nav link.
- `*.schema.json`: the declared format of each JSON file with the same name. The loaders validate each file against its schema when they read it.

## Rules

- Edit a fact here, then run `make sync`. Never edit the generated copy of a fact.
- A schema change must keep the real data valid. `make test` checks the real files.
- The `resume` key in `experiences.json` puts an item on the resume. `true` shows the item as it is. A string or an object changes the wording on the resume only. See `docs/development.md` for every form.
- Dates in `experiences.json` are `YYYY-MM` or `"present"`.
- A resume contact line that `site.json` already holds names its key (`"site": "github"`). Never copy a `site.json` value into another file.
- `base_url` in `site.json` must be the domain that GitHub Pages serves with no redirect. Every canonical URL starts with it, and `site/CNAME` is generated from its host.
- Do not move an unconfirmed fact onto the resume. Confirm new facts with Shaun.
- To add a top-level page, create its HTML file in `site/` and add one entry to `pages.json`.
