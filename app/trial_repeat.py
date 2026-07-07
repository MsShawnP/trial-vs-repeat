"""Trial and repeat math — the analysis tool #4 adds on top of the shared panel.

Everything here is a pure read-side computation over ``get_transactions()``. Nothing
is seeded or hardcoded: trial is the first-ever purchase, repeat is a later purchase
within a window, and every summary number applies a maturity cutoff so recent triers
who have not yet had a full window to repeat are excluded (right-censoring — the
credibility make-or-break). The repeat window is a parameter throughout.

Grain notes:
- The panel spans burn-in (2023) + analysis (2024-2025); first-ever purchases are
  identified against the FULL history, which is why the burn-in runway matters.
- The two launch items (CHP-SB-010 leaky, CHP-PS-010 sticky) both launch in 2023-Q2,
  so their triers are always mature — the demo is stable at any window.
"""

import pandas as pd

import cinderhaven_household_panel as panel

AS_OF = pd.Timestamp(panel.DEMO_AS_OF_DATE)
N_HOUSEHOLDS = panel.N_HOUSEHOLDS


# ── Filtering ─────────────────────────────────────────────────────────
def _tx(product_line=None, retailer_id=None, sku=None) -> pd.DataFrame:
    """The transaction slice for a filter combination (brand-level unless sku given)."""
    tx = panel.get_transactions()
    if sku is not None:
        tx = tx[tx["sku_id"] == sku]
    if product_line is not None:
        tx = tx[tx["product_line"] == product_line]
    if retailer_id is not None:
        tx = tx[tx["retailer_id"] == retailer_id]
    return tx


def _first_purchase(tx: pd.DataFrame) -> pd.DataFrame:
    """Each household's first-ever purchase in this slice: the trial event.

    Columns: household_id, first_date, first_qi, first_ql. One row per household that
    ever bought in the slice.
    """
    fp = (
        tx.sort_values("date")
        .drop_duplicates("household_id", keep="first")
        .loc[:, ["household_id", "date", "quarter_index", "quarter_label"]]
        .rename(columns={"date": "first_date", "quarter_index": "first_qi",
                         "quarter_label": "first_ql"})
        .reset_index(drop=True)
    )
    return fp


def _window(weeks: int) -> pd.Timedelta:
    return pd.Timedelta(weeks=weeks)


# ── Trial ─────────────────────────────────────────────────────────────
def trial_curve(product_line=None, retailer_id=None, sku=None) -> pd.DataFrame:
    """Cumulative first-ever-buyer curve, by quarter (calendar order, all 12 quarters).

    Columns: quarter_index, quarter_label, is_analysis, new_triers, cumulative_triers,
    cumulative_trial_rate (cumulative triers / all panel households).
    """
    from cinderhaven_household_panel import get_quarters

    tx = _tx(product_line, retailer_id, sku)
    fp = _first_purchase(tx)
    quarters = get_quarters()[["quarter_index", "label", "is_analysis"]].sort_values("quarter_index")

    new_by_q = fp.groupby("first_qi").size()
    rows = []
    cumulative = 0
    for qi, label, is_analysis in quarters.itertuples(index=False):
        new_triers = int(new_by_q.get(qi, 0))
        cumulative += new_triers
        rows.append({
            "quarter_index": qi,
            "quarter_label": label,
            "is_analysis": bool(is_analysis),
            "new_triers": new_triers,
            "cumulative_triers": cumulative,
            "cumulative_trial_rate": cumulative / N_HOUSEHOLDS,
        })
    return pd.DataFrame(rows)


# ── Repeat (with maturity cutoff) ─────────────────────────────────────
def repeat_summary(window_weeks: int, product_line=None, retailer_id=None, sku=None) -> dict:
    """Repeat rate within ``window_weeks`` of first purchase, maturity-cutoff applied.

    A trier is *mature* if a full window has elapsed between their first purchase and
    the panel's as-of date; only mature triers count toward the repeat rate (recent
    triers who could not yet have repeated are excluded, not counted as non-repeaters).
    A trier *repeats* if they made any further purchase in the slice strictly after
    their first purchase and within the window.

    Returns: n_triers, n_mature, n_immature, n_repeaters, repeat_rate,
    maturity_cutoff_date (triers whose first purchase is after this are immature),
    window_weeks.
    """
    tx = _tx(product_line, retailer_id, sku)
    fp = _first_purchase(tx)
    win = _window(window_weeks)

    fp["mature"] = fp["first_date"] + win <= AS_OF
    mature = fp[fp["mature"]]

    if len(mature):
        joined = tx.merge(mature[["household_id", "first_date"]], on="household_id")
        in_window = (joined["date"] > joined["first_date"]) & (
            joined["date"] <= joined["first_date"] + win
        )
        joined = joined.assign(is_repeat=in_window)
        repeated = joined.groupby("household_id")["is_repeat"].any()
        n_repeaters = int(repeated.sum())
        repeat_rate = n_repeaters / len(mature)
    else:
        n_repeaters = 0
        repeat_rate = 0.0

    return {
        "n_triers": len(fp),
        "n_mature": len(mature),
        "n_immature": int((~fp["mature"]).sum()),
        "n_repeaters": n_repeaters,
        "repeat_rate": repeat_rate,
        "maturity_cutoff_date": (AS_OF - win),
        "window_weeks": window_weeks,
    }


