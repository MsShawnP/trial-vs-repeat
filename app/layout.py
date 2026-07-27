"""Layout assembly — brand frame, tab navigation, filter bar, and content area.

Cloned from Decompose's shell. All data is in-process via panel_data. The three tab
panels are pre-rendered and toggled by display so each view's callbacks always find
their targets in the DOM (a style change can't silently disconnect a tab — there's a
regression test for exactly that).
"""

import json
import logging

from dash import Input, Output, callback, dcc, html

from app import lailara_frame, panel_data
from app.app import app
from app.filters import (
    DEFAULT_FILTER_STATE,
    build_filter_bar,
    register_filter_callbacks,
)
from app.views import cohort, flow, verdict

logger = logging.getLogger(__name__)

TAB_LABELS = ["Trial vs Repeat", "Cohort Retention", "Leaky Bucket Flow"]
TAB_IDS = ["verdict", "cohort", "flow"]


def _build_tabs():
    return dcc.Tabs(
        id="main-tabs",
        value="verdict",
        children=[
            dcc.Tab(
                label=label,
                value=value,
                className="custom-tab",
                selected_className="custom-tab--selected",
            )
            for label, value in zip(TAB_LABELS, TAB_IDS)
        ],
        className="custom-tabs",
    )


def _build_content_area():
    """Pre-render all three tab panels; a callback toggles display."""
    return html.Div(
        [
            html.Div(verdict.layout(), id="tab-panel-verdict", style={"display": "block"}),
            html.Div(cohort.layout(), id="tab-panel-cohort", style={"display": "none"}),
            html.Div(flow.layout(), id="tab-panel-flow", style={"display": "none"}),
        ]
    )


def _build_page_intro():
    """The tool's purpose in one plain line — what it answers, before any chart.

    A CEO/CFO landing cold should know what this tool is *for* within a few seconds,
    without opening 'Why this matters' or reading the footer. This is the umbrella
    question all three tabs serve.
    """
    return html.Div(
        [
            html.P(
                "Of the households that tried this brand, how many came back?",
                className="page-intro-lead",
            ),
            html.P(
                "Repeat rate separates real adoption from expensive sampling — a brand "
                "from a promotion. Household penetration can climb every quarter while "
                "the bucket quietly leaks.",
                className="page-intro-sub",
            ),
        ],
        className="page-intro",
    )


def _build_as_of_note():
    """As-of date + synthetic-data disclosure (both required on an exec-facing page)."""
    as_of = panel_data.AS_OF_DATE.strftime("%b %d, %Y")
    return html.Div(
        [
            html.Span(f"Panel as of {as_of}", className="as-of-chip"),
            html.Span(
                "Synthetic Cinderhaven data — a demonstration of the method, not a "
                "real brand.",
                className="synthetic-note",
            ),
        ],
        className="as-of-row",
    )


def register_layout():
    """Set app.layout and register all callbacks."""
    inner_layout = html.Div(
        [
            dcc.Store(
                id="filter-state",
                storage_type="session",
                data=json.dumps(DEFAULT_FILTER_STATE),
            ),
            html.Div(
                [
                    _build_page_intro(),
                    _build_as_of_note(),
                    _build_tabs(),
                    build_filter_bar(),
                    _build_content_area(),
                ],
                className="lailara-container",
            ),
        ]
    )

    app.layout = lailara_frame.wrap(
        inner_layout,
        tool_name="Leaky Bucket",
        footer_note="Trial vs repeat for CPG brands — of the households that tried you, "
        "how many came back, and is penetration growth real adoption or expensive sampling.",
        no_container=True,
    )

    register_filter_callbacks()
    verdict.register_callbacks()
    cohort.register_callbacks()
    flow.register_callbacks()

    @callback(
        Output("tab-panel-verdict", "style"),
        Output("tab-panel-cohort", "style"),
        Output("tab-panel-flow", "style"),
        Input("main-tabs", "value"),
    )
    def _toggle_tab_visibility(tab_value):
        """Show the active tab panel, hide the rest."""
        show = {"display": "block"}
        hide = {"display": "none"}
        return (
            show if tab_value == "verdict" else hide,
            show if tab_value == "cohort" else hide,
            show if tab_value == "flow" else hide,
        )
