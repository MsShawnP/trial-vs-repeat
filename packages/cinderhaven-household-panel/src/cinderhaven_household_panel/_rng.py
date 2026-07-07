"""Deterministic, independent random streams for panel generation.

Every generator draws from its own named stream so that adding or reordering one
generator never perturbs another's draws. All streams derive from the locked
``SEED``, so the whole panel is reproducible.
"""

import hashlib

import numpy as np

from .constants import SEED


def _stable_hash(name: str) -> int:
    """Deterministic 64-bit hash of a stream name (Python's hash() is salted)."""
    return int.from_bytes(hashlib.sha256(name.encode("utf-8")).digest()[:8], "big")


def child_rng(stream: str) -> np.random.Generator:
    """Return an independent, reproducible Generator for a named stream."""
    seed_seq = np.random.SeedSequence([SEED, _stable_hash(stream)])
    return np.random.default_rng(seed_seq)
