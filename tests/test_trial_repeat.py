"""Trial/repeat math gates — the credibility make-or-break.

These verify the two things a CFO's trust hangs on: (1) the maturity cutoff really
excludes right-censored triers from summary repeat numbers, and (2) the two seeded
launch stories reproduce (leaky is trial-heavy / repeat-light; sticky is the opposite).
Numbers are computed from the panel, never asserted into it.
"""

import pandas as pd
import pytest

import cinderhaven_household_panel as panel
from app import trial_repeat as tr

AS_OF = pd.Timestamp(panel.DEMO_AS_OF_DATE)
LEAKY = "CHP-SB-010"
STICKY = "CHP-PS-010"


# ── Maturity cutoff / right-censoring ─────────────────────────────────
class TestMaturityCutoff:
    def test_cutoff_date_is_as_of_minus_window(self):
        s = tr.repeat_summary(52)
        assert s["maturity_cutoff_date"] == AS_OF - pd.Timedelta(weeks=52)

    def test_recent_triers_are_excluded_as_immature(self):
        # Brand-level with a 52-week window: households whose first-ever brand purchase
        # falls in the last year cannot have had a full window, so they must be immature.
        s = tr.repeat_summary(52)
        assert s["n_immature"] > 0, "a 52w window must leave recent triers immature"
        assert s["n_mature"] + s["n_immature"] == s["n_triers"]

    def test_repeat_rate_denominator_is_mature_only(self):
        # The rate must be repeaters / mature triers, never repeaters / all triers.
        s = tr.repeat_summary(52)
        assert s["n_repeaters"] <= s["n_mature"]
        expected = s["n_repeaters"] / s["n_mature"]
        assert s["repeat_rate"] == pytest.approx(expected)

    def test_longer_window_leaves_more_immature(self):
        # A wider window pushes the cutoff earlier, so at least as many triers are immature.
        short = tr.repeat_summary(8)
        long = tr.repeat_summary(52)
        assert long["n_immature"] >= short["n_immature"]

    def test_launch_items_are_always_mature(self):
        # Both launch items trial in 2023-Q2, so every trier is mature even at 52w —
        # this is what makes the demo stable.
        for sku in (LEAKY, STICKY):
            s = tr.repeat_summary(52, sku=sku)
            assert s["n_immature"] == 0
            assert s["n_mature"] == s["n_triers"] > 0


# ── The two launch stories reproduce ──────────────────────────────────
class TestLaunchStories:
    def test_leaky_is_trial_heavy_repeat_light(self):
        s = tr.repeat_summary(52, sku=LEAKY)
        assert s["n_triers"] > 800, "leaky item should have a big trial reach"
        assert 0.10 <= s["repeat_rate"] <= 0.20, f"leaky repeat {s['repeat_rate']:.1%} outside 10-20%"

    def test_sticky_is_high_repeat(self):
        s = tr.repeat_summary(52, sku=STICKY)
        assert s["repeat_rate"] >= 0.45, f"sticky repeat {s['repeat_rate']:.1%} below 45%"

    def test_sticky_beats_leaky_at_every_window(self):
        for w in (8, 12, 26, 52):
            leaky = tr.repeat_summary(w, sku=LEAKY)["repeat_rate"]
            sticky = tr.repeat_summary(w, sku=STICKY)["repeat_rate"]
            assert sticky > leaky, f"at {w}w sticky {sticky:.1%} !> leaky {leaky:.1%}"

    def test_leaky_has_larger_trial_reach_than_sticky(self):
        leaky = tr.repeat_summary(52, sku=LEAKY)["n_triers"]
        sticky = tr.repeat_summary(52, sku=STICKY)["n_triers"]
        assert leaky > sticky

    def test_verdict_flags_promotion_vs_brand(self):
        v = tr.item_verdict(52, threshold=0.30).set_index("sku_id")
        assert v.loc[LEAKY, "verdict"] == "Promotion"
        assert v.loc[STICKY, "verdict"] == "Brand"


# ── Trial curve ───────────────────────────────────────────────────────
class TestTrialCurve:
    def test_cumulative_is_monotonic_and_bounded(self):
        c = tr.trial_curve()
        assert c["cumulative_triers"].is_monotonic_increasing
        assert (c["cumulative_trial_rate"] >= 0).all()
        assert (c["cumulative_trial_rate"] <= 1.0).all()

    def test_new_triers_sum_to_final_cumulative(self):
        c = tr.trial_curve()
        assert c["new_triers"].sum() == c["cumulative_triers"].iloc[-1]

    def test_all_twelve_quarters_present(self):
        c = tr.trial_curve()
        assert len(c) == panel.TOTAL_QUARTERS == 12


# ── Cohort retention triangle ─────────────────────────────────────────
class TestCohortRetention:
    def test_offset_zero_is_full_retention(self):
        ret = tr.cohort_retention(sku=LEAKY)
        assert (ret.loc[ret["offset"] == 0, "retention"] == 1.0).all()

    def test_retention_within_unit_interval(self):
        ret = tr.cohort_retention()
        assert (ret["retention"] >= 0).all() and (ret["retention"] <= 1.0).all()

    def test_recent_cohorts_have_fewer_offsets(self):
        # Right-censoring shown structurally: the last cohort has only offset 0.
        ret = tr.cohort_retention()
        last = ret["cohort_qi"].max()
        assert ret.loc[ret["cohort_qi"] == last, "offset"].max() == 0


# ── Depth of repeat ───────────────────────────────────────────────────
class TestDepthOfRepeat:
    def test_buckets_sum_to_mature_triers(self):
        d = tr.depth_of_repeat(52, sku=STICKY)
        assert sum(d["counts"].values()) == d["n_mature"]

    def test_shares_sum_to_one(self):
        d = tr.depth_of_repeat(52, sku=STICKY)
        assert sum(d["shares"].values()) == pytest.approx(1.0)

    def test_leaky_is_shallower_than_sticky(self):
        # More of the leaky item's triers never come back (1x share higher).
        leaky = tr.depth_of_repeat(52, sku=LEAKY)["shares"]["1x"]
        sticky = tr.depth_of_repeat(52, sku=STICKY)["shares"]["1x"]
        assert leaky > sticky
