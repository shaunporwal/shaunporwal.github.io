"""Draws the sample decision curve on the dcurves card as inline SVG, with the standard library only.

The SVG holds no color and no style: the page stylesheet colors each class from its tokens, so the picture follows
the light and dark themes. The maths and the geometry are in lib_curve.py. The clip path has one fixed id, so a page
holds one curve.
"""
import html

from lib_curve import (
    BOX,
    HEIGHT,
    T_MAX,
    WIDTH,
    Curve,
    area_path,
    benefit_model,
    line_path,
    marker_at,
    number,
    threshold_for_benefit_all,
    x_at,
    y_at,
)

CLIP_ID = "curve-clip"
LABEL_RAISE = 8
LABEL_DROP = 14
LABEL_BESIDE = 8
LABEL_BENEFIT_ALL = 0.04
PING_RADIUS, DOT_RADIUS = 7, 4


def clip_defs() -> str:
    width, height = BOX["right"] - BOX["left"], BOX["bottom"] - BOX["top"]
    rect = f'<rect x="{BOX["left"]}" y="{BOX["top"]}" width="{width}" height="{height}"/>'
    return f'<defs><clipPath id="{CLIP_ID}">{rect}</clipPath></defs>'


def axis() -> str:
    return f'<path class="curve-axis" d="M{BOX["left"]} {BOX["top"]}V{BOX["bottom"]}H{BOX["right"]}"/>'


def none_line() -> str:
    return f'<path class="curve-none" d="M{number(x_at(0))} {number(y_at(0))}H{number(x_at(T_MAX))}"/>'


def plot(curve: Curve) -> str:
    """The area and the three lines, clipped to the plot box so treating all can fall out of the bottom."""
    parts = (
        f'<path class="curve-area" d="{area_path(curve)}"/>',
        none_line(),
        f'<path class="curve-all" d="{line_path(curve, "all")}"/>',
        f'<path class="curve-model" pathLength="1" d="{line_path(curve, "model")}"/>',
    )
    return f'<g clip-path="url(#{CLIP_ID})">\n' + "\n".join(parts) + "\n</g>"


def marker(curve: Curve, threshold: float) -> str:
    """The live point on the model line, with a ring that the stylesheet pulses while the picture plays."""
    x, y = (number(value) for value in marker_at(curve, threshold))
    ring = f'<circle class="curve-ping" cx="{x}" cy="{y}" r="{PING_RADIUS}"/>'
    dot = f'<circle class="curve-dot" cx="{x}" cy="{y}" r="{DOT_RADIUS}"/>'
    return ring + "\n" + dot


def label(text: str, x: float, y: float, anchor: str, modifier: str) -> str:
    position = f'x="{number(x)}" y="{number(y)}" text-anchor="{anchor}"'
    return f'<text class="curve-label {modifier}" {position}>{html.escape(text)}</text>'


def line_labels(names: dict, curve: Curve) -> str:
    """The direct label of each line: the model above its right end, treat all beside its fall, treat none below."""
    all_t = threshold_for_benefit_all(curve, LABEL_BENEFIT_ALL)
    parts = (
        label(names["model"], x_at(T_MAX), y_at(benefit_model(curve, T_MAX)) - LABEL_RAISE, "end", "curve-label-model"),
        label(names["all"], x_at(all_t) + LABEL_BESIDE, y_at(LABEL_BENEFIT_ALL), "start", "curve-label-all"),
        label(names["none"], x_at(T_MAX), y_at(0) + LABEL_DROP, "end", "curve-label-none"),
    )
    return "\n".join(parts)


def opening_tag(alt: str) -> str:
    return f'<svg class="curve-svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{html.escape(alt)}">'


def render_curve_svg(picture: dict) -> str:
    curve = Curve(picture["prevalence"], picture["separation"])
    parts = (
        clip_defs(),
        axis(),
        plot(curve),
        marker(curve, picture["threshold"]),
        line_labels(picture["lines"], curve),
    )
    return opening_tag(picture["alt"]) + "\n" + "\n".join(parts) + "\n</svg>"

