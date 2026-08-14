"""Phase diagnostics that keep raw, unwrapped and offset-removed surfaces."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PhaseComparisonDiagnostics:
    computed_raw: np.ndarray
    reference_raw: np.ndarray
    computed_unwrapped: np.ndarray
    reference_unwrapped: np.ndarray
    wrapped_residual: np.ndarray
    unwrapped_residual: np.ndarray
    global_offset: float
    global_offset_removed_residual: np.ndarray
    panel_offsets: np.ndarray
    panel_offset_removed_residual: np.ndarray
    raw_mae: float
    global_offset_removed_mae: float
    panel_raw_mae: np.ndarray
    panel_offset_removed_mae: np.ndarray


def compare_complex_phase(
    computed: np.ndarray,
    reference: np.ndarray,
    *,
    frequency_axis: int = -1,
) -> PhaseComparisonDiagnostics:
    """Compare complex phases without silently fitting away discrepancies.

    ``global_offset`` is one circular constant over the complete dataset.
    ``panel_offsets`` are separately reported constants along the frequency
    axis.  Raw residuals remain the primary evidence; offset-removed values
    are diagnostics of a possible convention mismatch, not corrected data.
    """

    left = np.asarray(computed, dtype=np.complex128)
    right = np.asarray(reference, dtype=np.complex128)
    if left.shape != right.shape or left.size == 0:
        raise ValueError("computed and reference must have the same non-empty shape")
    if not np.all(np.isfinite(left)) or not np.all(np.isfinite(right)):
        raise ValueError("phase inputs must be finite")
    if not isinstance(frequency_axis, int) or isinstance(frequency_axis, bool):
        raise TypeError("frequency_axis must be an integer")
    axis = frequency_axis + left.ndim if frequency_axis < 0 else frequency_axis
    if not 0 <= axis < left.ndim:
        raise ValueError("frequency_axis is outside the input dimensions")
    computed_raw = np.angle(left)
    reference_raw = np.angle(right)
    computed_unwrapped = np.unwrap(computed_raw, axis=axis)
    reference_unwrapped = np.unwrap(reference_raw, axis=axis)
    wrapped = _wrap(computed_raw - reference_raw)
    unwrapped = computed_unwrapped - reference_unwrapped
    global_offset = float(np.angle(np.mean(np.exp(1.0j * wrapped))))
    global_removed = _wrap(wrapped - global_offset)
    panel_offsets = np.angle(np.mean(np.exp(1.0j * wrapped), axis=axis))
    expanded_offsets = np.expand_dims(panel_offsets, axis=axis)
    panel_removed = _wrap(wrapped - expanded_offsets)
    panel_raw_mae = np.mean(np.abs(wrapped), axis=axis)
    panel_removed_mae = np.mean(np.abs(panel_removed), axis=axis)
    return PhaseComparisonDiagnostics(
        computed_raw=computed_raw,
        reference_raw=reference_raw,
        computed_unwrapped=computed_unwrapped,
        reference_unwrapped=reference_unwrapped,
        wrapped_residual=wrapped,
        unwrapped_residual=unwrapped,
        global_offset=global_offset,
        global_offset_removed_residual=global_removed,
        panel_offsets=panel_offsets,
        panel_offset_removed_residual=panel_removed,
        raw_mae=float(np.mean(np.abs(wrapped))),
        global_offset_removed_mae=float(np.mean(np.abs(global_removed))),
        panel_raw_mae=panel_raw_mae,
        panel_offset_removed_mae=panel_removed_mae,
    )


def _wrap(values: np.ndarray) -> np.ndarray:
    return np.angle(np.exp(1.0j * values))


__all__ = ["PhaseComparisonDiagnostics", "compare_complex_phase"]
