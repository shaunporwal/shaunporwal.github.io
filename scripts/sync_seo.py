#!/usr/bin/env python3
"""Stamps SEO/social meta tags (description, canonical, OpenGraph, Twitter card)
into every page under site/, between <!-- SEO:START --> / <!-- SEO:END -->
markers. Top-level pages use a small hand-written registry (PAGES below);
every post under site/posts/*/ is discovered automatically (via lib_posts) and
needs no registration — add a new posts/<slug>/index.html and this fills in
its SEO tags on the next commit. Site-wide constants (name, base URL, default
image) come from data/site.json via lib_site, not hardcoded here. Run
directly (`python3 scripts/sync_seo.py`), wired into the pre-commit hook.
"""
import pathlib
import re

try:
    from lib_posts import all_posts
    from lib_site import load_site
except ImportError:
    from scripts.lib_posts import all_posts
    from scripts.lib_site import load_site

MARKER_RE = re.compile(r"<!-- SEO:START -->.*?<!-- SEO:END -->\n?", re.DOTALL)

# Top-level pages don't have a generic way to derive a description, so they're
# registered by hand here. New top-level pages need one line added; posts need
# nothing (auto-discovered). {name} is filled in from data/site.json.
PAGES = {
    "index.html": (
        "{name}",
        "{name}'s blog: writing in public about building, coding, and thinking clearly.",
        "website",
    ),
    "about.html": (
        "About — {name}",
        "About {name} — engineer working across AI/ML, biomedical data science, and chemical inventory software.",
        "website",
    ),
    "stuff.html": (
        "Stuff — {name}",
        "A small gallery of 3D models and other stuff from {name}.",
        "website",
    ),
    "resume.html": (
        "{name} — Resume",
        "{name}'s resume: software engineering, machine learning, and biomedical data science experience.",
        "website",
    ),
}


def esc(s: str) -> str:
    return s.replace('"', "&quot;")


def build_block(url: str, title: str, description: str, og_type: str, image: str) -> str:
    return (
        "<!-- SEO:START -->\n"
        f'<meta name="description" content="{esc(description)}">\n'
        f'<link rel="canonical" href="{url}">\n'
        f'<meta property="og:type" content="{og_type}">\n'
        f'<meta property="og:title" content="{esc(title)}">\n'
        f'<meta property="og:description" content="{esc(description)}">\n'
        f'<meta property="og:url" content="{url}">\n'
        f'<meta property="og:image" content="{image}">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{esc(title)}">\n'
        f'<meta name="twitter:description" content="{esc(description)}">\n'
        f'<meta name="twitter:image" content="{image}">\n'
        "<!-- SEO:END -->\n"
    )


def inject(text: str, block: str) -> str | None:
    """Returns the updated text, or None if nothing changed."""
    if MARKER_RE.search(text):
        new_text = MARKER_RE.sub(block, text)
    elif "</title>\n" in text:
        new_text = text.replace("</title>\n", "</title>\n" + block, 1)
    else:
        return None
    return new_text if new_text != text else None


def page_url(base_url: str, name: str) -> str:
    return f"{base_url}/" if name == "index.html" else f"{base_url}/{name}"


def post_url(base_url: str, slug: str) -> str:
    return f"{base_url}/posts/{slug}/"


def post_image(base_url: str, default_image: str, post: dict) -> str:
    if post["image"]:
        return f"{base_url}/posts/{post['slug']}/{post['image']}"
    return default_image


def page_block(site: dict, name: str, templates: tuple) -> str:
    title_tmpl, description_tmpl, og_type = templates
    return build_block(
        page_url(site["base_url"], name),
        title_tmpl.format(name=site["name"]),
        description_tmpl.format(name=site["name"]),
        og_type,
        site["default_og_image"],
    )


def post_block(site: dict, post: dict) -> str:
    return build_block(
        post_url(site["base_url"], post["slug"]),
        f"{post['title']} — {site['name']}",
        post["excerpt"],
        "article",
        post_image(site["base_url"], site["default_og_image"], post),
    )


def targets(site_dir: pathlib.Path, site: dict) -> list[tuple[str, pathlib.Path, str]]:
    """(name relative to site_dir, path, SEO block) for every page and post."""
    pages = [
        (name, site_dir / name, page_block(site, name, templates))
        for name, templates in PAGES.items()
        if (site_dir / name).exists()
    ]
    posts = [
        (f"posts/{post['slug']}/index.html", site_dir / "posts" / post["slug"] / "index.html", post_block(site, post))
        for post in all_posts(site_dir)
    ]
    return pages + posts


def write_block(path: pathlib.Path, block: str) -> bool:
    new_text = inject(path.read_text(), block)
    if new_text is None:
        return False
    path.write_text(new_text)
    return True


def sync(site_dir: pathlib.Path) -> list[str]:
    site = load_site(site_dir.parent)
    changed = []
    for name, path, block in targets(site_dir, site):
        if write_block(path, block):
            changed.append(name)
    return changed


def main():
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    changed = sync(repo_root / "site")
    for c in changed:
        print(f"updated seo: {c}")
    if not changed:
        print("seo already in sync")


if __name__ == "__main__":
    main()
