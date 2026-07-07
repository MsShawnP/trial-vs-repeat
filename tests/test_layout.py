"""Layout & tab-wiring regression gates.

Void Finder once shipped with a tab whose content callback got silently disconnected
by a style change. These tests fail if (a) the tab-visibility callback is missing, or
(b) any tab panel stops rendering its own distinct content.
"""

def _walk(component):
    """Yield every component in a Dash layout tree (depth-first)."""
    yield component
    children = getattr(component, "children", None)
    if children is None:
        return
    if not isinstance(children, (list, tuple)):
        children = [children]
    for child in children:
        if hasattr(child, "to_plotly_json"):
            yield from _walk(child)


def _collect_ids(component):
    """Recursively collect every component id in a Dash layout tree."""
    return {getattr(c, "id", None) for c in _walk(component)
            if isinstance(getattr(c, "id", None), str)}


def _classnames(component):
    """All className strings present anywhere in a layout tree."""
    return " ".join(str(getattr(c, "className", "")) for c in _walk(component))


def _texts(component):
    """All string leaves in a layout tree (for text-content assertions)."""
    out = []
    for c in _walk(component):
        ch = getattr(c, "children", None)
        if isinstance(ch, str):
            out.append(ch)
    return " ".join(out)


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


def test_exec_content_contract_is_present():
    """The exec-facing page must keep its headline, why-panel, glossary, and the
    synthetic-data disclosure — a regression that drops any of these ships silently."""
    from app.app import app
    from app.layout import register_layout

    register_layout()
    classes = _classnames(app.layout)
    texts = _texts(app.layout)
    assert "verdict-headline" in " ".join(_collect_ids(app.layout))  # plain headline
    assert "why-details" in classes                                  # why-this-matters panel(s)
    assert "glossary-details" in classes                             # glossary
    assert "synthetic-note" in classes                               # disclosure element
    assert "Synthetic Cinderhaven data" in texts                     # disclosure text


def test_filter_controls_have_tooltips():
    """The exec rule: every filter carries a tooltip (title=)."""
    from app.filters import build_filter_bar

    tips = [getattr(c, "title", None) for c in _walk(build_filter_bar())]
    labeled = [t for t in tips if t]
    assert len(labeled) >= 4  # scope, repeat window, product line, retailer
