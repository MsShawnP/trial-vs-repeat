"""Locked constants for the Cinderhaven household panel.

The canonical universe (SKUs, product lines, retailers, regions) is reused from
``cinderhaven-store-universe`` — the series SSOT — so this panel never drifts from
the rest of the Cinderhaven tools. Panel-specific figures below are locked and
versioned; changing them is a change-protocol event (see DECISIONS.md).
"""

try:
    from cinderhaven_store_universe.constants import (
        ALL_SKUS,
        DEMO_AS_OF_DATE,
        PRODUCT_LINES,
        REGIONS,
        RETAILERS,
    )
except ImportError as exc:  # pragma: no cover - environment setup guard
    raise ImportError(
        "cinderhaven-household-panel requires the peer package "
        "cinderhaven-store-universe (the canonical universe SSOT). Install it "
        "editable first, e.g. `pip install -e "
        "<doormath>/packages/cinderhaven-store-universe`."
    ) from exc

# --- Locked generation seed --------------------------------------------------
# Generation is deterministic given this value. Matches the house seed.
SEED = 42

# --- Panel data version ------------------------------------------------------
# Bump when the generated panel changes in a way that would shift downstream
# figures. Finalized in Slice 1 / step B.
PANEL_VERSION = "0.1.0"

# --- Panel size (locked, confirmed with Shawn 2026-07-06) --------------------
N_HOUSEHOLDS = 5_000

# --- Timeline: 4 burn-in quarters + 8 analysis quarters = 12 quarters --------
BURN_IN_QUARTERS = 4
ANALYSIS_QUARTERS = 8
TOTAL_QUARTERS = BURN_IN_QUARTERS + ANALYSIS_QUARTERS

# Calendar anchor. The 8-quarter analysis window aligns to the store-universe POS
# window (2024-2025, as-of 2025-12-29); the 4 burn-in quarters therefore cover
# 2023, giving tool #4's trial/repeat logic history runway before the window.
PANEL_START_YEAR = 2023

__all__ = [
    "ALL_SKUS",
    "DEMO_AS_OF_DATE",
    "PRODUCT_LINES",
    "REGIONS",
    "RETAILERS",
    "SEED",
    "PANEL_VERSION",
    "N_HOUSEHOLDS",
    "BURN_IN_QUARTERS",
    "ANALYSIS_QUARTERS",
    "TOTAL_QUARTERS",
    "PANEL_START_YEAR",
]
