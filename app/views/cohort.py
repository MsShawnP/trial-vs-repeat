"""Cohort Retention view — the retention triangle + depth of repeat.

The triangle cohorts households by the quarter they first bought, then shows what
share bought again each later quarter. Recent cohorts have fewer observable quarters,
so the triangle is short on the right — that gap IS the right-censoring, shown rather
than smoothed away. Depth of repeat splits mature triers into 1× / 2× / 3×+.
"""

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from app import panel_data
from app.charts import CHART_CONFIG, economist_layout
from app.components import view_heading, why_this_matters
from app.constants import (
    CANVAS,
    DEPTH_COLORS,
    FONT_SANS,
    FONT_SERIF,
    GRIDLINE,
    HK_35,
    HK_85,
    INK,
    TEXT_SECONDARY,
    fmt_number,
    fmt_pct,
)

_WHY = (
    "A single repeat number hides who is actually sticking. Cohorting by first-purchase "
    "quarter shows whether newer buyers behave like older ones — and the triangle's "
    "missing corner is the honest admission that recent cohorts haven't had time to "
    "repeat yet. Depth separates one-and-done triers from households building a habit."
)

_RETENTION_SCALE = [[0.0, CANVAS], [0.15, HK_85], [1.0, HK_35]]


def layout():
    return html.Div(
        [
            view_heading(
                "Cohort retention",
                "Group buyers by the quarter they first bought, then watch how many "
                "come back. The missing corner is time not yet elapsed — not failure.",
            ),
            dcc.Graph(id="cohort-heatmap", config=CHART_CONFIG, style={"minHeight": "440px"}),
            html.P(
                "Each row is a cohort (first-purchase quarter); each column is quarters "
                "since. Darker = more of that cohort bought again. Blank cells to the "
                "right are quarters that haven't happened yet for recent cohorts.",
                className="chart-caption",
            ),
            html.P(
                "Retention here is quarter-grain — the share of the cohort that bought "
                "again in that quarter — and does not use the repeat-window setting. It "
                "answers a different question than the repeat rate on the Trial vs "
                "Repeat tab, so the two numbers are not meant to match.",
                className="chart-caption chart-caption--note",
            ),
            dcc.Graph(id="depth-chart", config=CHART_CONFIG, style={"minHeight": "340px"}),
            html.P(
                "Depth counts distinct purchase occasions (shopping trips) within the "
                "window: 1× = trial only, 2× = came back once, 3×+ = twice or more. "
                "Several units bought on the same day count as one trip.",
                className="chart-caption",
            ),
            html.P(id="depth-note", className="as-of"),
            why_this_matters(_WHY),
        ],
        className="view cohort-view",
    )


def _empty_figure(message):
    """A blank Economist-styled figure carrying a centered note (empty-slice guard)."""
    fig = go.Figure()
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5,
                       showarrow=False,
                       font=dict(family=FONT_SANS, size=15, color=TEXT_SECONDARY))
    fig.update_layout(**economist_layout(showlegend=False,
                                         xaxis=dict(visible=False), yaxis=dict(visible=False)))
    return fig


def _build_triangle(ret):
    """Heatmap: cohort (row) × offset quarters-since-first (col), z = retention share."""
    if ret.empty:
        return _empty_figure("No cohorts under the current filter.")
    cohorts = ret.drop_duplicates("cohort_qi").sort_values("cohort_qi")
    row_order = cohorts["cohort_label"].tolist()
    sizes = dict(zip(cohorts["cohort_label"], cohorts["cohort_size"]))
    max_offset = int(ret["offset"].max()) if len(ret) else 0
    offsets = list(range(max_offset + 1))

    pivot = ret.pivot_table(index="cohort_label", columns="offset", values="retention")
    pivot = pivot.reindex(index=row_order, columns=offsets)
    z = pivot.to_numpy(dtype=float)
    text = np.where(np.isnan(z), "", np.vectorize(lambda v: fmt_pct(v, 0))(z))

    y_labels = [f"{lbl}  (n={fmt_number(sizes[lbl])})" for lbl in row_order]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=[f"+{o}" for o in offsets],
            y=y_labels,
            text=text,
            texttemplate="%{text}",
            textfont=dict(family=FONT_SANS, size=11, color=INK),
            colorscale=_RETENTION_SCALE,
            zmin=0,
            zmax=1,
            hoverongaps=False,
            hovertemplate="Cohort %{y}<br>+%{x} quarters<br>Retention %{z:.0%}<extra></extra>",
            colorbar=dict(
                title=dict(text="Retention", font=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY)),
                tickformat=".0%",
                outlinewidth=0,
            ),
        )
    )
    layout = economist_layout(
        title=dict(text="Retention by first-purchase cohort",
                   font=dict(family=FONT_SERIF, size=22, color=INK)),
        xaxis=dict(title=dict(text="Quarters since first purchase",
                              font=dict(family=FONT_SANS, size=14, color=TEXT_SECONDARY)),
                   showgrid=False, showline=False, automargin=True, side="top",
                   tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY)),
        yaxis=dict(autorange="reversed", showgrid=False, showline=False, automargin=True,
                   tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY)),
        showlegend=False,
        margin=dict(l=140, r=24, t=72, b=48),
    )
    fig.update_layout(**layout)
    return fig


def _build_depth(depth, window_weeks):
    """Vertical bars: share of mature triers at 1× / 2× / 3×+ purchases in the window."""
    order = ["1x", "2x", "3x+"]
    labels = {"1x": "1× (trial only)", "2x": "2×", "3x+": "3×+"}
    shares = [depth["shares"][k] for k in order]
    counts = [depth["counts"][k] for k in order]
    colors = [DEPTH_COLORS[k] for k in order]

    fig = go.Figure(
        go.Bar(
            x=[labels[k] for k in order],
            y=shares,
            marker_color=colors,
            text=[f"<b>{fmt_pct(s)}</b><br>{fmt_number(c)}" for s, c in zip(shares, counts)],
            textposition="outside",
            textfont=dict(family=FONT_SANS, size=12, color=INK),
            cliponaxis=False,
            hovertemplate="%{x}<br>%{y:.1%} of mature triers<extra></extra>",
        )
    )
    y_max = max(shares) if shares else 1.0
    layout = economist_layout(
        title=dict(text=f"Depth of repeat within {window_weeks} weeks",
                   font=dict(family=FONT_SERIF, size=22, color=INK)),
        yaxis=dict(title=dict(text="Share of mature triers",
                              font=dict(family=FONT_SANS, size=14, color=TEXT_SECONDARY)),
                   showgrid=True, gridcolor=GRIDLINE, showline=False, automargin=True,
                   tickformat=".0%", range=[0, y_max * 1.2 if y_max else 1],
                   tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY)),
        showlegend=False,
        margin=dict(l=64, r=24, t=64, b=44),
    )
    fig.update_layout(**layout)
    return fig


def register_callbacks():
    @callback(
        Output("cohort-heatmap", "figure"),
        Output("depth-chart", "figure"),
        Output("depth-note", "children"),
        Input("filter-state", "data"),
    )
    def _update(filter_json):
        from app.filters import parse_filter_state

        scope, window, line, retailer = parse_filter_state(filter_json)
        sku = panel_data.scope_sku(scope)
        ret = panel_data.cohort_retention(line, retailer, sku)
        depth = panel_data.depth_of_repeat(window, line, retailer, sku)
        note = (
            f"Depth counts only the {fmt_number(depth['n_mature'])} triers whose "
            f"{window}-week window has fully elapsed (maturity cutoff applied)."
        )
        return _build_triangle(ret), _build_depth(depth, window), note
