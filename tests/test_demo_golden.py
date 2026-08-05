"""Demo golden + engine-fidelity lock — Trial vs Repeat.

The strongest lock available: the client-mode ``compute_trial_repeat`` must
reproduce the tested engine's ``repeat_summary`` on the real seeded demo panel —
same maturity cutoff, same repeaters, same rate. This pins BOTH the demo repeat
number and the client-mode fidelity, so neither can drift without the other.

Plus a hand-computed fixture that exercises the right-censoring boundary (a repeat
one day outside the window does NOT count).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

pytest.importorskip("lailara_engagement")

from client_mode import compute_trial_repeat  # noqa: E402


def test_client_compute_matches_engine_on_demo_panel():
    from trial_repeat import AS_OF, repeat_summary  # app engine
    import cinderhaven_household_panel as panel

    eng = repeat_summary(window_weeks=12)
    tx = panel.get_transactions().rename(columns={"date": "purchase_date"})
    mine = compute_trial_repeat(tx, 12, AS_OF)
    assert mine["n_mature"] == eng["n_mature"] == 4456
    assert mine["n_repeaters"] == eng["n_repeaters"] == 2188
    assert round(mine["repeat_rate"], 4) == round(eng["repeat_rate"], 4) == 0.491


def test_maturity_boundary_fixture():
    # as_of 2026-01-31, window 12w (84 days) -> maturity cutoff 2025-11-08.
    as_of = pd.Timestamp("2026-01-31")
    tx = pd.DataFrame([
        ("H1", "2025-06-01"), ("H1", "2025-07-01"),   # repeat in window -> repeater
        ("H2", "2025-06-15"),                          # no repeat -> non-repeater
        ("H3", "2025-08-01"), ("H3", "2025-09-01"),   # repeat in window -> repeater
        ("H4", "2026-01-15"),                          # immature (first purchase after cutoff)
        ("H5", "2025-07-01"), ("H5", "2025-12-01"),   # repeat OUTSIDE the 84-day window -> non-repeater
    ], columns=["household_id", "purchase_date"])
    tx["purchase_date"] = pd.to_datetime(tx["purchase_date"])
    r = compute_trial_repeat(tx, 12, as_of)
    assert r["n_triers"] == 5
    assert r["n_mature"] == 4          # H1,H2,H3,H5 mature; H4 immature
    assert r["n_immature"] == 1
    assert r["n_repeaters"] == 2       # H1,H3 (H5's repeat is out of window)
    assert r["repeat_rate"] == 0.5
    assert r["maturity_cutoff_date"] == "2025-11-08"
