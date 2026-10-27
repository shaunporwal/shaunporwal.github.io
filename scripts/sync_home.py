#!/usr/bin/env python3
"""Stamps the hero and the Work cards into site/index.html from data/site.json and the experience record.

The hero holds the current role, the name, the lead text, three links and the portrait.
Each card in the Work section links one project in `projects` in data/site.json. Stamped
between <!-- HERO:START --> / <!-- HERO:END --> and <!-- WORK:START --> / <!-- WORK:END -->
markers. Run directly (`python3 scripts/sync_home.py`), wired into the pre-commit hook.
"""
import html
import pathlib

from lib_blocks import replace_block, wrap, write_if_changed
from lib_images import size_attributes
from lib_record import current_roles, load_record
from lib_site import REPO_ROOT, load_site

ARROW = (
    '<svg class="card-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M7 17 17 7M8 7h9v9"/></svg>'
)
NEW_TAB = ' target="_blank" rel="noopener"'


def role_line(record: dict) -> str:
    roles = [f"{role['title']} at {role['org']}" for role in current_roles(record)]
    return html.escape(" and ".join(roles))


def hero_links(site: dict) -> str:
    return (
        f'<a class="btn btn-primary" href="{site["cal"]}"{NEW_TAB}>Book a call</a>\n'
        f'        <a class="btn btn-outline" href="resume.html"{NEW_TAB}>Resume</a>\n'
        f'        <a class="btn btn-outline" href="{site["github"]}" target="_blank" rel="me noopener">GitHub</a>'
    )


def portrait(site: dict, site_dir: pathlib.Path) -> str:
    path = site["avatar_path"]
    sizes = size_attributes(site_dir / path.lstrip("/"))
    alt = html.escape(f"Portrait of {site['name']}")
    return f'<img src="{path.lstrip("/")}" alt="{alt}"{sizes} fetchpriority="high">'


def render_hero(site: dict, record: dict, site_dir: pathlib.Path) -> str:
    name, lead = html.escape(site["name"]), html.escape(site["hero"]["lead"])
    return f"""<section class="hero" id="top">
  <div class="shell hero-grid">
    <div class="hero-copy">
      <p class="eyebrow rise rise-0">{role_line(record)}</p>
      <h1 class="display rise rise-1">{name}</h1>
      <p class="lead rise rise-2">{lead}</p>
      <div class="btn-row rise rise-3">
        {hero_links(site)}
      </div>
    </div>
    <figure class="hero-portrait rise rise-2">
      {portrait(site, site_dir)}
    </figure>
  </div>
</section>"""


def render_card(project: dict) -> str:
    name, summary = html.escape(project["name"]), html.escape(project["summary"])
    return f"""      <li class="card lift" data-reveal-item>
        <a class="card-link" href="{project["url"]}"{NEW_TAB}>
          <h3 class="card-title">{name}{ARROW}</h3>
          <p class="card-text">{summary}</p>
        </a>
      </li>"""


def render_work(site: dict) -> str:
    cards = "\n".join(render_card(project) for project in site["projects"])
    return f"""<section class="section" id="work">
  <div class="shell">
    <p class="eyebrow" data-reveal-item>{html.escape(site["work"]["eyebrow"])}</p>
    <h2 class="title" data-reveal-item>{html.escape(site["work"]["title"])}</h2>
    <ul class="card-grid">
{cards}
    </ul>
  </div>
</section>"""


def stamp(text: str, blocks: dict[str, str]) -> str:
    """text with each named block replaced. A block with no markers in text is skipped."""
    for name, body in blocks.items():
        text = replace_block(text, name, wrap(name, body)) or text
    return text


def sync(repo_root: pathlib.Path) -> bool:
    """Writes the hero and work blocks into site/index.html. Returns whether the file changed."""
    site_dir = repo_root / "site"
    site, record = load_site(repo_root), load_record(repo_root)
    blocks = {"HERO": render_hero(site, record, site_dir), "WORK": render_work(site)}
    path = site_dir / "index.html"
    return path.exists() and write_if_changed(path, stamp(path.read_text(), blocks))


def main():
    if sync(REPO_ROOT):
        print("updated site/index.html hero and work blocks")
    else:
        print("home blocks already in sync")


if __name__ == "__main__":
    main()
