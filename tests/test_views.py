"""Figure-builder gates — the view builders contain real logic (pivots, sign flips,
np.vectorize over NaN, .max() fallbacks) that registration tests don't exercise. These
run each builder on real AND empty data so a registered-but-broken chart can't ship."""

import plotly.graph_objects as go

from app import panel_data
from app.constants import BRAND_REPEAT_THRESHOLD as TH
from app.views import cohort, flow, verdict

NONE = "__no_such_retailer__"


# ── Builders produce valid figures on real data, with correct structure ─
def test_verdict_scatter_plots_two_items():
    vf = panel_data.item_verdict(52, TH)
    fig = verdict._build_scatter(vf)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # one marker trace per launch item


def test_cohort_triangle_offset_zero_is_full_retention():
    ret = panel_data.cohort_retention(sku="CHP-SB-010")
    fig = cohort._build_triangle(ret)
    assert isinstance(fig, go.Figure) and len(fig.data) == 1
    # The heatmap's first column (offset 0) must be all 1.0 (ignoring NaN padding).
    z0 = [row[0] for row in fig.data[0].z]
    assert all(v == 1.0 for v in z0 if v is not None)


def test_flow_chart_has_bars_plus_net_line_and_lapsed_below_zero():
    fig = flow._build_flow(panel_data.get_flow())
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 4  # retained, new, lapsed bars + net line
    lapsed = next(t for t in fig.data if t.name == "Lapsed (out)")
    assert all(v <= 0 for v in lapsed.y)  # churn drawn below zero


def test_trial_curve_is_monotonic_in_the_figure():
    fig = flow._build_trial_curve(panel_data.trial_curve())
    ys = list(fig.data[0].y)
    assert ys == sorted(ys)  # cumulative, non-decreasing


def test_depth_chart_three_buckets():
    fig = cohort._build_depth(panel_data.depth_of_repeat(52, sku="CHP-PS-010"), 52)
    assert isinstance(fig, go.Figure)
    assert len(fig.data[0].x) == 3  # 1x / 2x / 3x+


# ── Every builder survives an empty slice (the cohort KeyError regression) ─
def test_all_builders_survive_empty_slice():
    vf = panel_data.item_verdict(52, TH, product_line="AS")  # excludes both items
    assert isinstance(verdict._build_scatter(vf), go.Figure)  # no points, no crash

    ret = panel_data.cohort_retention(retailer_id=NONE)       # empty frame
    assert isinstance(cohort._build_triangle(ret), go.Figure)  # was a KeyError before the fix

    assert isinstance(cohort._build_depth(panel_data.depth_of_repeat(52, retailer_id=NONE), 52), go.Figure)
    assert isinstance(flow._build_flow(panel_data.get_flow(retailer_id=NONE)), go.Figure)
    assert isinstance(flow._build_trial_curve(panel_data.trial_curve(retailer_id=NONE)), go.Figure)