# ── Cohort retention triangle ─────────────────────────────────────────
def cohort_retention(product_line=None, retailer_id=None, sku=None) -> pd.DataFrame:
    """Retention triangle: cohort by first-purchase quarter × later-quarter retention.

    For cohort c (households whose first purchase was quarter c) and quarter q >= c,
    retention = share of the cohort who purchased again in quarter q. Offset 0 is
    always 1.0 (the trial quarter). Recent cohorts have fewer observable offsets — the
    triangle shape IS the right-censoring, shown rather than hidden.

    Columns: cohort_qi, cohort_label, cohort_size, quarter_index, offset, retention.
    """
    from cinderhaven_household_panel import get_quarters

    tx = _tx(product_line, retailer_id, sku)
    fp = _first_purchase(tx)
    labels = dict(zip(get_quarters()["quarter_index"], get_quarters()["label"]))
    max_qi = int(tx["quarter_index"].max()) if len(tx) else 0

    buyers_by_q = {qi: set(g["household_id"].unique()) for qi, g in tx.groupby("quarter_index")}

    rows = []
    for cohort_qi, group in fp.groupby("first_qi"):
        members = set(group["household_id"])
        size = len(members)
        for q in range(cohort_qi, max_qi + 1):
            retained = len(members & buyers_by_q.get(q, set()))
            rows.append({
                "cohort_qi": cohort_qi,
                "cohort_label": labels[cohort_qi],
                "cohort_size": size,
                "quarter_index": q,
                "offset": q - cohort_qi,
                "retention": retained / size,
            })
    return pd.DataFrame(rows)


# ── Depth of repeat ───────────────────────────────────────────────────
def depth_of_repeat(window_weeks: int, product_line=None, retailer_id=None, sku=None) -> dict:
    """Distribution of purchase depth among mature triers, within the window.

    Depth = number of distinct purchase days in [first_purchase, first_purchase +
    window]. 1x = trial only (never came back), 2x = came back once, 3x+ = twice or
    more. Returns counts and shares per bucket plus n_mature.
    """
    tx = _tx(product_line, retailer_id, sku)
    fp = _first_purchase(tx)
    win = _window(window_weeks)
    fp["mature"] = fp["first_date"] + win <= AS_OF
    mature = fp[fp["mature"]]

    buckets = {"1x": 0, "2x": 0, "3x+": 0}
    if len(mature):
        joined = tx.merge(mature[["household_id", "first_date"]], on="household_id")
        joined = joined[
            (joined["date"] >= joined["first_date"])
            & (joined["date"] <= joined["first_date"] + win)
        ]
        trips = joined.groupby("household_id")["date"].nunique()
        # Triers with no in-window row at all (shouldn't happen — the trial is in
        # window) default to 1x via reindex.
        trips = trips.reindex(mature["household_id"], fill_value=1)
        buckets["1x"] = int((trips == 1).sum())
        buckets["2x"] = int((trips == 2).sum())
        buckets["3x+"] = int((trips >= 3).sum())

    n = len(mature)
    shares = {k: (v / n if n else 0.0) for k, v in buckets.items()}
    return {"counts": buckets, "shares": shares, "n_mature": n}


# ── Per-item verdict: promotion or brand? ─────────────────────────────
def item_verdict(window_weeks: int, threshold: float, product_line=None, retailer_id=None) -> pd.DataFrame:
    """Trial reach vs mature repeat rate per launch item, with a promotion/brand verdict.

    A trial-heavy, repeat-light item (repeat below ``threshold``) reads as a promotion;
    at or above threshold it reads as a brand. Columns: sku_id, role, launch_label,
    n_triers, trial_reach, n_mature, repeat_rate, verdict.
    """
    rows = []
    for sku, cfg in panel.LAUNCH_ITEMS.items():
        summary = repeat_summary(window_weeks, product_line, retailer_id, sku=sku)
        trial_reach = summary["n_triers"] / N_HOUSEHOLDS
        repeat_rate = summary["repeat_rate"]
        verdict = "Brand" if repeat_rate >= threshold else "Promotion"
        rows.append({
            "sku_id": sku,
            "role": cfg["role"],
            "launch_label": panel.QUARTERS.loc[cfg["launch_quarter_index"], "label"],
            "n_triers": summary["n_triers"],
            "trial_reach": trial_reach,
            "n_mature": summary["n_mature"],
            "repeat_rate": repeat_rate,
            "verdict": verdict,
        })
    return pd.DataFrame(rows)
