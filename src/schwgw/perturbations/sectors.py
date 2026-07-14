from __future__ import annotations

from enum import Enum


class Sector(str, Enum):
    """Radiative Schwarzschild perturbation parity sectors."""

    ODD = "odd"
    EVEN = "even"
