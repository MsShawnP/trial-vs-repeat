"""Household dimension for the panel (A2).

Each household carries three latent attributes that drive later generation:

- ``base_propensity`` — gamma-distributed overall buying rate. Its heavy right
  skew (shape < 1) is what makes trip counts negative-binomial / overdispersed in
  A4, i.e. a few heavy buyers and a long one-and-done tail, like real panel data.
- ``price_sensitivity`` — how much a household pulls back when prices rise; the
  mechanism behind the "growth that's actually erosion" window.
- ``innovator_affinity`` — propensity to try new-launch items; drives the trial
  spike for the two launch stories tool #4 reuses.

Nothing here sets an outcome — only latent tendencies. The observed rates are
computed from transactions downstream.
"""

import numpy as np
import pandas as pd

from ._rng import child_rng
from .constants import N_HOUSEHOLDS, REGIONS

# Region population weights (roughly US CPG household distribution). Keyed to the
# canonical REGIONS so it can never drift from the SSOT.
_REGION_WEIGHTS = {
    "Northeast": 0.22,
    "Southeast": 0.28,
    "Midwest": 0.24,
    "West": 0.26,
}
assert set(_REGION_WEIGHTS) == set(REGIONS), "region weights must cover canonical REGIONS"

# Latent purchase-propensity: gamma with heavy right skew, mean 1.0.
_PROPENSITY_SHAPE = 0.7  # k < 1 → strong right skew, long heavy-buyer tail
_PROPENSITY_MEAN = 1.0


def get_households() -> pd.DataFrame:
    """Return the locked 5,000-household dimension (deterministic given SEED)."""
    rng = child_rng("households")
    n = N_HOUSEHOLDS

    regions = list(REGIONS)
    weights = np.array([_REGION_WEIGHTS[r] for r in regions], dtype=float)
    weights /= weights.sum()
    region = rng.choice(regions, size=n, p=weights)

    scale = _PROPENSITY_MEAN / _PROPENSITY_SHAPE
    base_propensity = rng.gamma(shape=_PROPENSITY_SHAPE, scale=scale, size=n)

    price_sensitivity = rng.beta(2.0, 3.0, size=n)   # mean 0.40
    innovator_affinity = rng.beta(2.0, 5.0, size=n)  # mean ~0.29 — few true innovators

    household_id = [f"HH-{i:05d}" for i in range(1, n + 1)]

    return pd.DataFrame(
        {
            "household_id": household_id,
            "region": region,
            "base_propensity": base_propensity,
            "price_sensitivity": price_sensitivity,
            "innovator_affinity": innovator_affinity,
        }
    )
