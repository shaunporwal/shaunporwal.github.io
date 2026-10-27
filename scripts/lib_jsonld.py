"""Builds the schema.org JSON-LD for the site: Person, WebSite, ProfilePage, BlogPosting and BreadcrumbList.

Each builder takes the loaded site data (and the experience record where it needs the current employer)
and returns a plain dict. script_tag() turns a dict into the <script> element. No builder writes an email
address, so no structured data on the site holds one.
"""
import json

from lib_record import current_roles
from lib_site import profile_links

CONTEXT = "https://schema.org"


def script_tag(data: dict) -> str:
    """A structured-data script tag. "</" is escaped so the data cannot close the tag."""
    body = json.dumps(data, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{body}\n</script>'


def employer(record: dict, projects: list[dict]) -> dict | None:
    """The current employer as an Organization. The url comes from the project with the same name."""
    roles = current_roles(record)
    if not roles:
        return None
    node = {"@type": "Organization", "name": roles[0]["org"]}
    urls = [project["url"] for project in projects if project["name"] == roles[0]["org"]]
    return {**node, "url": urls[0]} if urls else node


def person(site: dict, record: dict) -> dict:
    base = site["base_url"]
    node = {
        "@type": "Person",
        "@id": f"{base}/#person",
        "name": site["name"],
        "url": f"{base}/",
        "image": f"{base}{site['avatar_path']}",
        "jobTitle": site["job_title"],
        "description": site["summary"],
        "sameAs": [url for _, url in profile_links(site)],
    }
    works_for = employer(record, site["projects"])
    return {**node, "worksFor": works_for} if works_for else node


def website(site: dict) -> dict:
    base = site["base_url"]
    return {
        "@type": "WebSite",
        "@id": f"{base}/#website",
        "url": f"{base}/",
        "name": site["name"],
        "description": site["summary"],
        "inLanguage": "en",
        "publisher": {"@id": f"{base}/#person"},
    }


def home_graph(site: dict, record: dict) -> dict:
    """The WebSite and the Person, linked by @id, for the home page."""
    return {"@context": CONTEXT, "@graph": [website(site), person(site, record)]}


def profile_page(site: dict, record: dict) -> dict:
    return {"@context": CONTEXT, "@type": "ProfilePage", "mainEntity": person(site, record)}


def blog_posting(site: dict, post: dict, url: str, image: str) -> dict:
    data = {
        "@context": CONTEXT,
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["excerpt"],
        "url": url,
        "image": image,
        "author": {"@type": "Person", "name": site["name"], "url": f"{site['base_url']}/"},
    }
    return {**data, "datePublished": post["date"].isoformat()} if post["date"] else data


def breadcrumbs(site: dict, post: dict, url: str) -> dict:
    items = [(site["name"], f"{site['base_url']}/"), (post["title"], url)]
    elements = [
        {"@type": "ListItem", "position": position, "name": name, "item": item}
        for position, (name, item) in enumerate(items, start=1)
    ]
    return {"@context": CONTEXT, "@type": "BreadcrumbList", "itemListElement": elements}
