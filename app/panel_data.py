"""In-process panel data layer — the app's single data seam.

Leaky Bucket has **no database**. Its data is the deterministic, seed-locked
``cinderhaven-household-panel`` package (built by tool #3, vendored under
packages/): the app imports it, warms the panel once at startup, and serves every
metric from the package's in-process cache. The layout, filters, and views import
from *here*, not from the package directly, so the "no DB, in-process" contract and
the filter vocabulary live in one place.

Trial/repeat/cohort math (the analysis tool #4 adds on top of the shared panel) lives
in ``app.trial_repeat`` and is surfaced through the accessors near the bottom.
"""

import logging
import time

import cinderhaven_household_panel as panel
import pandas as pd

logger = logging.getLogger(__name__)

# ── Re-exported panel facts (so views never reach into the package) ──
PANEL_VERSION = panel.PANEL_VERSION
AS_OF_DATE = panel.DEMO_AS_OF_DATE
N_HOUSEHOLDS = panel.N_HOUSEHOLDS
ANALYSIS_QUARTERS = list(panel.ANALYSIS_QUARTER_LABELS)
BURN_IN_QUARTERS = list(panel.BURN_IN_QUARTER_LABELS)
ALL_QUARTERS = BURN_IN_QUARTERS + ANALYSIS_QUARTERS

# Repeat window is a first-class parameter (the right-censoring credibility piece):
# a trier only counts as "had a chance to repeat" once this many weeks have elapsed
# since their first purchase. Category-dependent; exposed in the filter bar.
REPEAT_WINDOW_OPTIONS = [8, 12]
DEFAULT_REPEAT_WINDOW_WEEKS = 12

_warmed = False


def warm_cache() -> None:
    """Build the panel once, at startup, so no visitor's request pays generation.

    Idempotent. Every downstream accessor reads through the same cached transactions.
    """
    global _warmed
    if _warmed:
        return
    start = time.perf_counter()
    panel.get_transactions()
    _warmed = True
    logger.info(
        "panel warmed in %.2fs (v%s, %d households, %d analysis quarters)",
        time.perf_counter() - start,
        PANEL_VERSION,
        N_HOUSEHOLDS,
        len(ANALYSIS_QUARTERS),
    )


# ── Filter vocabulary ────────────────────────────────────────────────
def product_line_options() -> list[dict[str, str]]:
    """Dropdown options for the product-line filter, with an 'All lines' default."""
    options = [{"label": "All lines", "value": "__all__"}]
    for code, meta in panel.PRODUCT_LINES.items():
        options.append({"label": meta["name"], "value": code})
    return options


def retailer_options() -> list[dict[str, str]]:
    """Dropdown options for the retailer filter, with an 'All retailers' default."""
    options = [{"label": "All retailers", "value": "__all__"}]
    for retailer_id, meta in panel.RETAILERS.items():
        options.append({"label": meta["name"], "value": retailer_id})
    return options


def _normalize(value: str | None) -> str | None:
    """Map the sentinel '__all__' (and empty) to None for the panel accessors."""
    return None if value in (None, "__all__", "") else value


# ── Thin pass-throughs to the shared panel ───────────────────────────
def get_metrics(product_line: str | None = None, retailer_id: str | None = None) -> pd.DataFrame:
    """Per-quarter metrics for a filter combination (thin pass-through)."""
    return panel.get_period_metrics(_normalize(product_line), _normalize(retailer_id))


def get_flow(product_line: str | None = None, retailer_id: str | None = None) -> pd.DataFrame:
    """New/retained/lapsed buyer flow for a filter combination — the leaky-bucket flow.

    Thin pass-through to the panel's ``get_buyer_flow``: each adjacent quarter pair's
    prior/current buyers, with retained/new/lapsed. Identities hold every row
    (prior = retained + lapsed; current = retained + new).
    """
    return panel.get_buyer_flow(_normalize(product_line), _normalize(retailer_id))


def launch_items() -> pd.DataFrame:
    """The two seeded launch items (#4's demo): the leaky one and the sticky one."""
    return panel.get_launch_items()
