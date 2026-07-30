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
        # Bounded both sides + pinned trier count so the seed-lock is load-bearing:
        # a window/seed drift that moved the headline number fails here, not silently.
        s = tr.repeat_summary(52, sku=LEAKY)
        assert s["n_triers"] == 1234, f"leaky trier count drifted: {s['n_triers']}"
        assert s["repeat_rate"] == pytest.approx(0.14, abs=0.02), (
            f"leaky repeat {s['repeat_rate']:.1%} off the canonical ~14%")

    def test_sticky_is_high_repeat(self):
        s = tr.repeat_summary(52, sku=STICKY)
        assert s["n_triers"] == 428, f"sticky trier count drifted: {s['n_triers']}"
        assert s["repeat_rate"] == pytest.approx(0.51, abs=0.03), (
            f"sticky repeat {s['repeat_rate']:.1%} off the canonical ~51%")

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


# ── Empty slice degrades gracefully (no crash, no NaN, no div-by-zero) ─
class TestEmptySlice:
    NONE = "__no_such_retailer__"

    def test_repeat_summary_zeroed_not_error(self):
        s = tr.repeat_summary(52, retailer_id=self.NONE)
        assert s["n_triers"] == 0 and s["n_mature"] == 0
        assert s["n_repeaters"] == 0 and s["repeat_rate"] == 0.0

    def test_depth_zeroed_not_error(self):
        d = tr.depth_of_repeat(52, retailer_id=self.NONE)
        assert d["n_mature"] == 0
        assert all(v == 0.0 for v in d["shares"].values())

    def test_trial_curve_all_zero_but_twelve_rows(self):
        c = tr.trial_curve(retailer_id=self.NONE)
        assert len(c) == 12 and c["cumulative_triers"].iloc[-1] == 0

    def test_cohort_and_flow_return_empty_frames(self):
        assert tr.cohort_retention(retailer_id=self.NONE).empty
        assert tr.buyer_flow(retailer_id=self.NONE)["new"].sum() == 0


# ── buyer_flow accounting identities hold every row ───────────────────
class TestBuyerFlowIdentities:
    def _check(self, f):
        assert (f["new"] - f["lapsed"] == f["net"]).all()
        assert (f["retained"] + f["lapsed"] == f["prior_buyers"]).all()
        assert (f["retained"] + f["new"] == f["current_buyers"]).all()

    def test_brand_flow_identities(self):
        self._check(tr.buyer_flow())

    def test_item_flow_identities(self):
        self._check(tr.buyer_flow(sku=LEAKY))

    def test_whole_brand_flow_matches_the_panel_transactions(self):
        """Whole-brand flow reproduces the panel's own household universe.

        This asserted equality with the panel's ``get_buyer_flow()`` until
        2026-07-28. That premise broke at panel 0.2.0, which scales
        PROJECTED_FLOW_COLUMNS by the brand factor k (~166.5) while this app
        reports panel-measured households — so the old assertion compared two
        different scales and passed or failed purely on which vendored copy got
        resolved. A provenance guard made that failure legible; deriving the
        expectation from raw data removes it instead.

        ``get_transactions()`` is never projected, under either panel version, so
        this is version-independent by construction. See PLAN.md "Panel vendoring
        divergence" and DECISIONS.md "Panel-measured households, not brand-scale".
        """
        import cinderhaven_household_panel as hp

        tx = hp.get_transactions()
        quarters = hp.get_quarters()[["quarter_index", "label"]].sort_values("quarter_index")
        buyers = {qi: set(g["household_id"].unique()) for qi, g in tx.groupby("quarter_index")}
        labels = dict(zip(quarters["quarter_index"], quarters["label"]))
        indices = quarters["quarter_index"].tolist()

        expected = {}
        for prev, curr in zip(indices[:-1], indices[1:]):
            prior, current = buyers.get(prev, set()), buyers.get(curr, set())
            expected[labels[curr]] = {
                "prior_buyers": len(prior),
                "current_buyers": len(current),
                "retained": len(prior & current),
                "new": len(current - prior),
                "lapsed": len(prior - current),
            }

        ours = tr.buyer_flow().set_index("to_label")
        assert list(ours.index) == list(expected), "quarter pairs diverge from the panel"

        for label, exp in expected.items():
            # The identities must hold on the panel-derived figures too, or the
            # expectation is itself malformed and proves nothing.
            assert exp["retained"] + exp["lapsed"] == exp["prior_buyers"]
            assert exp["retained"] + exp["new"] == exp["current_buyers"]
            for col, want in exp.items():
                got = ours.loc[label, col]
                assert got == want, (
                    f"{col} at {label}: app has {got}, panel transactions give {want}"
                )

    def test_whole_brand_flow_is_panel_measured_not_brand_scale(self):
        """Counts stay raw households and are never multiplied by the factor k.

        Guards the decision in DECISIONS.md rather than a dtype: a count above the
        panel universe means brand-scale projection has leaked into a figure the
        Flow tab labels as panel households.
        """
        from cinderhaven_household_panel import N_HOUSEHOLDS

        flow = tr.buyer_flow()
        for col in ("prior_buyers", "current_buyers", "retained", "new", "lapsed"):
            assert flow[col].dtype.kind == "i", (
                f"{col} is {flow[col].dtype}, not an integer household count — "
                "the brand-projected panel has leaked in"
            )
            assert flow[col].max() <= N_HOUSEHOLDS, (
                f"{col} peaks at {flow[col].max()}, above the {N_HOUSEHOLDS}-household "
                "panel universe — brand-scale projection has leaked in"
            )


