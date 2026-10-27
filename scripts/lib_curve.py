"""Decision curve maths and plot geometry for the dcurves card picture, with the standard library only.

The maths and the plot range match assets/js/decision-curve.js in the Junto hub, so both sites draw the same sample
curve. All functions are pure. The box and the range below are the one home of the geometry.
"""
import dataclasses
import math

WIDTH, HEIGHT = 320, 200
BOX = {"left": 20, "right": 300, "top": 24, "bottom": 164}
T_MAX = 0.5
NB_MIN, NB_MAX = -0.05, 0.22
SAMPLE = 0.005


@dataclasses.dataclass(frozen=True)
class Curve:
    """A calibrated model whose scores are normal. `separation` is the gap between the two groups."""

    prevalence: float
    separation: float


def normal_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def logit(p: float) -> float:
    return math.log(p / (1 - p))


def odds(t: float) -> float:
    return t / (1 - t)


def benefit_all(curve: Curve, t: float) -> float:
    """Net benefit of treating everyone. It starts at the prevalence and falls below zero."""
    return curve.prevalence - (1 - curve.prevalence) * odds(t)


def benefit_none(curve: Curve, t: float) -> float:
    return 0.0


def cutoff_at(curve: Curve, t: float) -> float:
    """The score cutoff at which the model reaches the threshold probability."""
    return (logit(t) - logit(curve.prevalence) + curve.separation**2 / 2) / curve.separation


def benefit_model(curve: Curve, t: float) -> float:
    """Net benefit of the model at threshold t."""
    if t == 0:
        return curve.prevalence
    cutoff = cutoff_at(curve, t)
    true_positive = curve.prevalence * (1 - normal_cdf(cutoff - curve.separation))
    false_positive = (1 - curve.prevalence) * (1 - normal_cdf(cutoff))
    return true_positive - false_positive * odds(t)


LINES = {"model": benefit_model, "all": benefit_all, "none": benefit_none}


def threshold_for_benefit_all(curve: Curve, benefit: float) -> float:
    """The threshold at which treating everyone reaches this net benefit. It reverses benefit_all."""
    excess_odds = (curve.prevalence - benefit) / (1 - curve.prevalence)
    return excess_odds / (1 + excess_odds)


def x_at(t: float) -> float:
    return BOX["left"] + t / T_MAX * (BOX["right"] - BOX["left"])


def y_at(benefit: float) -> float:
    share = (benefit - NB_MIN) / (NB_MAX - NB_MIN)
    return BOX["bottom"] - share * (BOX["bottom"] - BOX["top"])


def number(value: float) -> str:
    """One decimal, with no trailing zero: 23.3 and 32."""
    return format(round(value, 1), "g")


def thresholds() -> list[float]:
    return [index * SAMPLE for index in range(round(T_MAX / SAMPLE) + 1)]


def point(curve: Curve, name: str, t: float) -> str:
    return f"{number(x_at(t))} {number(y_at(LINES[name](curve, t)))}"


def line_path(curve: Curve, name: str) -> str:
    """The SVG path of one line, sampled along the whole threshold range."""
    points = [point(curve, name, t) for t in thresholds()]
    return "M" + "L".join(points)


def area_path(curve: Curve) -> str:
    """The region between the model line and the line for treating none."""
    base = number(y_at(0))
    return f"{line_path(curve, 'model')}L{number(x_at(T_MAX))} {base}L{number(x_at(0))} {base}Z"


def marker_at(curve: Curve, t: float) -> tuple[float, float]:
    """Where the live point sits: on the model line at threshold t."""
    return x_at(t), y_at(benefit_model(curve, t))
