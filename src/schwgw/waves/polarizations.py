"""Polarization-basis conversions for incident plane gravitational waves."""

from __future__ import annotations

import math
from typing import Any


def _as_complex_scalar(value: Any, name: str) -> complex:
    try:
        return complex(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be convertible to a complex scalar") from exc


def linear_to_circular(A_plus: Any, A_cross: Any) -> tuple[complex, complex]:
    """Convert linear ``(+/cross)`` amplitudes to ``(A_L, A_R)``."""

    plus = _as_complex_scalar(A_plus, "A_plus")
    cross = _as_complex_scalar(A_cross, "A_cross")
    scale = math.sqrt(2.0)
    return (plus + 1j * cross) / scale, (plus - 1j * cross) / scale


def circular_to_linear(A_L: Any, A_R: Any) -> tuple[complex, complex]:
    """Convert circular ``(A_L, A_R)`` amplitudes to ``(+/cross)``."""

    left = _as_complex_scalar(A_L, "A_L")
    right = _as_complex_scalar(A_R, "A_R")
    scale = math.sqrt(2.0)
    return (left + right) / scale, -1j * (left - right) / scale
