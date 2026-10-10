# templates/

This directory holds HTML fragments that generators stamp into pages.

## Files

- `nav.html`: the site nav. `scripts/sync_nav.py` stamps it between the `NAV` markers of every page whose `nav` switch is on in `data/pages.json`.

## Rules

- `{root}` is the relative path to the site root, for example `../../` in a post. Use it in front of every local link.
- `{name}`, `{github}`, `{x}`, and `{cal}` come from `data/site.json`. Do not write these values into the template.
- `{page_links}` is one link for each page with a `menu` entry in `data/pages.json`. To add, remove, or reorder a page link, edit `data/pages.json`, not the template.
- Write a literal brace as `{{` or `}}`, because the template goes through Python `str.format`.
- After an edit, run `make sync` and check one top-level page and one post.
