"""The panel's 12-quarter calendar (4 burn-in + 8 analysis).

Quarters are standard calendar quarters. The frame is deterministic and the
single source of truth for period boundaries used by every downstream generator
and metric.
"""

import pandas as pd

from .constants import (
    BURN_IN_QUARTERS,
    PANEL_START_YEAR,
    TOTAL_QUARTERS,
)

_QUARTER_MONTHS = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}


def build_quarters() -> pd.DataFrame:
    """Build the locked 12-quarter calendar as a DataFrame.

    Columns: quarter_index (0-11), label ("YYYY-Qn"), year, quarter (1-4),
    phase ("burn_in"/"analysis"), is_analysis (bool), start_date, end_date.
    """
    rows = []
    for i in range(TOTAL_QUARTERS):
        year = PANEL_START_YEAR + i // 4
        quarter = i % 4 + 1
        start_month, end_month = _QUARTER_MONTHS[quarter]
        start = pd.Timestamp(year=year, month=start_month, day=1)
        end = pd.Timestamp(year=year, month=end_month, day=1) + pd.offsets.MonthEnd(1)
        rows.append(
            {
                "quarter_index": i,
                "label": f"{year}-Q{quarter}",
                "year": year,
                "quarter": quarter,
                "phase": "burn_in" if i < BURN_IN_QUARTERS else "analysis",
                "is_analysis": i >= BURN_IN_QUARTERS,
                "start_date": start,
                "end_date": end,
            }
        )
    return pd.DataFrame(rows)


QUARTERS = build_quarters()

ANALYSIS_QUARTER_LABELS = QUARTERS.loc[QUARTERS["is_analysis"], "label"].tolist()
BURN_IN_QUARTER_LABELS = QUARTERS.loc[~QUARTERS["is_analysis"], "label"].tolist()


def get_quarters() -> pd.DataFrame:
    """Return a copy of the locked 12-quarter calendar."""
    return QUARTERS.copy()
