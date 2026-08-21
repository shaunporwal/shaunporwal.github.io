#!/usr/bin/env python3
"""Stamps SEO/social meta tags (description, canonical, OpenGraph, Twitter card)
into every page under site/, between <!-- SEO:START --> / <!-- SEO:END -->
markers. Top-level pages use a small hand-written registry (PAGES below);
every post under site/posts/*/ is discovered automatically (via lib_posts) and
needs no registration — add a new posts/<slug>/index.html and this fills in
its SEO tags on the next commit. Run directly (`python3 scripts/sync_seo.py`),
wired into the pre-commit hook.
"""
import re
import pathlib

try:
    from lib_posts import all_posts
except ImportError:
    from scripts.lib_posts import all_posts

BASE_URL = "https://shaunporwal.com"
DEFAULT_IMAGE = f"{BASE_URL}/media/heron.jpg"

MARKER_RE = re.compile(r"<!-- SEO:START -->.*?<!-- SEO:END -->\n?", re.DOTALL)

# Top-level pages don't have a generic way to derive a description, so they're
# registered by hand here. New top-level pages need one line added; posts need
# nothing (auto-discovered).
PAGES = {
    "index.html": (
        "Shaun Porwal",
        "Shaun Porwal's blog: writing in public about building, coding, and thinking clearly.",
        "website",
    ),
    "about.html": (
        "About — Shaun Porwal",
        "About Shaun Porwal — engineer working across AI/ML, biomedical data science, and chemical inventory software.",
        "website",
    ),
    "stuff.html": (
        "Stuff — Shaun Porwal",
        "A small gallery of 3D models and other stuff from Shaun Porwal.",
        "website",
    ),
    "resume.html": (
        "Shaun Porwal — Resume",
        "Shaun Porwal's resume: software engineering, machine learning, and biomedical data science experience.",
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


def page_url(name: str) -> str:
    return f"{BASE_URL}/" if name == "index.html" else f"{BASE_URL}/{name}"


def post_url(slug: str) -> str:
    return f"{BASE_URL}/posts/{slug}/"


def post_image(post: dict) -> str:
    if post["image"]:
        return f"{BASE_URL}/posts/{post['slug']}/{post['image']}"
    return DEFAULT_IMAGE


def sync(site_dir: pathlib.Path) -> list[str]:
    changed = []

    for name, (title, description, og_type) in PAGES.items():
        p = site_dir / name
        if not p.exists():
            continue
        block = build_block(page_url(name), title, description, og_type, DEFAULT_IMAGE)
        new_text = inject(p.read_text(), block)
        if new_text is not None:
            p.write_text(new_text)
            changed.append(name)

    for post in all_posts(site_dir):
        p = site_dir / "posts" / post["slug"] / "index.html"
        block = build_block(
            post_url(post["slug"]),
            f"{post['title']} — Shaun Porwal",
            post["excerpt"],
            "article",
            post_image(post),
        )
        new_text = inject(p.read_text(), block)
        if new_text is not None:
            p.write_text(new_text)
            changed.append(f"posts/{post['slug']}/index.html")

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
