#!/usr/bin/env python3
"""Stamps SEO/social meta tags (description, canonical, OpenGraph, Twitter card, icons,
theme colors, feed link, structured data) into every page under site/, between
<!-- SEO:START --> / <!-- SEO:END --> markers. Top-level pages come from data/pages.json;
every post under site/posts/*/ is discovered automatically (via lib_posts) and
needs no registration — add a new posts/<slug>/index.html and this fills in
its SEO tags on the next commit. Site-wide constants (name, base URL, default
image, icons) come from data/site.json via lib_site, the theme colors from
data/theme.json, and the JSON-LD from lib_jsonld. No tag holds an email address.
Run directly (`python3 scripts/sync_seo.py`), wired into the pre-commit hook.
"""
import html
import pathlib
import re
from dataclasses import dataclass

import lib_jsonld
from lib_blocks import replace_block, wrap, write_if_changed
from lib_images import image_size
from lib_posts import all_posts
from lib_record import load_record
from lib_site import REPO_ROOT, load_pages, load_site, load_theme, page_url

TITLE_END = "</title>\n"
TITLE_RE = re.compile(r"<title>.*?</title>", re.DOTALL)
NOINDEX = '<meta name="robots" content="noindex">'


def esc(s: str) -> str:
    return s.replace('"', "&quot;")


@dataclass(frozen=True)
class SeoMeta:
    url: str
    title: str
    description: str
    og_type: str
    image: str
    extra: tuple[str, ...] = ()  # more <head> lines, for example noindex or structured data


@dataclass(frozen=True)
class SeoInputs:
    """Everything the tags need: the site data, the record, the site folder and the head lines every page shares."""

    site: dict
    record: dict
    site_dir: pathlib.Path
    common: tuple[str, ...]


def common_head(site: dict, theme: dict) -> tuple[str, ...]:
    """Head lines every page shares: author, theme colors, icons, manifest and the feed."""
    base, name, icons = site["base_url"], esc(site["name"]), site["icons"]
    return (
        f'<meta name="author" content="{name}">',
        f'<meta property="og:site_name" content="{name}">',
        '<meta name="color-scheme" content="light dark">',
        f'<meta name="theme-color" content="{theme["light"]["background"]}" media="(prefers-color-scheme: light)">',
        f'<meta name="theme-color" content="{theme["dark"]["background"]}" media="(prefers-color-scheme: dark)">',
        f'<link rel="icon" href="{base}{icons["svg"]}" type="image/svg+xml">',
        f'<link rel="icon" href="{base}{icons["png"]}" sizes="48x48" type="image/png">',
        f'<link rel="apple-touch-icon" href="{base}{icons["apple"]}">',
        f'<link rel="manifest" href="{base}/manifest.webmanifest">',
        f'<link rel="alternate" type="application/atom+xml" title="{name}" href="{base}/feed.xml">',
    )


def build_block(meta: SeoMeta, common: tuple[str, ...] = ()) -> str:
    lines = [
        f'<meta name="description" content="{esc(meta.description)}">',
        f'<link rel="canonical" href="{meta.url}">',
        f'<meta property="og:type" content="{meta.og_type}">',
        f'<meta property="og:title" content="{esc(meta.title)}">',
        f'<meta property="og:description" content="{esc(meta.description)}">',
        f'<meta property="og:url" content="{meta.url}">',
        f'<meta property="og:image" content="{meta.image}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(meta.title)}">',
        f'<meta name="twitter:description" content="{esc(meta.description)}">',
        f'<meta name="twitter:image" content="{meta.image}">',
        *common,
        *meta.extra,
    ]
    return wrap("SEO", "\n".join(lines))


def inject(text: str, block: str) -> str | None:
    """text with the SEO block in place: replaced if present, else added after
    </title>. None if the page has neither."""
    replaced = replace_block(text, "SEO", block)
    if replaced is not None:
        return replaced
    if TITLE_END not in text:
        return None
    return text.replace(TITLE_END, TITLE_END + block + "\n", 1)


def post_url(base_url: str, slug: str) -> str:
    return f"{base_url}/posts/{slug}/"


