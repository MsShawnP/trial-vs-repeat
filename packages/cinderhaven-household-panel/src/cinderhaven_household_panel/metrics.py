"""Period metrics and buyer flow, computed from the panel (A5).

These are pure read-side accessors — they compute penetration, the three levers
(buying households x frequency x spend-per-trip), and new/retained/lapsed buyer flow
from the transactions. Nothing here is seeded; it is exactly what Decompose's app and
tool #4 will consume. Optional product-line / retailer filters power the app slices.

Penetration denominator is always the full panel (``N_HOUSEHOLDS``): a period's
penetration is the share of ALL panel households that bought (the filtered set) in
that period. The product identity buying_households x frequency x spend_per_trip =
sales holds exactly regardless of filter.
"""

import pandas as pd

from .constants import N_HOUSEHOLDS
from .transactions import get_transactions


def _filtered(product_line=None, retailer_id=None) -> pd.DataFrame:
    tx = get_transactions()
    if product_line is not None:
        tx = tx[tx["product_line"] == product_line]
    if retailer_id is not None:
        tx = tx[tx["retailer_id"] == retailer_id]
    return tx


def get_period_metrics(product_line=None, retailer_id=None) -> pd.DataFrame:
    """Per-quarter metrics: penetration, the three levers, and their sub-splits.

    Columns: quarter_index, quarter_label, is_analysis, buying_households,
    penetration, trips, frequency, units, sales, spend_per_trip, units_per_trip,
    price_per_unit. One row per quarter (0-11), in calendar order.
    """
    from .calendar import get_quarters

    tx = _filtered(product_line, retailer_id)
    quarters = get_quarters()[["quarter_index", "label", "is_analysis"]]

    grp = tx.groupby("quarter_index")
    agg = pd.DataFrame(
        {
            "buying_households": grp["household_id"].nunique(),
            "trips": grp.size(),
            "units": grp["units"].sum(),
            "sales": grp["spend"].sum(),
        }
    )
    m = quarters.merge(agg, left_on="quarter_index", right_index=True, how="left")
    # Quarters with no matching rows (e.g. a launch item pre-launch) → zeros.
    for col in ("buying_households", "trips", "units", "sales"):
        m[col] = m[col].fillna(0)

    m["penetration"] = m["buying_households"] / N_HOUSEHOLDS
    m["frequency"] = _safe_div(m["trips"], m["buying_households"])
    m["spend_per_trip"] = _safe_div(m["sales"], m["trips"])
    m["units_per_trip"] = _safe_div(m["units"], m["trips"])
    m["price_per_unit"] = _safe_div(m["sales"], m["units"])

    return m.rename(columns={"label": "quarter_label"}).reset_index(drop=True)


def get_buyer_flow(product_line=None, retailer_id=None) -> pd.DataFrame:
    """New / retained / lapsed buyer flow for each adjacent quarter pair.

    Columns: from_index, from_label, to_label, prior_buyers, current_buyers,
    retained, new, lapsed. Identities hold every row:
    prior_buyers = retained + lapsed; current_buyers = retained + new.
    """
    from .calendar import get_quarters

    tx = _filtered(product_line, retailer_id)
    quarters = get_quarters()[["quarter_index", "label"]].sort_values("quarter_index")

    buyers_by_q = {
        qi: set(g["household_id"].unique())
        for qi, g in tx.groupby("quarter_index")
    }
    labels = dict(zip(quarters["quarter_index"], quarters["label"]))
    indices = quarters["quarter_index"].tolist()

    rows = []
    for prev, curr in zip(indices[:-1], indices[1:]):
        prior = buyers_by_q.get(prev, set())
        current = buyers_by_q.get(curr, set())
        retained = len(prior & current)
        rows.append(
            {
                "from_index": prev,
                "from_label": labels[prev],
                "to_label": labels[curr],
                "prior_buyers": len(prior),
                "current_buyers": len(current),
                "retained": retained,
                "new": len(current - prior),
                "lapsed": len(prior - current),
            }
        )
    return pd.DataFrame(rows)


def _safe_div(numer, denom):
    return (numer / denom.where(denom != 0)).fillna(0.0)
