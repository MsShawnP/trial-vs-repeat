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

# Repeat window is a first-class parameter (the right-censoring credibility piece):
# a trier only counts as "had a chance to repeat" once this many weeks have elapsed
# since their first purchase. Category-dependent; exposed in the filter bar.
#
# Default is 52 weeks, NOT the brainstorm's 8/12: the shared panel models repeat
# spread across quarters (~0.5/quarter), so an 8/12-week window shows near-zero
# repeat for both launch items and the "15% doomed vs 45%+ winner" story only
# emerges at ~52 weeks (matching #3's canonical 16%/55%). These categories (pantry
# staples, snack bites) repeat on a quarterly cycle, so a 12-month window is the
# honest read. Measured, not assumed — see the probe in HANDOFF.md / Slice 1.
REPEAT_WINDOW_OPTIONS = [8, 12, 26, 52]
DEFAULT_REPEAT_WINDOW_WEEKS = 52

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


SCOPE_BRAND = "__brand__"


def scope_options() -> list[dict[str, str]]:
    """Analysis-scope options: the whole brand, or one of the two launch items."""
    options = [{"label": "Whole brand", "value": SCOPE_BRAND}]
    for sku, cfg in panel.LAUNCH_ITEMS.items():
        line_code = sku.split("-")[1]
        line_name = panel.PRODUCT_LINES[line_code]["name"]
        options.append({"label": f"{line_name} launch ({cfg['role']})", "value": sku})
    return options


def scope_sku(scope: str | None) -> str | None:
    """Map a scope value to a sku filter (None = whole brand)."""
    return None if scope in (None, SCOPE_BRAND, "") else scope


def _normalize(value: str | None) -> str | None:
    """Map the sentinel '__all__' (and empty) to None for the panel accessors."""
    return None if value in (None, "__all__", "") else value


# ── Thin pass-throughs to the shared panel ───────────────────────────
def get_flow(product_line: str | None = None, retailer_id: str | None = None,
             sku: str | None = None) -> pd.DataFrame:
    """New/retained/lapsed/net buyer flow for a filter combination — the leaky bucket.

    Scope-aware: whole brand (sku=None) or one launch item. Each adjacent quarter
    pair's prior/current buyers, with retained/new/lapsed/net. Identities hold every
    row (prior = retained + lapsed; current = retained + new).
    """
    return trial_repeat.buyer_flow(_normalize(product_line), _normalize(retailer_id), sku)


# ── Trial/repeat/cohort accessors (compute in app.trial_repeat) ──────
# Views import these from the seam, not the math module, so the "no DB, in-process"
# contract and the filter vocabulary stay in one place.
from app import trial_repeat  # noqa: E402  (imported here to keep the seam the single import)


def trial_curve(product_line: str | None = None, retailer_id: str | None = None,
                sku: str | None = None) -> pd.DataFrame:
    """Cumulative first-ever-buyer curve by quarter for a filter combination."""
    return trial_repeat.trial_curve(_normalize(product_line), _normalize(retailer_id), sku)


def repeat_summary(window_weeks: int, product_line: str | None = None,
                   retailer_id: str | None = None, sku: str | None = None) -> dict:
    """Maturity-cutoff repeat rate within ``window_weeks`` for a filter combination."""
    return trial_repeat.repeat_summary(window_weeks, _normalize(product_line),
                                       _normalize(retailer_id), sku)


def cohort_retention(product_line: str | None = None, retailer_id: str | None = None,
                     sku: str | None = None) -> pd.DataFrame:
    """Cohort-by-first-purchase-quarter retention triangle for a filter combination."""
    return trial_repeat.cohort_retention(_normalize(product_line), _normalize(retailer_id), sku)


def depth_of_repeat(window_weeks: int, product_line: str | None = None,
                    retailer_id: str | None = None, sku: str | None = None) -> dict:
    """1x / 2x / 3x+ depth distribution among mature triers for a filter combination."""
    return trial_repeat.depth_of_repeat(window_weeks, _normalize(product_line),
                                        _normalize(retailer_id), sku)


def item_verdict(window_weeks: int, threshold: float, product_line: str | None = None,
                 retailer_id: str | None = None) -> pd.DataFrame:
    """Per-launch-item trial reach, repeat rate, and promotion/brand verdict."""
    return trial_repeat.item_verdict(window_weeks, threshold, _normalize(product_line),
                                     _normalize(retailer_id))