# ── The empty-slice verdict must be "No data", never a false "Promotion" ─
class TestVerdictNoData:
    def test_excluded_item_reads_no_data_not_promotion(self):
        # product_line 'AS' excludes both launch items (SB and PS lines).
        vf = tr.item_verdict(52, 0.30, product_line="AS").set_index("sku_id")
        assert (vf["verdict"] == tr.VERDICT_NO_DATA).all()
        assert (vf["n_mature"] == 0).all()

    def test_line_scoped_verdict_keeps_matching_item(self):
        # 'SB' keeps the leaky item (line SB), excludes the sticky (line PS).
        vf = tr.item_verdict(52, 0.30, product_line="SB").set_index("sku_id")
        assert vf.loc[LEAKY, "verdict"] == tr.VERDICT_PROMOTION
        assert vf.loc[STICKY, "verdict"] == tr.VERDICT_NO_DATA


# ── Filter path through the math (product_line / retailer actually filter) ─
class TestFilterPath:
    def test_product_line_narrows_trial(self):
        brand = tr.trial_curve()["cumulative_triers"].iloc[-1]
        one_line = tr.trial_curve(product_line="SB")["cumulative_triers"].iloc[-1]
        assert 0 < one_line < brand

    def test_retailer_narrows_repeat_denominator(self):
        brand = tr.repeat_summary(52)["n_triers"]
        # Any real retailer id from the panel yields a strictly smaller trier base.
        import cinderhaven_household_panel as hp
        rid = next(iter(hp.RETAILERS))
        scoped = tr.repeat_summary(52, retailer_id=rid)["n_triers"]
        assert 0 < scoped < brand


# ── Failed-trial trade burn (P2-5 dollarization) ─────────────────────
def test_failed_trial_burn_ties_to_depth_and_maturity():
    from app import trial_repeat as tr

    for sku in ("CHP-SB-010", "CHP-PS-010"):
        summary = tr.repeat_summary(12, sku=sku)
        burn = tr.failed_trial_burn(12, sku=sku)
        # failed = mature minus repeaters, exactly
        assert burn["n_failed"] == summary["n_mature"] - summary["n_repeaters"]
        # burn is the assumed depth applied to failed first-purchase spend
        assert burn["burn"] == burn["failed_trial_spend"] * tr.TRIAL_PROMO_DEPTH
        assert burn["failed_trial_spend"] > 0


def test_failed_trial_burn_empty_slice_is_zero():
    from app import trial_repeat as tr

    out = tr.failed_trial_burn(12, product_line="AS", sku="CHP-SB-010")
    assert out == {"n_failed": 0, "failed_trial_spend": 0.0, "burn": 0.0}
