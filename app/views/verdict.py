"""Trial vs Repeat view (default tab) — the promotion-or-brand verdict.

The whole story in one screen: the two seeded launch items side by side. One had a
big trial spike and almost nobody came back (a promotion — expensive sampling); the
other drew a modest trial and kept them (a brand). The verdict, the stat cards, and
the trial-reach-vs-repeat scatter all recompute live from the repeat window.
"""

import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from app import panel_data
from app.charts import CHART_CONFIG, economist_layout, pct_yaxis
from app.components import (
    definitions_panel,
    metric_card,
    metric_cards_grid,
    view_heading,
    why_this_matters,
)
from app.constants import (
    BRAND_REPEAT_THRESHOLD,
    FONT_SANS,
    FONT_SERIF,
    INK,
    REFERENCE,
    TEXT_SECONDARY,
    VERDICT_BRAND,
    VERDICT_PROMOTION,
    fmt_number,
    fmt_pct,
)

_WHY = (
    "Household penetration can rise every quarter while the business quietly dies: if "
    "new buyers pour in and almost none repeat, growth is a treadmill that collapses "
    "the moment acquisition spend stops. Repeat rate is the difference between a brand "
    "and a promotion — and it's how a launch that looked great in month one gets "
    "discontinued after a 'successful' year."
)


def layout():
    return html.Div(
        [
            view_heading(
                "Trial vs repeat: promotion or brand?",
                "Two launches, side by side. One kept its triers. The other was "
                "expensive sampling. Same trial story — opposite endings.",
            ),
            html.Div(id="verdict-headline", className="verdict-headline"),
            html.Div(id="verdict-cards"),
            dcc.Graph(id="verdict-chart", config=CHART_CONFIG, style={"minHeight": "440px"}),
            html.P(
                "Each launch item plotted by how many households tried it (across) and "
                "how many came back within the repeat window (up). Above the dashed "
                "line reads as a brand; a point far to the right but low is a promotion.",
                className="chart-caption",
            ),
            html.P(id="verdict-cutoff-note", className="as-of"),
            why_this_matters(_WHY),
            definitions_panel(),
        ],
        className="view verdict-view",
    )


def _headline_children(vf, window_weeks):
    """A plain-language verdict a CFO can't misread, built from the two items' rows."""
    brands = vf[vf["verdict"] == "Brand"]
    promos = vf[vf["verdict"] == "Promotion"]
    lead = "One of these launches is a brand. The other is a promotion."
    if len(brands) == len(vf):
        lead = "Both launches kept their triers — both read as brands."
    elif len(promos) == len(vf):
        lead = "Neither launch kept its triers — both read as promotions."
    return [
        html.Div(lead, className="verdict-figure"),
        html.P(
            f"Repeat measured within {window_weeks} weeks of first purchase. "
            "A trial-heavy, repeat-light item is expensive sampling, not adoption.",
            className="verdict-sentence",
        ),
    ]


def _cards(vf, window_weeks):
    cards = []
    for row in vf.itertuples(index=False):
        is_brand = row.verdict == "Brand"
        cards.append(
            metric_card(
                label=f"{row.role.title()} launch — {row.sku_id}",
                value=fmt_pct(row.repeat_rate),
                delta=row.verdict,
                delta_class="delta-up" if is_brand else "delta-down",
                foot=f"{fmt_pct(row.trial_reach)} trial reach · "
                f"{fmt_number(row.n_mature)} mature triers · {window_weeks}w window",
            )
        )
    return metric_cards_grid(
        cards,
        caption="Trial reach is the share of all panel households that tried the item; "
        "repeat rate counts only triers whose window has fully elapsed.",
    )


def _build_scatter(vf):
    """Trial reach (x) vs repeat rate (y) per launch item, with the brand-line marked."""
    fig = go.Figure()
    for row in vf.itertuples(index=False):
        color = VERDICT_BRAND if row.verdict == "Brand" else VERDICT_PROMOTION
        fig.add_trace(
            go.Scatter(
                x=[row.trial_reach],
                y=[row.repeat_rate],
                mode="markers+text",
                marker=dict(size=22, color=color, line=dict(color=INK, width=1)),
                text=[f"  {row.role.title()} ({row.sku_id})"],
                textposition="middle right",
                textfont=dict(family=FONT_SANS, size=12, color=INK),
                cliponaxis=False,
                name=row.verdict,
                hovertemplate=(
                    f"{row.role.title()} — {row.sku_id}<br>"
                    "Trial reach %{x:.1%}<br>Repeat %{y:.1%}<extra></extra>"
                ),
            )
        )

    x_max = float(vf["trial_reach"].max()) if len(vf) else 0.3
    y_max = max(float(vf["repeat_rate"].max()) if len(vf) else 0.6, BRAND_REPEAT_THRESHOLD)

    layout = economist_layout(
        title=dict(
            text="Trial reach vs repeat rate",
            font=dict(family=FONT_SERIF, size=22, color=INK),
        ),
        xaxis=dict(
            title=dict(text="Trial reach (share of households)",
                       font=dict(family=FONT_SANS, size=14, color=TEXT_SECONDARY)),
            showgrid=False, showline=True, linecolor=REFERENCE, automargin=True,
            tickformat=".0%", range=[0, x_max * 1.35 if x_max else 0.3],
            tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
        ),
        yaxis=pct_yaxis(y_max, title="Repeat rate"),
        showlegend=False,
        margin=dict(l=70, r=40, t=64, b=56),
    )
    fig.update_layout(**layout)

    # The brand line: at/above this repeat rate reads as a brand, below as a promotion.
    fig.add_hline(y=BRAND_REPEAT_THRESHOLD, line=dict(color=REFERENCE, width=1.5, dash="dash"))
    fig.add_annotation(
        x=0, xref="paper", y=BRAND_REPEAT_THRESHOLD, yanchor="bottom",
        text=f"Brand line — {fmt_pct(BRAND_REPEAT_THRESHOLD, 0)} repeat",
        showarrow=False, xanchor="left",
        font=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
    )
    return fig


def register_callbacks():
    @callback(
        Output("verdict-headline", "children"),
        Output("verdict-cards", "children"),
        Output("verdict-chart", "figure"),
        Output("verdict-cutoff-note", "children"),
        Input("filter-state", "data"),
    )
    def _update(filter_json):
        from app.filters import parse_filter_state

        _scope, window, line, retailer = parse_filter_state(filter_json)
        vf = panel_data.item_verdict(window, BRAND_REPEAT_THRESHOLD, line, retailer)
        # Both launch items are always mature, so the cutoff note reports the window only.
        cutoff = (
            f"Repeat window: {window} weeks. Both launch items trialed in 2023-Q2, so "
            "every trier is fully mature — no right-censoring on this comparison."
        )
        return (
            _headline_children(vf, window),
            _cards(vf, window),
            _build_scatter(vf),
            cutoff,
        )
