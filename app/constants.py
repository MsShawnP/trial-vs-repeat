"""Lailara design-system tokens and format helpers for Plotly/Dash charts.

Cloned from Decompose's constants (colour values come from the lailara-palette
package — the single source of truth — re-exported under short semantic aliases).
The trial/repeat vocabulary (verdict, flow, depth colours) lives at the bottom.
"""

import math

from lailara_palette import (
    LL_CANVAS,
    LL_CHICAGO,
    LL_GRIDLINE,
    LL_HK,
    LL_INK,
    LL_REFERENCE,
    LL_SANS,
    LL_SERIF,
    LL_TEXT_SEC,
    LL_TOKYO,
)

# ── Canvas & London greyscale ──
CANVAS = LL_CANVAS
TEXT_SECONDARY = LL_TEXT_SEC
GRIDLINE = LL_GRIDLINE
REFERENCE = LL_REFERENCE
INK = LL_INK

# ── Accent hues (default shades) ──
CHICAGO_20 = LL_CHICAGO   # navy
HK_35 = LL_HK             # teal
HK_85 = "#b5e4d8"         # Hong Kong-85 — lightest usable data stop (DS: step 95 is
                          # surface-only). Not exported as a named lailara-palette const.
TOKYO_40 = LL_TOKYO       # berry

# ── Typography (for Plotly) ──
FONT_SERIF = f"{LL_SERIF}, Georgia, Times New Roman, serif"
FONT_SANS = f"{LL_SANS}, Source Sans Pro, Helvetica Neue, Helvetica, Arial, sans-serif"

# ── Trial/repeat vocabulary (Leaky Bucket's core semantics) ──────────
# The verdict axis: a "brand" repeats (sticky, good); a "promotion" is trial-heavy
# and repeat-light (leaky, the discontinuation risk).
VERDICT_BRAND = HK_35        # teal — repeat is healthy: real adoption
VERDICT_PROMOTION = TOKYO_40  # berry — trial-heavy / repeat-light: expensive sampling
VERDICT_NO_DATA = REFERENCE  # muted grey — item excluded by the filter / no mature triers

# Leaky-bucket flow semantics (buyers moving in and out of the bucket per period).
FLOW_NEW = HK_35        # teal — buyers flowing IN (new this period)
FLOW_RETAINED = CHICAGO_20   # navy — buyers who stayed
FLOW_LAPSED = TOKYO_40  # berry — buyers flowing OUT (lapsed)
FLOW_NET = INK          # ink — the net line

# Depth-of-repeat shades (1x / 2x / 3x+), light → dark as loyalty deepens.
DEPTH_COLORS = {"1x": REFERENCE, "2x": HK_35, "3x+": CHICAGO_20}

# Trial curve colour.
TRIAL_COLOR = CHICAGO_20   # navy — cumulative first-ever buyers

# The verdict threshold used for the "promotion or brand?" flag. A category-dependent
# copy/product decision; stated in-app and revisited in the Slice 3 copy pass.
BRAND_REPEAT_THRESHOLD = 0.30   # >= 30% mature repeat reads as a brand, not a promotion


# ── Format helpers ──
def _is_missing(value):
    return value is None or (isinstance(value, float) and math.isnan(value))


def fmt_pct(value, decimals=1):
    """Format a decimal (0.123) as a percentage string ('12.3%')."""
    if _is_missing(value):
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def fmt_number(value):
    """Format a count with thousands separators."""
    if _is_missing(value):
        return "N/A"
    return f"{value:,.0f}"
