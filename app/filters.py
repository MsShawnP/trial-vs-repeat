"""Shared filter bar component and callbacks.

Cloned from Decompose's filters, adapted to Leaky Bucket's controls: Scope (whole
brand or one launch item), Repeat window (the right-censoring parameter), Product
line, Retailer. Options come from the in-process panel at build time, so there is no
populate-from-DB callback.
"""

import json

from dash import Input, Output, callback, dcc, html

from app import panel_data

DEFAULT_FILTER_STATE = {
    "scope": panel_data.SCOPE_BRAND,
    "repeat_window": panel_data.DEFAULT_REPEAT_WINDOW_WEEKS,
    "product_line": "__all__",
    "retailer": "__all__",
}


def parse_filter_state(filter_json: str | None):
    """Decode the shared filter-state store into (scope, repeat_window, line, retailer).

    The single reader of the filter-state JSON contract — every view calls this instead
    of re-decoding the store, so the four-key shape lives in one place.
    """
    f = json.loads(filter_json) if filter_json else {}
    return (
        f.get("scope") or panel_data.SCOPE_BRAND,
        int(f.get("repeat_window") or panel_data.DEFAULT_REPEAT_WINDOW_WEEKS),
        f.get("product_line") or "__all__",
        f.get("retailer") or "__all__",
    )


def _window_options():
    return [{"label": f"{w} weeks", "value": w} for w in panel_data.REPEAT_WINDOW_OPTIONS]


def build_filter_bar():
    """Return the filter bar: Scope, Repeat window, Product line, Retailer."""
    return html.Div(
        [
            html.Div(
                [
                    html.Label(
                        "Scope",
                        title="Analyze the whole brand, or zoom into one launch item.",
                    ),
                    dcc.Dropdown(
                        id="filter-scope",
                        options=panel_data.scope_options(),
                        value=panel_data.SCOPE_BRAND,
                        clearable=False,
                        searchable=False,
                    ),
                ],
                className="filter-group",
                style={"minWidth": "200px", "flex": "1"},
            ),
            html.Div(
                [
                    html.Label(
                        "Repeat window",
                        title="How long a trier has to come back and still count as a "
                        "repeat. Longer windows suit categories that repeat slowly.",
                    ),
                    dcc.Dropdown(
                        id="filter-repeat-window",
                        options=_window_options(),
                        value=panel_data.DEFAULT_REPEAT_WINDOW_WEEKS,
                        clearable=False,
                        searchable=False,
                    ),
                ],
                className="filter-group",
                style={"minWidth": "150px", "flex": "1"},
            ),
            html.Div(
                [
                    html.Label(
                        "Product line",
                        title="Narrow to one product line, or keep All lines for the whole brand.",
                    ),
                    dcc.Dropdown(
                        id="filter-product-line",
                        options=panel_data.product_line_options(),
                        value="__all__",
                        clearable=False,
                        searchable=False,
                    ),
                ],
                className="filter-group",
                style={"minWidth": "180px", "flex": "1"},
            ),
            html.Div(
                [
                    html.Label(
                        "Retailer",
                        title="Narrow to one retailer, or keep All retailers for every channel.",
                    ),
                    dcc.Dropdown(
                        id="filter-retailer",
                        options=panel_data.retailer_options(),
                        value="__all__",
                        clearable=False,
                        searchable=False,
                    ),
                ],
                className="filter-group",
                style={"minWidth": "180px", "flex": "1"},
            ),
        ],
        className="filter-bar",
    )


def register_filter_callbacks():
    """Register filter callbacks — sync the four controls into the shared store."""

    @callback(
        Output("filter-state", "data"),
        Input("filter-scope", "value"),
        Input("filter-repeat-window", "value"),
        Input("filter-product-line", "value"),
        Input("filter-retailer", "value"),
    )
    def _sync_filter_state(scope, repeat_window, product_line, retailer):
        return json.dumps(
            {
                "scope": scope or panel_data.SCOPE_BRAND,
                "repeat_window": repeat_window or panel_data.DEFAULT_REPEAT_WINDOW_WEEKS,
                "product_line": product_line or "__all__",
                "retailer": retailer or "__all__",
            }
        )
