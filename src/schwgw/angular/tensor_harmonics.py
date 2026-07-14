"""Tensor-harmonic label registry for normalization and gauge checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Parity = Literal["even", "odd"]


@dataclass(frozen=True)
class TensorHarmonicInfo:
    label: str
    parity: Parity
    rw_gauge_radiative: bool


_REGISTRY: dict[str, TensorHarmonicInfo] = {
    "tt": TensorHarmonicInfo("tt", "even", True),
    "Rt": TensorHarmonicInfo("Rt", "even", True),
    "L0": TensorHarmonicInfo("L0", "even", True),
    "T0": TensorHarmonicInfo("T0", "even", True),
    "Et": TensorHarmonicInfo("Et", "even", False),
    "E1": TensorHarmonicInfo("E1", "even", False),
    "Bt": TensorHarmonicInfo("Bt", "odd", True),
    "B1": TensorHarmonicInfo("B1", "odd", True),
    "E2": TensorHarmonicInfo("E2", "even", False),
    "B2": TensorHarmonicInfo("B2", "odd", False),
}


def _info(label: str) -> TensorHarmonicInfo:
    try:
        return _REGISTRY[label]
    except KeyError as exc:
        raise ValueError(f"unknown tensor-harmonic label: {label}") from exc


def tensor_harmonic_labels() -> tuple[str, ...]:
    """Return frozen target-paper tensor-harmonic labels."""

    return tuple(_REGISTRY)


def tensor_harmonic_parity(label: str) -> Parity:
    """Return the frozen parity split for a tensor-harmonic label."""

    return _info(label).parity


def is_rw_gauge_radiative_label(label: str) -> bool:
    """Return whether ``label`` survives RW gauge for radiative ``ell >= 2``."""

    return _info(label).rw_gauge_radiative


def rw_gauge_radiative_labels(parity: Parity | None = None) -> tuple[str, ...]:
    """Return labels retained in RW gauge for radiative modes."""

    if parity is not None and parity not in ("even", "odd"):
        raise ValueError("parity must be 'even', 'odd', or None")
    return tuple(
        label
        for label, info in _REGISTRY.items()
        if info.rw_gauge_radiative and (parity is None or info.parity == parity)
    )
