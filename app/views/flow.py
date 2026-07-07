"""Leaky Bucket Flow view — buyers in vs out per quarter, plus the trial curve.

The bucket: each quarter households flow in (new) and out (lapsed). The net line is
whether the bucket is filling or draining. Penetration can climb while the bucket
leaks — this is the chart that shows it. The trial curve underneath is the cumulative
first-ever-buyer count: how fast you acquired, regardless of whether they stayed.
"""

import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from app import panel_data
from app.charts import CHART_CONFIG, economist_layout
from app.components import view_heading, why_this_matters
from app.constants import (
    FLOW_LAPSED,
    FLOW_NET,
    FLOW_NEW,
    FLOW_RETAINED,
    FONT_SANS,
    FONT_SERIF,
    INK,
    REFERENCE,
    TEXT_SECONDARY,
    TRIAL_COLOR,
    fmt_number,
)

_WHY = (
    "Trial and penetration only tell you who came in. The bucket tells you whether "
    "they stayed. A brand whose net line sits below zero is spending to refill a "
    "leaking bucket — the moment acquisition slows, penetration falls. The trial curve "
    "shows acquisition speed; the flow shows whether it was worth it."
)


def layout():
    return html.Div(
        [
            view_heading(
                "The leaky bucket",
                "Buyers flow in and out every quarter. The net line is whether the "
                "bucket is filling or draining — the thing penetration alone hides.",
            ),
            dcc.Graph(id="flow-chart", config=CHART_CONFIG, style={"minHeight": "420px"}),
            html.P(
                "Above zero: households retained from the prior quarter plus new ones. "
                "Below zero: households that lapsed. The line is the net change.",
                className="chart-caption",
            ),
            dcc.Graph(id="trial-curve", config=CHART_CONFIG, style={"minHeight": "360px"}),
            html.P(
                "Cumulative share of all panel households that had made their first-ever "
                "purchase by each quarter — acquisition speed, before any repeat.",
                className="chart-caption",
            ),
            why_this_matters(_WHY),
        ],
        className="view flow-view",
    )


def _build_flow(flow):
    x = flow["to_label"].tolist()
    retained = flow["retained"].tolist()
    new = flow["new"].tolist()
    lapsed = [-v for v in flow["lapsed"].tolist()]  # below zero = churn out
    net = flow["net"].tolist()

    label_font = dict(family=FONT_SANS, size=10, color="#ffffff")
    fig = go.Figure()
    fig.add_bar(
        x=x, y=retained, name="Retained", marker_color=FLOW_RETAINED,
        text=retained, texttemplate="%{text:,}", textposition="inside",
        insidetextfont=label_font,
        hovertemplate="%{x}<br>Retained %{y:,}<extra></extra>",
    )
    fig.add_bar(
        x=x, y=new, name="New (in)", marker_color=FLOW_NEW,
        text=new, texttemplate="%{text:,}", textposition="inside",
        insidetextfont=label_font,
        hovertemplate="%{x}<br>New %{y:,}<extra></extra>",
    )
    fig.add_bar(
        x=x, y=lapsed, name="Lapsed (out)", marker_color=FLOW_LAPSED,
        customdata=flow["lapsed"].tolist(),
        text=flow["lapsed"].tolist(), texttemplate="%{text:,}", textposition="inside",
        insidetextfont=label_font,
        hovertemplate="%{x}<br>Lapsed %{customdata:,}<extra></extra>",
    )
    fig.add_trace(
        go.Scatter(
            x=x, y=net, name="Net", mode="lines+markers",
            line=dict(color=FLOW_NET, width=2.5),
            marker=dict(size=7, color=FLOW_NET),
            hovertemplate="%{x}<br>Net %{y:+,}<extra></extra>",
        )
    )

    layout = economist_layout(
        title=dict(text="Buyers in vs out, by quarter",
                   font=dict(family=FONT_SERIF, size=22, color=INK)),
        barmode="relative",
        uniformtext=dict(minsize=8, mode="hide"),
        yaxis=dict(
            title=dict(text="Households", font=dict(family=FONT_SANS, size=14, color=TEXT_SECONDARY)),
            showgrid=True, gridcolor="#e6e4dd", showline=False, automargin=True,
            zeroline=True, zerolinecolor=REFERENCE, zerolinewidth=1.5,
            tickformat=",.0f",
            tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
        ),
        margin=dict(l=68, r=24, t=64, b=64),
    )
    fig.update_layout(**layout)
    return fig


def _build_trial_curve(curve):
    x = curve["quarter_label"].tolist()
    y = curve["cumulative_trial_rate"].tolist()
    triers = curve["cumulative_triers"].tolist()

    fig = go.Figure(
        go.Scatter(
            x=x, y=y, mode="lines+markers+text", name="Cumulative trial",
            line=dict(color=TRIAL_COLOR, width=3),
            marker=dict(size=7, color=TRIAL_COLOR),
            text=[f"{v:.0%}" for v in y],
            textposition="top center",
            textfont=dict(family=FONT_SANS, size=10, color=INK),
            cliponaxis=False,
            customdata=triers,
            hovertemplate="%{x}<br>%{y:.1%} tried (%{customdata:,} households)<extra></extra>",
        )
    )
    y_max = max(y) if y else 0.1
    layout = economist_layout(
        title=dict(text="Cumulative trial — first-ever buyers",
                   font=dict(family=FONT_SERIF, size=22, color=INK)),
        yaxis=dict(
            title=dict(text="Households that have tried (share)",
                       font=dict(family=FONT_SANS, size=14, color=TEXT_SECONDARY)),
            showgrid=True, gridcolor="#e6e4dd", showline=False, automargin=True,
            tickformat=".0%", rangemode="tozero",
            range=[0, y_max * 1.2 if y_max else 1],
            tickfont=dict(family=FONT_SANS, size=12, color=TEXT_SECONDARY),
        ),
        showlegend=False,
        margin=dict(l=64, r=24, t=64, b=44),
    )
    fig.update_layout(**layout)
    return fig


def register_callbacks():
    @callback(
        Output("flow-chart", "figure"),
        Output("trial-curve", "figure"),
        Input("filter-state", "data"),
    )
    def _update(filter_json):
        from app.filters import parse_filter_state

        scope, _window, line, retailer = parse_filter_state(filter_json)
        sku = panel_data.scope_sku(scope)
        flow = panel_data.get_flow(line, retailer, sku)
        curve = panel_data.trial_curve(line, retailer, sku)
        return _build_flow(flow), _build_trial_curve(curve)
