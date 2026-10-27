"""Renders the picture at the top of each Work card from the `picture` object of a project in data/site.json.

Three kinds: a looping silent clip with a still, a logo, and a sample decision curve. A table of named renderers
picks one by the `kind`, so a new kind is one function and one table entry. Each picture sits on a `card-media` plate
that the stylesheet shapes and that js/motion.js plays only while the plate is on screen.
"""
import html
import pathlib

from lib_curve_svg import render_curve_svg
from lib_images import size_attributes


def public_path(path: str) -> str:
    """A path from the site root, as a relative URL, the way the other images on the home page are written."""
    return path.lstrip("/")


def source(path: str, mime: str) -> str:
    return f'<source src="{public_path(path)}" type="{mime}">'


def render_clip(picture: dict, site_dir: pathlib.Path) -> str:
    """A silent loop that loads nothing until the script plays it. The still shows meanwhile, and with no script."""
    sizes = size_attributes(site_dir / public_path(picture["still"]))
    video = (
        f'<video muted loop playsinline preload="none" poster="{public_path(picture["still"])}"{sizes} '
        f'role="img" aria-label="{html.escape(picture["alt"])}">'
        f'{source(picture["mp4"], "video/mp4")}{source(picture["webm"], "video/webm")}</video>'
    )
    return f'<div class="card-media card-media-clip">{video}</div>'


def render_logo(picture: dict, site_dir: pathlib.Path) -> str:
    sizes = size_attributes(site_dir / public_path(picture["image"]))
    image = (
        f'<img class="card-logo" src="{public_path(picture["image"])}" alt="{html.escape(picture["alt"])}"'
        f'{sizes} loading="lazy" decoding="async">'
    )
    return f'<div class="card-media card-media-logo">{image}</div>'


def render_curve(picture: dict, site_dir: pathlib.Path) -> str:
    note = f'<span class="card-note">{html.escape(picture["note"])}</span>'
    return f'<div class="card-media card-media-curve">\n{render_curve_svg(picture)}\n{note}\n</div>'


# Every renderer takes (picture, site_dir), so the table calls each one the same way.
RENDERERS = {"clip": render_clip, "logo": render_logo, "decision-curve": render_curve}


def render_picture(picture: dict, site_dir: pathlib.Path) -> str:
    return RENDERERS[picture["kind"]](picture, site_dir)
