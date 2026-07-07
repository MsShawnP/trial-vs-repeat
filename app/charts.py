"""Shared Economist-style chart defaults and SVG config for Plotly figures.

Cloned from Decompose/Spin Rate so Leaky Bucket's charts are visually identical by
construction: Lailara tokens, serif titles, a single bottom horizontal legend,
automargin so the longest label always renders, and axis-tick helpers that show each
tick's true value with no duplicates.
"""

import math

from app.constants import (
    CANVAS,
    FONT_SANS,
    FONT_SERIF,
    GRIDLINE,
    INK,
    TEXT_SECONDARY,
)


def economist_layout(**overrides):
    """Return a Plotly layout dict with Lailara/Economist-style defaults."""
    defaults = dict(
        paper_bgcolor=CANVAS,
        plot_bgcolor=CANVAS,
        font=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
        title=dict(font=dict(family=FONT_SERIF, size=22, color=INK)),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=GRIDLINE,
            automargin=True,
            tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRIDLINE,
            gridwidth=1,
            showline=False,
            automargin=True,
            tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
        ),
        margin=dict(l=70, r=24, t=64, b=48),
        hoverlabel=dict(
            bgcolor=CANVAS,
            font=dict(family=FONT_SANS, size=13, color=INK),
            bordercolor=GRIDLINE,
        ),
        dragmode=False,
        showlegend=True,
        # Bottom, horizontal, small swatches — every figure inherits this unless it
        # explicitly overrides, so legend placement is consistent across charts.
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="left",
            x=0,
            font=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
            bgcolor="rgba(0,0,0,0)",
            itemsizing="constant",
        ),
    )
    defaults.update(overrides)
    return defaults


def _nice_dtick(max_value: float, divisions: int = 6) -> float:
    """Pick a round tick step (1/2/2.5/5 × 10ⁿ) giving ~5–8 evenly spaced ticks."""
    if max_value <= 0:
        return 1.0
    raw = max_value / divisions
    magnitude = 10 ** math.floor(math.log10(raw))
    step = 10 * magnitude
    for mult in (1, 2, 2.5, 5, 10):
        if mult * magnitude >= raw:
            step = mult * magnitude
            break
    return step


def pct_yaxis(max_value: float, title: str = "Rate", **overrides) -> dict:
    """A y-axis for percentages: true, evenly-spaced, non-duplicate % ticks, headroom.

    ``max_value`` is a decimal fraction (0.55 = 55%). Tick step is chosen so labels
    never round to the same value; the axis max is extended so top labels aren't clipped.
    """
    # Choose a round percentage step (5% / 10% / 25% …) from the fraction range.
    dtick_pct = _nice_dtick(max_value * 100, divisions=5)
    dtick = max(1.0, dtick_pct) / 100.0
    axis = dict(
        title=dict(text=title, font=dict(family=FONT_SANS, size=14, color=TEXT_SECONDARY)),
        showgrid=True,
        gridcolor=GRIDLINE,
        gridwidth=1,
        showline=False,
        automargin=True,
        tickformat=".0%",
        dtick=dtick,
        range=[0, max_value * 1.18 if max_value > 0 else 1],
        tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
    )
    axis.update(overrides)
    return axis


def count_yaxis(max_value: float, title: str = "Households", **overrides) -> dict:
    """A y-axis for whole counts: round, evenly-spaced, non-duplicate integer ticks."""
    dtick = _nice_dtick(max_value, divisions=6)
    axis = dict(
        title=dict(text=title, font=dict(family=FONT_SANS, size=14, color=TEXT_SECONDARY)),
        showgrid=True,
        gridcolor=GRIDLINE,
        gridwidth=1,
        showline=False,
        automargin=True,
        tickformat=",.0f",
        dtick=dtick,
        range=[0, max_value * 1.15 if max_value > 0 else 1],
        tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
    )
    axis.update(overrides)
    return axis


CHART_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
    "toImageButtonOptions": {"format": "svg"},
}
