"""Trial vs Repeat view (default tab) — the promotion-or-brand verdict.

The whole story in one screen: the two seeded launch items side by side. One had a
big trial spike and almost nobody came back (a promotion — expensive sampling); the
other drew a modest trial and kept them (a brand). The verdict, the stat cards, and
the trial-reach-vs-repeat scatter all recompute live from the repeat window.
"""

import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from app import panel_data
from app import trial_repeat as tr
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
    VERDICT_NO_DATA,
    VERDICT_PROMOTION,
    fmt_number,
    fmt_pct,
)

# Map each verdict label to its marker/badge colour.
_VERDICT_COLOR = {
    tr.VERDICT_BRAND: VERDICT_BRAND,
    tr.VERDICT_PROMOTION: VERDICT_PROMOTION,
    tr.VERDICT_NO_DATA: VERDICT_NO_DATA,
}

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
    """A plain-language verdict a CFO can't misread, built from the items with data.

    Items excluded by the current filter (verdict 'No data') are set aside — an empty
    slice must never read as a failed launch.
    """
    scored = vf[vf["verdict"] != tr.VERDICT_NO_DATA]
    brands = scored[scored["verdict"] == tr.VERDICT_BRAND]
    promos = scored[scored["verdict"] == tr.VERDICT_PROMOTION]

    if len(scored) == 0:
        lead = "No launch item matches this filter — clear the product line or retailer to compare."
    elif len(brands) == 1 and len(promos) == 1:
        # The hero case (whole-brand default): name which is which so a CFO reads the
        # verdict at a glance, in product terms — not the internal SKU code.
        lead = (f"The {promos.iloc[0]['line_name']} launch is a promotion. "
                f"The {brands.iloc[0]['line_name']} launch is a real brand.")
    elif len(brands) and len(promos):
        # More than two launch items (not in the current panel) — fall back to counts.
        lead = "Some of these launches are brands; others are promotions."
    elif len(promos) == 0:
        lead = (f"The {brands.iloc[0]['line_name']} launch kept its triers — this reads as a brand."
                if len(scored) == 1
                else "Both launches kept their triers — both read as brands.")
    else:
        lead = (f"The {promos.iloc[0]['line_name']} launch didn't keep its triers — this reads as a promotion."
                if len(scored) == 1
                else "Neither launch kept its triers — both read as promotions.")

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
        no_data = row.verdict == tr.VERDICT_NO_DATA
        if no_data:
            value, delta_class = "—", "delta-flat"
            foot = "No triers under the current product-line / retailer filter."
        else:
            value = fmt_pct(row.repeat_rate)
            delta_class = "delta-up" if row.verdict == tr.VERDICT_BRAND else "delta-down"
            foot = (f"{fmt_pct(row.trial_reach)} trial reach · "
                    f"{fmt_number(row.n_mature)} mature triers · {window_weeks}w window")
        cards.append(
            metric_card(
                label=f"{row.role.title()} launch — {row.sku_id}",
                value=value,
                delta=row.verdict,
                delta_class=delta_class,
                foot=foot,
                tip=f"Repeat rate = share of {row.sku_id}'s triers who bought it again "
                f"within {window_weeks} weeks, counting only triers whose window has "
                "fully elapsed (maturity cutoff). At or above "
                f"{fmt_pct(BRAND_REPEAT_THRESHOLD, 0)} reads as a brand; below, a promotion.",
            )
        )
    return metric_cards_grid(
        cards,
        caption="Trial reach is the share of all panel households that tried the item; "
        "repeat rate counts only triers whose window has fully elapsed.",
    )


def _build_scatter(vf):
    """Trial reach (x) vs repeat rate (y) per launch item, with the brand-line marked.

    Items with no data under the current filter are omitted (they have no meaningful
    trial-reach/repeat point), never plotted at the origin as if they failed.
    """
    plotted = vf[vf["verdict"] != tr.VERDICT_NO_DATA]

    fig = go.Figure()
    for row in plotted.itertuples(index=False):
        color = _VERDICT_COLOR.get(row.verdict, REFERENCE)
        fig.add_trace(
            go.Scatter(
                x=[row.trial_reach],
                y=[row.repeat_rate],
                mode="markers+text",
                marker=dict(size=22, color=color, line=dict(color=INK, width=1)),
                text=[f"  <b>{row.role.title()} ({row.sku_id})</b>"],
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

    if len(plotted) == 0:
        fig.add_annotation(
            text="No launch item matches this filter.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(family=FONT_SANS, size=15, color=TEXT_SECONDARY),
        )

    x_max = float(plotted["trial_reach"].max()) if len(plotted) else 0.3
    y_max = max(float(plotted["repeat_rate"].max()) if len(plotted) else 0.6,
                BRAND_REPEAT_THRESHOLD)

    layout = economist_layout(
        title=dict(
            text="Trial reach vs repeat rate",
            font=dict(family=FONT_SERIF, size=22, color=INK),
        ),
        xaxis=dict(
            # Same panel-basis disclosure as the Flow and Cohort axes. This one is
            # on the lead tab, so leaving it as a bare "share of households" would
            # be the first number a CFO reads and the only unlabelled one.
            # Wrapped: as one line this overflows the plot by ~166px at 375px.
            # The other three basis labels are y-axis titles, which rotate and so
            # have the plot's height to work with; this is the only x-axis one.
            title=dict(text=f"Trial reach<br>(share of {panel_data.N_HOUSEHOLDS:,} panel households)",
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
        # Derive the right-censoring note from the data, not a hardcoded claim.
        scored = vf[vf["verdict"] != tr.VERDICT_NO_DATA]
        immature = int((scored["n_triers"] - scored["n_mature"]).sum()) if len(scored) else 0
        if len(scored) == 0:
            cutoff = f"Repeat window: {window} weeks. No launch item matches the current filter."
        elif immature == 0:
            cutoff = (f"Repeat window: {window} weeks. Every trier of the shown item(s) is "
                      "fully mature — no right-censoring on this comparison.")
        else:
            cutoff = (f"Repeat window: {window} weeks. {fmt_number(immature)} recent trier(s) "
                      "are still within their window and excluded (maturity cutoff).")
        return (
            _headline_children(vf, window),
            _cards(vf, window),
            _build_scatter(vf),
            cutoff,
        )
