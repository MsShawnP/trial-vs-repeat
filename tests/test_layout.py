"""Layout & tab-wiring regression gates.

Void Finder once shipped with a tab whose content callback got silently disconnected
by a style change. These tests fail if (a) the tab-visibility callback is missing, or
(b) any tab panel stops rendering its own distinct content.
"""

from dash import Dash


def _collect_ids(component):
    """Recursively collect every component id in a Dash layout tree."""
    ids = set()
    cid = getattr(component, "id", None)
    if isinstance(cid, str):
        ids.add(cid)
    children = getattr(component, "children", None)
    if children is None:
        return ids
    if not isinstance(children, (list, tuple)):
        children = [children]
    for child in children:
        if hasattr(child, "to_plotly_json"):
            ids |= _collect_ids(child)
    return ids


def test_each_view_renders_its_own_distinct_chart():
    from app.views import cohort, flow, verdict

    assert "verdict-chart" in _collect_ids(verdict.layout())
    assert "cohort-heatmap" in _collect_ids(cohort.layout())
    assert "flow-chart" in _collect_ids(flow.layout())
    # And they are genuinely distinct — no shared chart id across views.
    v, c, f = _collect_ids(verdict.layout()), _collect_ids(cohort.layout()), _collect_ids(flow.layout())
    charts = {"verdict-chart", "cohort-heatmap", "depth-chart", "flow-chart", "trial-curve"}
    assert (v & charts) and (c & charts) and (f & charts)
    assert not (v & charts) & (c & charts)  # verdict's charts != cohort's charts


def _callback_keys():
    """All registered callback output specs (views use @callback → global registry)."""
    from dash._callback import GLOBAL_CALLBACK_MAP
    from app.app import app

    return " ".join(list(GLOBAL_CALLBACK_MAP.keys()) + list(app.callback_map.keys()))


def test_tab_visibility_callback_is_wired():
    from app.app import app
    from app.layout import register_layout

    register_layout()
    assert app.layout is not None
    # The tab-visibility callback must exist: main-tabs value → each tab panel's style.
    keys = _callback_keys()
    for panel in ("tab-panel-verdict", "tab-panel-cohort", "tab-panel-flow"):
        assert f"{panel}.style" in keys, f"{panel} visibility callback missing"


def test_all_view_callbacks_registered():
    from app.layout import register_layout

    register_layout()
    keys = _callback_keys()
    # Each view's data callback must be registered (its primary output present).
    for output in ("verdict-chart.figure", "cohort-heatmap.figure", "flow-chart.figure",
                   "filter-state.data"):
        assert output in keys, f"missing callback output {output}"
