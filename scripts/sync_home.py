#!/usr/bin/env python3
"""Stamps the hero and the Work cards into site/index.html from data/site.json and the experience record.

The hero holds the current role, the name, the lead text, three links and the portrait.
Each card in the Work section links one project in `projects` in data/site.json. It leads with the
project's picture (see lib_pictures.py), then the name and one line. Stamped
between <!-- HERO:START --> / <!-- HERO:END --> and <!-- WORK:START --> / <!-- WORK:END -->
markers. Run directly (`python3 scripts/sync_home.py`), wired into the pre-commit hook.
"""
import html
import pathlib
import textwrap

from lib_blocks import replace_block, wrap, write_if_changed
from lib_html import NEW_TAB, PROFILE_TAB
from lib_images import size_attributes
from lib_pictures import render_picture
from lib_record import current_roles, load_record
from lib_site import REPO_ROOT, load_site, profile

ARROW = (
    '<svg class="card-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M7 17 17 7M8 7h9v9"/></svg>'
)
PICTURE_INDENT = " " * 10


HERO_TEMPLATE = """<section class="hero" id="top">
  <div class="hero-art" aria-hidden="true"><span class="hero-dots"></span><span class="hero-lit"></span></div>
  <div class="shell hero-grid">
    <div class="hero-copy">
      <p class="eyebrow rise rise-0">{role}</p>
      <h1 class="display rise rise-1">{name}</h1>
      <p class="lead rise rise-2">{lead}</p>
      <div class="btn-row rise rise-3">
        {links}
      </div>
    </div>
    <figure class="hero-portrait rise rise-2">
      {portrait}
    </figure>
  </div>
</section>"""


def role_line(record: dict) -> str:
    roles = [f"{role['title']} at {role['org']}" for role in current_roles(record)]
    return html.escape(" and ".join(roles))


def hero_links(site: dict) -> str:
    github_label, github_url = profile(site, "github")
    return (
        f'<a class="btn btn-primary btn-sheen" href="{site["cal"]}"{NEW_TAB}>Book a call</a>\n'
        f'        <a class="btn btn-outline" href="resume.html">Resume</a>\n'
        f'        <a class="btn btn-outline" href="{github_url}"{PROFILE_TAB}>{github_label}</a>'
    )


def portrait(site: dict, site_dir: pathlib.Path) -> str:
    path = site["avatar_path"]
    sizes = size_attributes(site_dir / path.lstrip("/"))
    alt = html.escape(f"Portrait of {site['name']}")
    return f'<img src="{path.lstrip("/")}" alt="{alt}"{sizes} fetchpriority="high">'


def render_hero(site: dict, record: dict, site_dir: pathlib.Path) -> str:
    return HERO_TEMPLATE.format(
        role=role_line(record),
        name=html.escape(site["name"]),
        lead=html.escape(site["hero"]["lead"]),
        links=hero_links(site),
        portrait=portrait(site, site_dir),
    )


def render_card(project: dict, site_dir: pathlib.Path) -> str:
    name, summary = html.escape(project["name"]), html.escape(project["summary"])
    picture = textwrap.indent(render_picture(project["picture"], site_dir), PICTURE_INDENT).lstrip()
    return f"""      <li class="card lift" data-reveal-item>
        <a class="card-link" href="{project["url"]}"{NEW_TAB}>
          {picture}
          <div class="card-body">
            <h3 class="card-title">{name}{ARROW}</h3>
            <p class="card-text">{summary}</p>
          </div>
        </a>
      </li>"""


def render_work(site: dict, site_dir: pathlib.Path) -> str:
    cards = "\n".join(render_card(project, site_dir) for project in site["projects"])
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
    blocks = {"HERO": render_hero(site, record, site_dir), "WORK": render_work(site, site_dir)}
    path = site_dir / "index.html"
    return path.exists() and write_if_changed(path, stamp(path.read_text(), blocks))


def main():
    if sync(REPO_ROOT):
        print("updated site/index.html hero and work blocks")
    else:
        print("home blocks already in sync")


if __name__ == "__main__":
    main()