def post_image(base_url: str, default_image: str, post: dict) -> str:
    if post["image"]:
        return f"{base_url}/posts/{post['slug']}/{post['image']}"
    return default_image


def set_title(text: str, title: str) -> str:
    """text with its <title> set to title, so the tag and the SEO tags share one source."""
    match = TITLE_RE.search(text)
    if not match:
        return text
    return text[: match.start()] + f"<title>{html.escape(title, quote=False)}</title>" + text[match.end():]


def image_size_lines(inputs: SeoInputs, image_url: str) -> tuple[str, ...]:
    """og:image:width and og:image:height for an image of this site, or nothing when the size is unknown."""
    path = inputs.site_dir / image_url.removeprefix(inputs.site["base_url"] + "/")
    size = image_size(path) if path.is_file() else None
    if not size:
        return ()
    pairs = zip(("width", "height"), size, strict=True)
    return tuple(f'<meta property="og:image:{name}" content="{value}">' for name, value in pairs)


def page_extra(inputs: SeoInputs, page: dict) -> tuple[str, ...]:
    """noindex for a page that asks for it, and the WebSite and Person data for the home page."""
    extra = (NOINDEX,) if page.get("noindex") else ()
    if page["file"] == "index.html":
        extra += (lib_jsonld.script_tag(lib_jsonld.home_graph(inputs.site, inputs.record)),)
    return extra


def page_meta(inputs: SeoInputs, page: dict) -> SeoMeta:
    site = inputs.site
    extra = image_size_lines(inputs, site["default_og_image"]) + page_extra(inputs, page)
    return SeoMeta(
        page_url(site["base_url"], page["file"]),
        page["title"].format(name=site["name"]),
        page["description"].format(name=site["name"]),
        page["og_type"],
        site["default_og_image"],
        extra,
    )


def post_extra(inputs: SeoInputs, post: dict, url: str, image: str) -> tuple[str, ...]:
    """A draft stays reachable by URL, but noindex keeps it out of search results."""
    if post["draft"]:
        return (NOINDEX,)
    site = inputs.site
    return (
        lib_jsonld.script_tag(lib_jsonld.blog_posting(site, post, url, image)),
        lib_jsonld.script_tag(lib_jsonld.breadcrumbs(site, post, url)),
    )


def post_meta(inputs: SeoInputs, post: dict) -> SeoMeta:
    site = inputs.site
    url = post_url(site["base_url"], post["slug"])
    image = post_image(site["base_url"], site["default_og_image"], post)
    extra = image_size_lines(inputs, image) + post_extra(inputs, post, url, image)
    return SeoMeta(url, f"{post['title']} — {site['name']}", post["excerpt"], "article", image, extra)


def targets(repo_root: pathlib.Path, inputs: SeoInputs) -> list[tuple[str, pathlib.Path, SeoMeta]]:
    """(name relative to site/, path, SEO data) for every page and post."""
    site_dir = inputs.site_dir
    pages = [
        (page["file"], site_dir / page["file"], page_meta(inputs, page))
        for page in load_pages(repo_root)
        if (site_dir / page["file"]).exists()
    ]
    posts = [
        (f"posts/{post['slug']}/index.html", site_dir / "posts" / post["slug"] / "index.html", post_meta(inputs, post))
        for post in all_posts(site_dir)
    ]
    return pages + posts


def write_seo(path: pathlib.Path, meta: SeoMeta, common: tuple[str, ...]) -> bool:
    new_text = inject(set_title(path.read_text(), meta.title), build_block(meta, common))
    return new_text is not None and write_if_changed(path, new_text)


def load_inputs(repo_root: pathlib.Path) -> SeoInputs:
    site = load_site(repo_root)
    common = common_head(site, load_theme(repo_root))
    return SeoInputs(site, load_record(repo_root), repo_root / "site", common)


def sync(repo_root: pathlib.Path) -> list[str]:
    inputs = load_inputs(repo_root)
    changed = []
    for name, path, meta in targets(repo_root, inputs):
        if write_seo(path, meta, inputs.common):
            changed.append(name)
    return changed


def main():
    changed = sync(REPO_ROOT)
    for c in changed:
        print(f"updated seo: {c}")
    if not changed:
        print("seo already in sync")


if __name__ == "__main__":
    main()
